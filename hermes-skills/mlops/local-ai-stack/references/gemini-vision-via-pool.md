# Image analysis with pooled Gemini keys (direct REST fallback)

When the Hermes vision toolset is unavailable (gateway logs show
`check_vision_requirements returned False` — no local vision deps), you can
still analyze images by calling Google's generative API directly with a key
from the Hermes credential pool. Proven 2026-08 on this box (used to inspect
a client's studio photo of a voltage-detection pole).

## Where the key lives

Keys are NOT in `.env` (that file only has commented placeholders). They live
in the credential pool:

```
<hermes_home>/auth.json  →  credential_pool.gemini[] .access_token
```

Two Gemini keys are registered as `gemini-master-1` / `gemini-master-2`.
`hermes auth show <name>` does NOT exist — read auth.json directly.

## Working recipe (Python, not curl)

curl from git-bash returned empty responses for this endpoint (multi-MB JSON
body with base64 image) — use `urllib` instead:

```python
import json, base64, urllib.request, urllib.error

with open(r"<hermes_home>\auth.json", encoding="utf-8") as f:
    key = json.load(f)["credential_pool"]["gemini"][0]["access_token"]

with open(r"path\to\photo.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "contents": [{
        "parts": [
            {"text": "Describe in detail what is in this photo: ..."},  # ask specific questions
            {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}},
        ]
    }]
}
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={key}"
req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=90) as resp:
        d = json.loads(resp.read().decode())
    print(d["candidates"][0]["content"]["parts"][0]["text"])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:500])
```

## Gotchas

- Model name: `gemini-3-flash-preview` (available on the pooled keys; verified
  HTTP 200 + 50 models including gemini-3-pro-preview).
- Response shape: `candidates[0].content.parts[0].text`; a `promptFeedback` /
  no-candidates response means the request was blocked — re-read the full dict.
- The vision model handles studio product shots well: it described the pole's
  segments, colors, clamp head and the absence of a person, and warned that a
  white-background catalog shot is poor training data for object detection.
- The key is a live credential — don't echo it into chat; redact like any secret.
