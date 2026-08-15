---
name: telegram-bot-windows-service
category: software-development
description: Deploy Telegram bot as Windows service with zombie-killer.
trigger: Use when deploying a Telegram bot as a Windows service that must survive restarts, handle multiple languages, parse free-text commands, and self-heal from zombie processes.
---

# Telegram Bot Windows Service Deployment

## Scope
End-to-end deployment of autonomous AI Telegram bots on Windows:
- Long-poll bot with async-safe Telegram calls (timeout, per-update isolation)
- Self-zombie-killer: eliminates stale python.exe processes on same token
- Multilingual free-text command parsing (RU/EN/ES)
- Persistent settings with language-switch protection
- Windows service via NSSM (auto-start, logs, restart on crash)
- One-command installer script (PowerShell)

## Critical Patterns

### 1. Zombie Process Self-Killer
**Problem**: MSYS `kill` only terminates bash wrapper; python.exe survives and keeps long-polling → two bots on one token → commands answered with stale memory.

**Solution**: At `__main__` entry, kill all other `python.exe` running the same script:
```python
def kill_other_instances():
    import psutil, subprocess
    mypid = psutil.Process().pid  # REAL python.exe PID, not bash wrapper
    ps_script = f"""$mypid = {mypid}
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object {{ $_.CommandLine -match 'mybot' -and $_.ProcessId -ne $mypid }} |
    ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}
    """
    with open("kill_zombies.ps1", "w", encoding="utf-8") as f:
        f.write(ps_script)
    subprocess.run(["powershell", "-NoProfile", "-File", "kill_zombies.ps1"],
                   capture_output=True, text=True, timeout=20, encoding="utf-8", errors="ignore")
```
**Pitfall**: Use `psutil.Process().pid`, NOT `os.getpid()` (returns bash PID in MSYS). Write PS script to file — MSYS mangles inline `$_` and quotes.

### 2. Language Switch Must Not Overwrite Target
**Bug**: `set_lang()` called `save_settings()` which wrote current in-memory `TARGET_DESC` to disk. If a zombie answered the `/setlocal` callback, its stale target ("human") overwrote the real target ("red car").

**Fix**: `save_settings(persist_target=False)` on language switch — reads previous target from disk and preserves it:
```python
def save_settings(persist_target=True):
    data = {"target": TARGET_DESC, "lang": LANG, ...}
    if not persist_target:
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                prev = json.load(f)
            pt = prev.get("target")
            if isinstance(pt, str) and pt.strip():
                data["target"] = pt
        except Exception:
            pass
    # write data...
```
Call: `save_settings(persist_target=False)` ONLY from `set_lang()`. All other callers (`/target`, `/zone`, `/autoguard`) use default `True`.

### 3. Async Menu Updates (Never Block Poll Loop)
**Problem**: `setMyCommands` + `deleteMyCommands` ×3 = 5 sequential HTTP calls × 15s timeout = 75s poll freeze.

**Fix**: Background thread + reduced timeout:
```python
def set_bot_menu_async():
    threading.Thread(target=set_bot_menu, daemon=True).start()

def set_bot_menu():
    for lc in ("ru", "es", "en"):
        try: tg("deleteMyCommands", data={"language_code": lc})
        except: pass
    try: tg("setMyCommands", data={"commands": _commands_payload(LANG)})
    except: pass
    # timeout=8 in tg() helper
```

### 4. Per-Update Isolation
Wrap each update handler so one network error doesn't lose other commands:
```python
for upd in j["result"]:
    try:
        _handle_update(upd)
    except Exception as e:
        print(f"  update err: {e}", flush=True)
```

### 5. Multilingual Free-Text Target Parsing
Single parser handles RU/EN/ES for colors + classes:
```python
COLOR_MAP = {
    "red": [((0,100,80),(10,255,255)), ((170,100,80),(180,255,255))],
    "yellow": [((15,60,80),(40,255,255))],
    # ... 11 colors, red = dual HSV range
}
CLASS_MAP = {
    2: ["car", "cars", "coche", "carros", "автомобиль", "машина", ...],
    0: ["person", "persona", "человек", ...],
    5: ["bus", "autobus", "автобус", ...],
    7: ["truck", "camion", "грузовик", ...],
}
```
`parse_target("red car")` → `classes={2}, ranges=red dual HSV`. Unrecognized words → filter unchanged + localized "Couldn't recognize" message.

### 6. PowerShell stderr Encoding Fix
Windows RU locale → PowerShell stderr in cp866, not utf-8:
```python
subprocess.run(..., encoding="utf-8", errors="ignore")
```

### 7. Telegram Timeout Reduction
Default 15s → 8s for all `tg()` calls. Combined with async menu, poll loop never freezes.

### 8. NSSM Service Installation
```powershell
nssm install SuperGuardAlarm "C:\SuperGuard\venv\Scripts\python.exe" "C:\SuperGuard\panic_mode.py"
nssm set SuperGuardAlarm AppDirectory "C:\SuperGuard"
nssm set SuperGuardAlarm Start SERVICE_AUTO_START
nssm set SuperGuardAlarm AppStdout "C:\SuperGuard\superguard.log"
```

## File Structure (Deployed)
```
C:\SuperGuard\
├── panic_mode.py          # Single-file bot (~1000 lines)
├── sguard.env             # Secrets (token, chat_id, plug IP/key) — NEVER COMMIT
├── sguard_settings.json   # Auto-generated persistent settings
├── requirements.txt       # opencv-python, ultralytics, tinytuya, requests, psutil, numpy
├── venv/                  # Python 3.12 virtual env
├── superguard.log         # Service stdout
└── superguard_err.log     # Service stderr
```

## Installer Script
See `templates/install_superguard.ps1` — one-command deploy from GitHub:
```powershell
irm https://raw.githubusercontent.com/.../install_superguard.ps1 | iex
```
Prompts for secrets interactively, creates venv, installs deps, writes `sguard.env`, registers NSSM service, adds firewall rules for Tuya plug (port 6668).

## Verification
See `scripts/verify_deployment.py` — runs syntax, i18n, target-parse, import, and critical-function checks.

## References
- `references/zombie-killer-pattern.md` — detailed reproduction & fix
- `references/lang-switch-target-bug.md` — bug analysis & persist_target fix
- `references/multilingual-target-parsing.md` — COLOR_MAP/CLASS_MAP design
- `references/async-menu-poll-loop.md` — timeout & threading pattern

## Support Files
- `templates/install_superguard.ps1` — production installer
- `templates/sguard.env.example` — config template
- `templates/requirements.txt` — pinned dependencies
- `scripts/verify_deployment.py` — ad-hoc verification
- `scripts/test_i18n.py` — i18n test (48 keys × 3 langs)
- `scripts/test_target_parse.py` — target parser test (11 cases)