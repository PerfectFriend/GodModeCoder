# LLM Provider Free-Tier Limits (checked 2026-08)

Measured in-session where noted; otherwise from provider docs. Limits change — re-verify before promising capacity.

| Provider | Key format / where | Free tier | Notes |
|---|---|---|---|
| Google Gemini | `AIza…` — https://aistudio.google.com/apikey | ~1500 req/day/key, 10–15 RPM | gemini-2.5/3-flash; best free models; multiple Google accounts multiply the pool (15 accs ≈ 22.5k req/day) |
| Groq | `gsk_…` — https://console.groq.com/keys | ~14,400 req/day, 30 RPM | llama-3.3-70b, llama-3.1-405b; very fast |
| Cerebras | https://cloud.cerebras.ai | ~14,000 req/day, 30 RPM | llama-3.3-70b; fastest inference (~2200 tok/s) |
| NVIDIA NIM | `nvapi-…` — https://build.nvidia.com | ~1000 req/day, ~40 RPM per key | 429 on burst fire (measured); 102 models, 24 free/nemotron |
| OpenCode Zen | `sk-…` — https://opencode.ai/zen/v1 | soft limit; 25/25 burst OK (measured) | 6 free models incl. deepseek-v4-flash-free (cost "0") |
| GLM (Zhipu/Z.ai) | https://open.bigmodel.cn | 200 RPM, ~1000 req/day | glm-4.5-flash strong for code |
| Kimi (Moonshot) | https://platform.moonshot.ai | free tier exists | kimi-k2 / kimi-k2-thinking |
| Mistral | https://console.mistral.ai | 1 RPM, ~500 req/day | weak but free |
| OpenRouter | `sk-or-…` — https://openrouter.ai/settings/keys | `:free` models ~50–1000 req/day | gateway to ALL :free models |
| xAI (Grok) | https://console.x.ai | ~150 req/day | weak |
| SambaNova / Together / Fireworks | — | limited free tier | llama-family, mid |

Key format quick map: NVIDIA `nvapi-…`, OpenCode Zen `sk-…`, Groq `gsk_…`, Gemini `AIza…`, OpenRouter `sk-or-v1-…`. A bare `sk-…` is ambiguous — validate with the completion probe, never assume OpenRouter.

Validation rule: never trust `GET /v1/models` returning 200 (public model lists and fake endpoints return 200 for any key). Probe `POST <base>/v1/chat/completions` with `max_tokens:5`.
