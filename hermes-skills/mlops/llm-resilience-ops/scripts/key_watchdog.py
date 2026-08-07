#!/usr/bin/env python3
"""Key watchdog: probe all pooled API keys, reset stale statuses, report dead keys.

Silent (no stdout) when everything is healthy and nothing changed -> cron stays quiet.
Reports: dead keys, duplicates, quota keys (only on change), stale-status resets performed.

Run via cron (no_agent) or manually:  python key_watchdog.py

Adapt HOME / MODELS / EXTRA_ENV to your environment.
"""
import concurrent.futures, json, os, re, shutil, ssl, subprocess, urllib.error, urllib.request

HOME = r"C:\Users\tomas\AppData\Local\hermes"  # <- adjust
_script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(_script_dir, "..", "hermes-agent")):
    HOME = os.path.dirname(_script_dir)
STATE_FILE = os.path.join(_script_dir, ".key_watchdog_state.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

MODELS = {
    "nvidia": "nvidia/llama-3.3-nemotron-super-49b-v1",
    "opencode-zen": "deepseek-v4-flash-free",
    "kilocode": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openai-api": "gpt-4o-mini",
    "gemini": "gemini-2.0-flash",
    "groq": "llama-3.3-70b-versatile",
}

EXTRA_ENV = [  # (env var, provider, base_url) - keys not in hermes auth pools
    ("GROQ_API_KEY", "groq", "https://api.groq.com/openai/v1"),
]


def load_env():
    env = {}
    p = os.path.join(HOME, ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8", errors="replace"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_creds():
    """Return list of {provider, label, key, base_url, source}."""
    creds, seen = [], set()
    auth = json.load(open(os.path.join(HOME, "auth.json"), encoding="utf-8"))
    env = load_env()
    for provider, entries in auth.get("credential_pool", {}).items():
        for e in entries:
            label = f"{provider}:{e['label']}"
            if e.get("access_token"):
                creds.append({"provider": provider, "label": label, "key": e["access_token"],
                              "base_url": e.get("base_url"), "source": "manual"})
            elif str(e.get("source", "")).startswith("env:"):
                val = env.get(str(e["source"])[4:]) or os.environ.get(str(e["source"])[4:])
                if val:
                    creds.append({"provider": provider, "label": label, "key": val,
                                  "base_url": e.get("base_url"), "source": "env"})
            seen.add(label)
    for var, prov, base in EXTRA_ENV:
        if var in env and env[var] and f"env:{var}" not in seen:
            creds.append({"provider": prov, "label": f"env:{var}", "key": env[var],
                          "base_url": base, "source": "env"})
    return creds


def probe(c):
    model = MODELS.get(c["provider"])
    if not c["key"] or not c["base_url"] or not model:
        return {**c, "status": "SKIP", "http": None, "detail": "missing key/base/model"}
    for attempt in range(2):  # one retry for transient timeouts
        res = _probe_once(c, model)
        if res["status"] != "ERR" or attempt == 1:
            return res
    return res


def _probe_once(c, model):
    ctx = ssl.create_default_context()
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": "hi"}],
                       "max_tokens": 5}).encode()
    req = urllib.request.Request(c["base_url"].rstrip("/") + "/chat/completions",
                                 data=body, method="POST")
    req.add_header("Authorization", "Bearer " + c["key"])
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            data = r.read().decode("utf-8", "replace")
            cost = ""
            m = re.search(r'"cost"\s*:\s*"?([0-9.]+)"?', data)
            if m:
                cost = f" cost={m.group(1)}"
            return {**c, "status": "OK", "http": 200, "detail": f"HTTP 200{cost}"}
    except urllib.error.HTTPError as e:
        msg = ""
        try:
            msg = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            pass
        low = msg.lower()
        if e.code in (401, 403):
            return {**c, "status": "DEAD", "http": e.code, "detail": f"HTTP {e.code}"}
        if e.code == 429:
            if "insufficient_quota" in low or "quota" in low:
                return {**c, "status": "QUOTA", "http": 429, "detail": "429 quota (valid key, no balance)"}
            return {**c, "status": "RATE", "http": 429, "detail": "429 rate-limited (alive, throttled)"}
        return {**c, "status": f"HTTP{e.code}", "http": e.code, "detail": msg[:120]}
    except Exception as e:
        return {**c, "status": "ERR", "http": None, "detail": f"{type(e).__name__}: {str(e)[:80]}"}


def find_hermes_cli():
    exe = shutil.which("hermes")
    if exe:
        return exe
    for cand in (os.path.join(HOME, "hermes-agent", "venv", "Scripts", "hermes.exe"),
                 os.path.join(HOME, "hermes-agent", "venv", "Scripts", "hermes")):
        if os.path.exists(cand):
            return cand
    return None


def reset_provider(provider):
    cli = find_hermes_cli()
    if not cli:
        return False
    try:
        r = subprocess.run([cli, "auth", "reset", provider], capture_output=True, text=True,
                           timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.returncode == 0
    except Exception:
        return False


def main():
    creds = load_creds()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(probe, creds):
            results.append(r)

    # duplicates by full key value
    by_key = {}
    for r in results:
        by_key.setdefault(r["key"], []).append(r["label"])
    dups = [labels for labels in by_key.values() if len(labels) > 1]

    dead = [r for r in results if r["status"] == "DEAD"]
    quota = sorted(r["label"] for r in results if r["status"] == "QUOTA")
    errs = [r for r in results if r["status"] in ("ERR", "SKIP")]

    # stale statuses: marked exhausted/error in auth.json but probes OK -> reset provider
    auth = json.load(open(os.path.join(HOME, "auth.json"), encoding="utf-8"))
    ok_by_provider = {}
    for r in results:
        ok_by_provider.setdefault(r["provider"], []).append(r["status"] == "OK")
    stale_providers = []
    for provider, entries in auth.get("credential_pool", {}).items():
        if provider not in MODELS:
            continue
        marked = [e for e in entries if e.get("last_status") in ("exhausted", "rate-limited")
                  or e.get("last_error_code") in (401, 403, 429)]
        if marked and all(ok_by_provider.get(provider, [])):
            stale_providers.append(provider)

    resets_done = []
    for p in stale_providers:
        if reset_provider(p):
            resets_done.append(p)

    # change detection vs previous run
    try:
        prev = json.load(open(STATE_FILE, encoding="utf-8"))
    except Exception:
        prev = {}
    quota_changed = sorted(quota) != sorted(prev.get("quota", []))
    json.dump({"dead": sorted(r["label"] for r in dead), "quota": sorted(quota)},
              open(STATE_FILE, "w", encoding="utf-8"))

    # build report - only when something worth saying
    lines = []
    if dead:
        lines.append("🔴 DEAD KEYS (invalid/expired):")
        for r in dead:
            lines.append(f"  • {r['label']} — {r['detail']}")
    if dups:
        lines.append("🟡 DUPLICATES (same key added twice):")
        for labels in dups:
            lines.append(f"  • {' == '.join(labels)}")
    if resets_done:
        lines.append("♻️  Reset stale statuses: " + ", ".join(resets_done))
    if quota and (quota_changed or dead):
        lines.append("🟠 Quota keys (valid, no balance): " + ", ".join(quota))
    if errs:
        lines.append("⚪ Probe errors: " + "; ".join(f"{r['label']} ({r['detail']})" for r in errs))

    if lines:
        print("🔑 Key watchdog\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
