---
name: llm-api-key-pools
description: "Manage LLM API key pools and rotation via hermes auth."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [api-keys, rotation, credential-pools, hermes-auth, llm-providers, rate-limits]
    related_skills: [hermes-agent, local-ai-stack]
---

# LLM API Key Pools & Rotation (hermes auth)

Manage many provider API keys so Hermes rotates them automatically when limits are exhausted. Hermes supports two layers: **credential pools** per provider (multiple keys, auto-rotation on 429) and a **fallback provider chain** (switch provider when all keys die). Both are CLI-driven.

## Commands

```bash
# Add a key to a provider's pool (rotates automatically on 429/rate-limit)
hermes auth add <provider> --type api-key --api-key <KEY> --label <label>

hermes auth list                  # pools + which key is active (←)
hermes auth status <provider>     # logged-in state
hermes auth remove <provider> <index|id|label>   # NOTE: positional, no --index flag
hermes auth reset <provider>      # clear exhaustion status (e.g. after quota refill)

# Fallback provider chain (tried in order when primary fails)
hermes fallback list
hermes fallback add               # interactive picker only — no CLI args
hermes fallback remove
```

Pitfalls:
- `hermes auth remove` takes the target POSITIONALLY (`hermes auth remove openrouter 3`) — `--index` is rejected.
- `hermes fallback add` is interactive-only (a picker); you cannot script it — plan for a terminal session.
- Some providers are NOT registered in `hermes auth` (e.g. `groq`, `openai`, `custom`) → `Unknown provider`. Register them via config aliases instead: `hermes config set model.aliases.<name>.model/provider/base_url`, and put the key in `.env` (e.g. `GROQ_API_KEY=`, `OPENAI_API_KEY=`).

## ⚠️ Key validation — GET /models 200 is NOT proof of validity

Learned the hard way (2026-08): several providers return HTTP 200 for `GET /v1/models` even with a **wrong/foreign key**:

- `api.opencode.ai/v1/models` → 200 with a `"Not Found"` HTML/JSON body.
- OpenRouter `GET /v1/models` → 200 without requiring auth at all.
- So a 200 on the models endpoint proves nothing. **Always validate with a real `POST /v1/chat/completions`** (small max_tokens) and require 200 + a completion, or an explicit quota error body.

⚠️ **config.yaml `model.base_url` vs provider mismatch = phantom 401s**: if `model.base_url` points at a DIFFERENT provider than the pool (e.g. `provider: nvidia` but `base_url: https://openrouter.ai/api/v1`), every fresh session first hits the wrong endpoint with the pool key → 401 → the pool marks the (healthy) key `exhausted` and rotates. All 7 nvidia keys looked "auth failed (401)" in `hermes auth list` while live probes returned 200. Fix: align `model.base_url` with the pool's real endpoint (`hermes config set model.base_url https://integrate.api.nvidia.com/v1`).

⚠️ **Stale statuses / gateway memory**: the running gateway (`hermes gateway run`) holds the credential pool in memory and rewrites `auth.json` — CLI `auth remove/reset` edits are clobbered until the gateway restarts. Restart from OUTSIDE the gateway process (blocked from inside: SIGTERM propagates). Windows: `schtasks /create /tn RestartGW /tr "...hermes.exe gateway restart" /sc once /st HH:MM /f`.

Watchdog: `scripts/key_watchdog.py` probes all pool keys (browser UA, retry on timeout), auto-resets stale statuses, reports dead/duplicate/quota keys; run via cron `no_agent` (silent when healthy).

Quick probe:
```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 20 \
  https://<base_url>/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0" \
  -d '{"model":"<known-model>","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
```

PITFALL (found 2026-08): Cloudflare-fronted endpoints (opencode.ai/zen, groq) return **403 `error code: 1010` to clients with a non-browser User-Agent** (Python-urllib default; curl may be fine but add `-A` anyway). All 12 zen keys showed 403 in a batch probe until a browser UA was added — always send one. Also: `hermes auth list` statuses can be stale — 7 nvidia keys flagged `auth failed (401)`/`rate-limited` there all returned 200 on a live probe.

## Key format → provider map (from real sessions)

| Prefix / shape | Provider | Base URL |
|---|---|---|
| `nvapi-...` | nvidia | https://integrate.api.nvidia.com/v1 |
| `sk-...` (long) | **opencode-zen** (NOT openrouter!) | https://opencode.ai/zen/v1 |
| `gsk_...` | groq | https://api.groq.com/openai/v1 (not in hermes auth — use alias) |
| `sk-proj-...` | openai | https://api.openai.com/v1 (not in hermes auth) |
| `AQ.Ab8...` | google gemini (AI Studio) | https://generativelanguage.googleapis.com |
| JWT (`eyJ...`) | kilocode | https://api.kilo.ai/api/gateway |
| `sk-or-...` | openrouter | https://openrouter.ai/api/v1 |

- opencode-zen provider aliases: `opencode`, `zen` (so the *session provider* "opencode" IS the opencode-zen pool).
- A key can pass the models-200 check on MULTIPLE providers — that's the trap. e.g. `sk-` opencode keys returned 200 on openrouter's unauthenticated models endpoint → they were wrongly pooled there first; the chat-completions probe (401) exposed it, then the pool had to be cleaned.

## Capacity planning (how many agents can run 24/7)

Rough per-key free-tier throughput (verify with a burst test — N sequential chat-completions, count 429s):
- nvidia NIM: ~40 RPM, ~1000 req/day per key (429s appear fast under load)
- opencode-zen: softer limits (25/25 burst OK)
- groq: ~30 RPM, ~14,400 req/day
- gemini (AI Studio): ~1500 req/day per account

Budget: an always-busy subagent ≈ 3000–5000 req/day. So `nvidia×6 + zen×12 + groq×1` ≈ 18–28k req/day ≈ **3–5 concurrent agents**, or ~8–10 with a gemini multi-account pool.

## Adding a provider that's not in `hermes auth` (groq example)

```bash
# 1. Key into .env (secrets belong there, not config.yaml)
# 2. Alias in config.yaml (config set writes nested keys correctly):
hermes config set model.aliases.groq-llama.model "llama-3.3-70b-versatile"
hermes config set model.aliases.groq-llama.provider "custom"
hermes config set model.aliases.groq-llama.base_url "https://api.groq.com/openai/v1"
# 3. Use via /model groq-llama (CLI or Telegram)
```
NOTE: write the alias as a full nested object in ONE config edit if possible — setting `.base_url` after the short-form string overwrote the whole alias in one session; re-add `.model`/`.provider` afterwards.

See `references/provider-key-notes.md` for validated endpoints and per-provider quirks.
