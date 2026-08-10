---
title: Telegram Bot API Encoding Troubleshooting
category: reference
---

# Telegram Bot API Encoding Troubleshooting

## Problem: "strings must be encoded in UTF-8" (Error 400)

### When it happens
- Using `curl -F` with non-ASCII caption on Windows
- Using `curl -X POST` with JSON containing Unicode on Windows cmd/bash
- Any tool that doesn't properly encode UTF-8 in multipart/form-data

### Root cause
Windows console encoding (CP1251/CP866) vs Telegram API requiring UTF-8. The shell or curl sends bytes in system encoding, Telegram rejects as invalid UTF-8.

## Solutions

### 1. Use Python requests (RECOMMENDED)
```python
import requests

requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": "Привет 🌾"}  # Auto-encodes UTF-8
).raise_for_status()

# For files:
with open("file.md", "rb") as f:
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendDocument",
        data={"chat_id": CHAT_ID, "caption": "Файл 📄"},
        files={"document": ("file.md", f, "text/markdown")}
    ).raise_for_status()
```

### 2. If curl is required: Use --data-binary with explicit UTF-8
```bash
# Save JSON to file first (avoids shell encoding issues)
cat > payload.json <<'EOF'
{"chat_id": 143293811, "text": "Привет 🌾"}
EOF

curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data-binary @payload.json
```

### 3. For multipart with curl: Use a form file
```bash
# Create form data file (binary-safe)
curl -F "chat_id=143293811" \
     -F "caption=Файл 📄" \
     -F "document=@lesson-exponential-dangers.md" \
     "https://api.telegram.org/bot${TOKEN}/sendDocument"
# Still may fail on Windows — prefer Python
```

## Verification Commands

```bash
# Test token (always works — no encoding issues)
curl -s "https://api.telegram.org/bot${TOKEN}/getMe"

# Test simple ASCII message
curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id":143293811,"text":"test"}'
```

## Key Insight

**Python `requests` handles encoding automatically** because:
1. `json=` parameter encodes as UTF-8 with correct headers
2. `files=` multipart uses proper boundary and UTF-8 filenames
3. No shell encoding layer to corrupt bytes

**curl on Windows** passes through cmd/bash which may transcode based on active code page (`chcp 65001` helps but isn't reliable).

## Related Skills

- `telegram-bot-api-usage` — Main patterns
- `hermes-gateway-setup` — Gateway token location, 409 conflict resolution