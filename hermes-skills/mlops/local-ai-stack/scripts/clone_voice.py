#!/usr/bin/env python3
"""
Voicebox voice-cloning CLI (proven 2026-08, Windows + git-bash).

Creates a cloned profile from audio samples, uploads them, and tests generation.

Usage:
    python clone_voice.py create --name "Голос Мастера" [--language ru]
    python clone_voice.py add-sample --profile <id> --audio file.wav --text "что сказано"
    python clone_voice.py samples --profile <id>
    python clone_voice.py test --profile <id> --text "Привет, это тест клона!"

Pitfalls baked in:
  * cloned profile: send NO preset_engine/preset_voice_id AND NO default_engine
    (qwen_custom_voice as default_engine -> 400; discovered 2026-08)
  * poll GET /history/{id} (plain JSON) — /generate/{id}/status is SSE and hangs urllib
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

VOICEBOX = "http://127.0.0.1:8000"


def post_json(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def get_json(url):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def post_multipart(url, file_path, text):
    """Upload one audio sample + reference_text (multipart/form-data)."""
    boundary = "----VoiceboxClone" + str(int(time.time()))
    with open(file_path, "rb") as f:
        audio = f.read()
    fn = os.path.basename(file_path)
    parts = []
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fn}\"\r\n"
                 f"Content-Type: application/octet-stream\r\n\r\n".encode())
    parts.append(audio)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"reference_text\"\r\n\r\n{text}\r\n".encode("utf-8"))
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def wait_done(gen_id, timeout=600):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            st = get_json(f"{VOICEBOX}/history/{gen_id}")
        except Exception:
            time.sleep(3)
            continue
        if st.get("status") == "completed":
            return st
        if st.get("status") in ("failed", "error"):
            raise RuntimeError(f"Генерация {st.get('status')}: {st.get('error')}")
        time.sleep(3)
    raise TimeoutError("Таймаут генерации")


def cmd_create(args):
    payload = {"name": args.name, "voice_type": "cloned", "language": args.language}
    # NOTE: no engine fields — cloned profiles reject default_engine (400)
    try:
        r = post_json(f"{VOICEBOX}/profiles", payload)
        pid = r.get("profile_id") or r.get("id")
        print(f"OK profile: {pid} name={r.get('name')}")
        return pid
    except urllib.error.HTTPError as e:
        print(f"ERR HTTP {e.code}: {e.read().decode('utf-8','replace')[:300]}")
        return None


def cmd_add_sample(args):
    r = post_multipart(f"{VOICEBOX}/profiles/{args.profile}/samples", args.audio, args.text)
    print(f"OK sample: {r.get('id')} audio={r.get('audio_path')}")


def cmd_list_samples(args):
    r = get_json(f"{VOICEBOX}/profiles/{args.profile}/samples")
    items = r if isinstance(r, list) else r.get("samples", r.get("items", []))
    print(f"Samples: {len(items)}")
    for s in items:
        print(f"  {s.get('id')} | {s.get('audio_path')} | {str(s.get('reference_text'))[:50]}")


def cmd_test(args):
    payload = {"profile_id": args.profile, "text": args.text, "language": args.language}
    if args.engine:
        payload["engine"] = args.engine  # engine is per-request for clones
    gen = post_json(f"{VOICEBOX}/generate", payload)
    gid = gen.get("id")
    print(f"Generation: {gid} ...")
    st = wait_done(gid)
    audio = st.get("audio_path")
    print(f"OK: {audio}")
    full = os.path.join(r"C:\Users\tomas\Voicebox\data", audio.replace("\\", os.sep)) \
        if not os.path.isabs(audio) else audio
    if os.path.exists(full):
        print(f"   File: {full} ({os.path.getsize(full)} bytes)")
    else:
        print(f"   File not found: {full}")


def main():
    ap = argparse.ArgumentParser(description="Voicebox voice cloning CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create", help="create cloned profile (no engine fields!)")
    p.add_argument("--name", required=True)
    p.add_argument("--language", default="ru")
    p.set_defaults(fn=cmd_create)

    p = sub.add_parser("add-sample", help="upload one audio sample")
    p.add_argument("--profile", required=True)
    p.add_argument("--audio", required=True)
    p.add_argument("--text", required=True)
    p.set_defaults(fn=cmd_add_sample)

    p = sub.add_parser("samples", help="list samples of a profile")
    p.add_argument("--profile", required=True)
    p.set_defaults(fn=cmd_list_samples)

    p = sub.add_parser("test", help="test generation")
    p.add_argument("--profile", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--engine", default=None)
    p.add_argument("--language", default="ru")
    p.set_defaults(fn=cmd_test)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
