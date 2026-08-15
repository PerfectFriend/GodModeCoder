"""Send a local file (.md, .pdf, image, ...) to a Telegram chat via the Bot API.

Reusable utility — any time the user asks "send this file / инструкцию / скрипт в
телегу". Reads the bot token from the Hermes .env WITHOUT leaking it to stdout
(the token stays masked in tool output, logs, chat). Stdlib urllib only.

Working invocation (proven 2026-08: 'message_id: 87 OK sent'):
    python send_telegram_doc.py "C:\\path\\to\\file.md" [chat_id] ["caption"]

Charge: chat_id defaults to the user DM; pass the chat id to target a group.
"""
import os, sys, json, uuid, urllib.request, urllib.error

ENV_PATH = os.environ.get("HERMES_ENV", r"C:\Users\tomas\AppData\Local\hermes\.env")
DEFAULT_CHAT = "143293811"  # user's DM on this profile

def read_token():
    """Return TELEGRAM_BOT_TOKEN value without echoing it."""
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("ERROR: TELEGRAM_BOT_TOKEN not found in .env")

def _field(bound, name, value):
    return (f"--{bound}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode()

def _filefield(bound, fname, data, ctype):
    return (f"--{bound}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{fname}\"\r\n"
            f"Content-Type: {ctype}\r\n\r\n").encode() + data + b"\r\n"

def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = sys.argv[1]
    chat = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CHAT
    caption = sys.argv[3] if len(sys.argv) > 3 else ""
    token = _token_and_send(path, chat, caption)
    return token

def _token_and_send(path, chat, caption):
    token = _read_token_inner()
    fname = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(fname)[1].lower()
    mime = {".md":"text/markdown", ".pdf":"application/pdf", ".png":"image/png",
            ".jpg":"image/jpeg", ".json":"application/json", ".txt":"text/plain",
            ".zip":"application/zip", ".wav":"audio/wav", ".mp3":"audio/mpeg"
            }.get(ext, "application/octet-stream")
    bound = "----WF" + uuid.uuid4().hex
    body = (_field(bound, "chat_id", chat) + _field(bound, "caption", caption)
            + _filefield(bound, fname, data, mime) + (f"--{bound}--\r\n").encode())
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={bound}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            r = json.loads(resp.read().decode())
        print(f"OK sent. message_id: {r['result']['message_id']}")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:300]}")
    except Exception as e:
        raise SystemExit(f"Error: {e}")

def _read_token_inner():
    for line in open(ENV_PATH, encoding="utf-8"):
        line = line.strip()
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("ERROR: TELEGRAM_BOT_TOKEN not found in .env")

if __name__ == "__main__":
    main()