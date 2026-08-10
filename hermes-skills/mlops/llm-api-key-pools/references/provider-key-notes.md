# Provider key endpoints & quirks (validated 2026-08)

All base URLs are OpenAI-compatible (`/v1/chat/completions`) unless noted.

## nvidia (NIM)
- Base: `https://integrate.api.nvidia.com/v1`
- Key: `nvapi-...`
- `GET /v1/models` returns ~102 models; free tier ~40 RPM / ~1000 req/day per key (429s under burst).
- Include `nvidia/` prefix on model ids where the catalog shows it (`nvidia/llama-3.3-nemotron-super-49b-v1`).

## opencode-zen (the "opencode" provider)
- Base: `https://opencode.ai/zen/v1`
- Key: `sk-...` (long, NOT `sk-or-`)
- Provider aliases in Hermes: `opencode`, `zen`, `opencode_zen`; env var `OPENCODE_ZEN_API_KEY`.
- `GET /v1/models` → 20 models, 6 free incl. `deepseek-v4-flash-free`, `nemotron-3-ultra-free`, `mimo-v2.5-free`, `ling-3.0-flash-free`.
- Free model confirmed working with `"cost": 0` in usage.
- TRAP: `api.opencode.ai/v1/models` (wrong host, no `/zen/`) returns HTTP 200 with a "Not Found" body — does NOT validate keys.

## openrouter
- Base: `https://openrouter.ai/api/v1`
- Key: `sk-or-...`
- TRAP: `GET /v1/models` returns 200 WITHOUT auth — useless for validation. Use chat-completions probe.

## groq
- Base: `https://api.groq.com/openai/v1`
- Key: `gsk_...`
- NOT in `hermes auth` — register via model alias (provider: custom).
- 15 models incl. `llama-3.3-70b-versatile`, `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`, whisper-large-v3 (STT).

## openai
- Base: `https://api.openai.com/v1`
- Key: `sk-proj-...`
- NOT in `hermes auth` — put in `.env` as `OPENAI_API_KEY`.
- 119 models visible; a key with no billing returns `insufficient_quota` 429 on chat-completions even though /models works. Check `{"error":{"code":"insufficient_quota"}}` body.

## google gemini (AI Studio)
- Base: `https://generativelanguage.googleapis.com/v1beta`
- Key: `AQ.Ab8...` (new AI Studio format), passed as `?key=` query param.
- 50 models incl. gemini-2.5-flash, gemini-3-flash/pro previews.

## kilocode
- Base: `https://api.kilo.ai/api/gateway` (NOT api.kilocode.ai — that 404s)
- Key: JWT (`eyJhbGci...`)
- 344 models, 11 free: `nvidia/nemotron-3-ultra-550b-a55b:free`, `openrouter/free` (aggregator), `kilo-auto/free`, stepfun/ling/laguna/cohere free variants.
- Also exposes paid frontier models (claude-opus-5, gpt-5.6-sol) at low rates — useful escape hatch.

## Cleaning up a wrongly-populated pool
```bash
hermes auth list                       # find indexes
hermes auth remove openrouter 12       # remove by index, high→low to keep indexes stable
```
