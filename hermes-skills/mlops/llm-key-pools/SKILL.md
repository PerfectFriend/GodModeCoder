---
name: llm-key-pools
description: "Add provider API keys to Hermes pools with rotation."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LLM, API-keys, providers, rotation, credential-pools, fallback]
    related_skills: [hermes-agent]
---

# LLM Provider Key Pools & Rotation (Hermes)

Use when a user hands you API keys for one or more LLM providers and wants pooled rotation, fallback chains, or capacity planning — e.g. "add these to rotation", "make a config with these keys", "will these last for N agents?".

## Core mechanics

- **Pools** — multiple credentials per provider; Hermes auto-rotates to the next key on rate-limit (429) / exhaustion, and skips unhealthy ones for a cooldown window.
- **Fallback chain** — cross-provider order tried when the primary model fails (rate-limit, overload, connection). Managed separately from pools.

## Commands (exact syntax)

```bash
hermes auth add <provider> --type api-key --api-key <KEY> --label <label>
hermes auth list                       # pools; ← = active credential
hermes auth status <provider>          # 'logged in' + pool health
hermes auth reset <provider>           # clear exhaustion flag after quota refresh
hermes auth remove <provider> <target> # target = INDEX, id, or exact label (POSITIONAL!)
hermes fallback list | add | remove    # add is an interactive picker only
```

Pitfalls:
- `hermes auth remove openrouter --index 5` → error "unrecognized arguments: --index". The target is positional: `hermes auth remove openrouter 5`.
- A key already in `.env` as `<PROVIDER>_API_KEY` shows in the pool as an `env:` entry (usually #1). Manual keys join after it.
- Rate-limited keys show as `rate-limited (429) (NNm left)` — rotation skips them automatically until reset.
- Do NOT store credentials via `hermes config set` — it warns "not a recognized config key" and saves a dead key. Secrets go in `.env` or `hermes auth`; settings go in config.yaml.
- Platform tokens follow the same rule: e.g. Telegram bot token goes in `.env` as `TELEGRAM_BOT_TOKEN` (+ `TELEGRAM_ALLOWED_USERS` = owner chat id), and the platform is enabled with `hermes config set platforms.telegram.enabled true` — never `gateway.telegram.bot_token` in config.yaml (unrecognized). The `.env` file ships with commented templates listing the exact env var names — read them before guessing.

## Validating keys — GET /models is a TRAP

A 200 on `GET /v1/models` does NOT prove a key works:
- openrouter.ai/api/v1/models returns 200 even with a bogus key (model list is public).
- api.opencode.ai/v1/models returns "Not Found" with HTTP 200 (not a real endpoint).
- opencode.ai/zen/v1/models returns 403 for invalid keys.

ALWAYS validate with a real completion:

```bash
curl -s -w "\nHTTP:%{http_code}" --max-time 30 <BASE>/v1/chat/completions \
  -H "Authorization: Bearer <KEY>" -H "Content-Type: application/json" \
  -d '{"model":"<real-model>","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
```

Valid key → 200 + a completion (check `"cost":"0"` for free tier). Invalid → 401/403. Same rule applies to provider attribution: a key that 200s two providers' /models endpoints is valid for at most one — the completion probe settles it.

## Common provider base URLs / env vars

| Provider id | Base | Env var |
|---|---|---|
| opencode-zen (alias `opencode`) | https://opencode.ai/zen/v1 | OPENCODE_ZEN_API_KEY |
| nvidia | https://integrate.api.nvidia.com/v1 | NVIDIA_API_KEY |
| openrouter | https://openrouter.ai/api/v1 | OPENROUTER_API_KEY |
| kilocode | https://api.kilo.ai/api/gateway | KILOCODE_API_KEY |
| gemini | (provider default) | GOOGLE_API_KEY / GEMINI_API_KEY |
| groq | https://api.groq.com/openai/v1 | GROQ_API_KEY |

Free models on opencode-zen (verified): deepseek-v4-flash-free, mimo-v2.5-free, ling-3.0-flash-free, nemotron-3-ultra-free, north-mini-code-free, laguna-s-2.1-free.

KiloCode (JWT key, starts `eyJ…`): 344 models, 11 free — incl `nvidia/nemotron-3-ultra-550b-a55b:free` (our main model for free), `openrouter/free` (aggregator over all free models), `kilo-auto/free`. Validated 10/10 with zero refusals. Note the base URL is `api.kilo.ai/api/gateway`, NOT api.kilocode.ai (404).

## Providers NOT in `hermes auth` (workarounds)
- **Groq** (`gsk_`): `hermes auth add groq` → "Unknown provider" (only used for STT). Write `GROQ_API_KEY` to `.env`, then add aliases: `hermes config set model.aliases.groq-llama "custom/llama-3.3-70b-versatile"`, then `.base_url` = https://api.groq.com/openai/v1, and RE-SET `.model` + `.provider` = custom — setting `.base_url` on a `provider/model` string alias drops the model+provider fields, leaving a dead alias.
- **OpenAI** (`sk-proj-`): no `openai` pool provider (only `openai-codex` OAuth). Put `OPENAI_API_KEY` in `.env`. If the key is valid but generation returns 429 `insufficient_quota`, the account has no balance — keep the key (activates on top-up), don't delete.
- Probe supported ids cheaply: `hermes auth add <anything>` prints "Unknown provider".

## Capacity math (rule of thumb)

- Free-tier key ≈ 1000 req/day (NVIDIA: ~40 RPM, 429 on burst — measured; Zen: softer limit; KiloCode: ~10k+ via free-model aggregator).
- One continuously working subagent ≈ 4–5k req/day.
- ~18k req/day (6 NVIDIA + 12 Zen keys) ≈ 3–4 concurrent subagents ≈ 500–900 tasks/day.
- 6 NVIDIA + 12 Zen + 1 KiloCode ≈ 28k+ req/day ≈ 6–7 concurrent subagents (KiloCode adds a resilient second path to the same free models).
- `delegation.max_concurrent_children` (config) caps parallelism; raise it only when key supply supports it.

## Adding a provider (workflow)

1. Identify provider by key format: `nvapi-` = NVIDIA, `sk-or-` = OpenRouter, `sk-proj-` = OpenAI (env-only), `sk-` = ambiguous (validate!), `gsk_` = Groq (alias route), `eyJ…` JWT = KiloCode, `AIza` = Gemini.
2. Validate each key with the completion probe above.
3. `hermes auth add <provider> --type api-key --api-key <KEY> --label <label>` per key.
4. `hermes auth list` to confirm pool + active credential.
5. Optionally append the provider to the fallback chain (`hermes fallback add`, interactive).

## Priority order for free keys (2026)

Gemini (AI Studio; multiple Google accounts multiply the pool) > Groq > GLM/Zhipu > Cerebras > OpenRouter `:free` > Kimi > Mistral.

Full limits table and key-get URLs: `references/free-tier-limits.md`.
