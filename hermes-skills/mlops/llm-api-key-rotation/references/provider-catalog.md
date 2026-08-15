# LLM Provider Catalog (verified mid-2026)

Endpoints, key prefixes, free-model lists, and quota quirks discovered while building rotation pools. Verify quotas with a burst test — they change.

## Verified providers

### NVIDIA NIM
- **Base**: `https://integrate.api.nvidia.com/v1` (OpenAI-compatible)
- **Key**: `nvapi-...`
- **Env**: `NVIDIA_API_KEY`
- **Models**: 102 listed; free tier includes nemotron family
- **Quota**: ~1000 req/day/key, ~40 RPM. Verified: 429 on the 5th rapid-fire request; rate-limited state auto-clears (~45 min window observed in Hermes auth list)
- **Test model**: `nvidia/llama-3.3-nemotron-super-49b-v1`
- **Quirk**: no rate-limit headers in responses; only way to find limits is burst testing

### OpenCode Zen
- **Base**: `https://opencode.ai/zen/v1` (OpenAI-compatible)
- **Key**: `sk-...` (ambiguous prefix — MUST validate against this endpoint)
- **Env**: `OPENCODE_ZEN_API_KEY`
- **Provider id in Hermes**: `opencode-zen` (aliases: `opencode`, `zen`)
- **Models**: 20 total, 6 free: `deepseek-v4-flash-free`, `mimo-v2.5-free`, `ling-3.0-flash-free`, `nemotron-3-ultra-free`, `north-mini-code-free`, `laguna-s-2.1-free`
- **Quota**: softer than NVIDIA — 25 rapid-fire calls all OK; ~1000+/day estimated
- **Quirk**: `api.opencode.ai/v1/models` is NOT a real endpoint (returns 404 with HTTP 200 status — a classic false-positive validation trap). The real path is `opencode.ai/zen/v1`. Also: `https://opencode.ai/api/v1/models` returns HTML 404 page — also a trap.

### OpenRouter
- **Base**: `https://openrouter.ai/api/v1`
- **Key**: `sk-or-v1-...`
- **Env**: `OPENROUTER_API_KEY`
- **Quirk**: `GET /api/v1/models` returns **200 even with no/wrong auth** — useless for validation. Must POST chat/completions (wrong key → 401).
- Free models accessible via `:free` suffix (e.g. `deepseek/deepseek-chat-v3-0324:free`)

### KiloCode
- **Base**: `https://api.kilo.ai/api/gateway/v1` (NOT api.kilocode.ai — that 404s)
- **Key**: JWT (`eyJ...`) — decode payload for user id; expiry embedded in token
- **Env**: `KILOCODE_API_KEY`
- **Models**: 344 total; **11 free** including:
  - `nvidia/nemotron-3-ultra-550b-a55b:free` (1M ctx — same model as NVIDIA's paid flagship!)
  - `openrouter/free` (aggregator of all free models)
  - `kilo-auto/free` (auto-rotates free models)
  - `stepfun/step-3.7-flash:free`, `inclusionai/ling-3.0-flash:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `cohere/north-mini-code:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `nvidia/nemotron-3.5-content-safety:free`
- **Paid bonus**: `kilo-auto/frontier` routes to Claude Opus 5 / GPT-5.6 class models at ~$0.005-0.03/1K
- **Quota**: 10/10 burst OK; effectively a free gateway to the same models as NVIDIA/Zen — great redundancy

### OpenAI
- **Base**: `https://api.openai.com/v1`
- **Key**: `sk-proj-...` (project keys)
- **Env**: `OPENAI_API_KEY` — NOTE: no `openai` or `custom` provider id exists in `hermes auth`; store in `.env` only
- **Quirk**: key can list 119 models (GET /models → 200) while ALL chat/completions return **429 `insufficient_quota`** — valid key, zero balance. Test generation, not listing.

### Gemini (recommended for volume)
- **Key**: `AIza...`, **Env**: `GOOGLE_API_KEY` / `GEMINI_API_KEY`
- **Quota**: ~1500 req/day per Google account on free tier — 15 accounts = ~22,500 req/day. Best volume source.
- Keys from: https://aistudio.google.com/apikey

## Hermes auth quirks (verified)

- `hermes auth remove <provider> <index-or-label>` — target is POSITIONAL, `--index` flag does not exist
- Removing by index repeatedly: remove highest index first (indices renumber)
- `hermes auth add` unknown provider → `Unknown provider: <name>` (provider must be a registered model-provider plugin)
- `hermes auth status <provider>` → `logged in`
- Exhausted creds show as `rate-limited (429) (Xm left)` and are skipped automatically
- `hermes fallback add` — interactive TUI picker, no non-interactive flags

## Validation script pattern

Python stdlib loop over candidate endpoints, one key at a time; 200 on chat/completions = valid. See SKILL.md Step 2 for the curl equivalent. Never batch-test via GET /models.
