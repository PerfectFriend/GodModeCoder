#!/usr/bin/env python3
"""Voicebox TTS command provider for Hermes (proven 2026-08).

Turns a text file into audio via the local Voicebox server
(http://127.0.0.1:8000) using a preset profile (cloned male voice,
Qwen3-TTS 1.7B). Designed to be wired into Hermes as a command TTS
provider (tts.providers.<name>.type: command), but works standalone:

    python voicebox_tts.py <input_text_path> <output_audio_path>

Hermes supplies {input_path} (temp UTF-8 text) and {output_path} (where
audio must land) via placeholder substitution.

Flow: POST /generate -> poll /generate/{id}/status until "completed"
(status endpoint streams SSE "data: {...}" lines, not raw JSON!) ->
GET /history/{id}/export-audio -> write bytes to output path.

Pitfalls handled:
- /status returns SSE; tolerate both raw JSON and SSE (last data: wins).
- Generate rejects a preset profile unless `engine` is passed explicitly
  and equals the profile's preset_engine.
- Cyrillic text: fine as UTF-8 file input; never inline curl -d.
- Git-bash: call this script with forward-slash Windows paths
  (C:/Users/...), Windows Python cannot open MSYS /c/... paths.

Usage from Hermes config:
  tts:
    provider: voicebox
    providers:
      voicebox:
        type: command
        command: '"<venv>\Scripts\python.exe" "C:\Users\tomas\voicebox_tts.py" {input_path} {output_path}'
        output_format: wav
        voice_compatible: true
"""
import json
import re
import sys
import time
import urllib.request
import urllib.error

VOICEBOX_URL = "http://127.0.0.1:8000"
PROFILE_ID = "e7013ccf-70c7-4f22-a277-e6b3e4ddc4ef"  # Мастер-мужской (Ryan)
ENGINE = "qwen_custom_voice"
MODEL_SIZE = "1.7B"          # 1.7B = full quality; 0.6B = faster on CPU
POLL_INTERVAL = 3.0
TIMEOUT_S = 600


def detect_language(text: str) -> str:
    """Russian if the text has at least as much Cyrillic as Latin."""
    cyrillic = len(re.findall(r"[а-яА-ЯёЁ]", text))
    latin = len(re.findall(r"[a-zA-Z]", text))
    return "ru" if cyrillic >= latin else "en"


def post(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get(url: str) -> dict:
    """GET a JSON endpoint, tolerating SSE (`data: {...}`) responses."""
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8", "replace")
    body = body.strip()
    try:
        return json.loads(body)
    except ValueError:
        last = None
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                payload = line[5:].strip()
                try:
                    last = json.loads(payload)
                except ValueError:
                    continue
        if last is not None:
            return last
        raise ValueError(f"no JSON/SSE payload in: {body[:200]}")


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: voicebox_tts.py <input_text_path> <output_path>", file=sys.stderr)
        return 1

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read().strip()
    output_path = sys.argv[2]

    if not text:
        print("empty text", file=sys.stderr)
        return 1

    lang = detect_language(text)

    # 1. Kick off generation. `engine` must match the profile's preset_engine.
    try:
        gen = post(
            f"{VOICEBOX_URL}/generate",
            {
                "profile_id": PROFILE_ID,
                "engine": ENGINE,
                "text": text,
                "language": lang,
                "model_size": MODEL_SIZE,
            },
        )
    except urllib.error.HTTPError as e:
        print(f"voicebox generate HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"voicebox generate failed: {e}", file=sys.stderr)
        return 1

    gen_id = gen.get("id")
    if not gen_id:
        print(f"no generation id in: {gen}", file=sys.stderr)
        return 1

    # 2. Poll until completed (status endpoint streams SSE).
    deadline = time.time() + TIMEOUT_S
    while time.time() < deadline:
        try:
            status = get(f"{VOICEBOX_URL}/generate/{gen_id}/status")
        except Exception as e:
            print(f"poll failed: {e}", file=sys.stderr)
            time.sleep(POLL_INTERVAL)
            continue

        st = status.get("status")
        if st == "completed":
            break
        if st in ("failed", "error", "cancelled"):
            print(f"voicebox generation {st}: {status.get('error')}", file=sys.stderr)
            return 1
        time.sleep(POLL_INTERVAL)
    else:
        print("voicebox generation timed out", file=sys.stderr)
        return 1

    # 3. Fetch audio bytes and write to output path.
    audio_url = f"{VOICEBOX_URL}/history/{gen_id}/export-audio"
    try:
        req = urllib.request.Request(audio_url, method="GET")
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
    except Exception as e:
        print(f"audio download failed: {e}", file=sys.stderr)
        return 1

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"ok: wrote {len(data)} bytes to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
