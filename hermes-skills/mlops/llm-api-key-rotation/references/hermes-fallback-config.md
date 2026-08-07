# Hermes Fallback Provider Configuration — Session 2026-08-06

## Configured Fallback Chain (config.yaml)

```yaml
fallback_model:
  provider: opencode-zen
  model: nemotron-3-ultra-free
fallback_providers:
  '0':
    provider: opencode-zen
    model: nemotron-3-ultra-free
  '1':
    provider: opencode-zen
    model: deepseek-v4-flash-free
  '2':
    provider: opencode-zen
    model: kimi-k3
  '3':
    provider: gemini
    model: gemini-2.0-flash
  '4':
    provider: kilocode
    model: deepseek-v4-flash-free
  '5':
    provider: openai-api
    model: gpt-4o-mini
```

## CLI Commands Used

```bash
# Primary fallback
hermes config set fallback_model.provider opencode-zen
hermes config set fallback_model.model nemotron-3-ultra-free

# Fallback providers array
hermes config set fallback_providers.0.provider opencode-zen
hermes config set fallback_providers.0.model nemotron-3-ultra-free
hermes config set fallback_providers.1.provider opencode-zen
hermes config set fallback_providers.1.model deepseek-v4-flash-free
hermes config set fallback_providers.2.provider opencode-zen
hermes config set fallback_providers.2.model kimi-k3
hermes config set fallback_providers.3.provider gemini
hermes config set fallback_providers.3.model gemini-2.0-flash
hermes config set fallback_providers.4.provider kilocode
hermes config set fallback_providers.4.model deepseek-v4-flash-free
hermes config set fallback_providers.5.provider openai-api
hermes config set fallback_providers.5.model gpt-4o-mini

# Reset auth status to clear any exhaustion
hermes auth reset opencode-zen
```

## Verification

```bash
# Check fallback config
hermes config get fallback_providers

# Check auth status for all fallback providers
hermes auth status opencode-zen
hermes auth status gemini
hermes auth status kilocode
hermes auth status openai-api
```

## Provider Status (2026-08-06)

| Provider | Keys | Status | Notes |
|----------|------|--------|-------|
| NVIDIA | 6 | ✅ logged in | Primary (nemotron-3-ultra) |
| OpenCode Zen | 12 | ✅ logged in | Fallback #1-3 |
| Gemini | 2 | ✅ logged in | Fallback #4 |
| KiloCode | 1 | ✅ logged in | Fallback #5 |
| OpenAI | 1 | ✅ logged in | Fallback #6 |

## OpenCode Zen Free Models (Validated)

| Model | Status | Use as Fallback |
|-------|--------|-----------------|
| `nemotron-3-ultra-free` | ✅ 200, cost: 0 | ✅ Primary |
| `mimo-v2.5-free` | Listed free | ✅ Candidate |
| `longcat-2.0-free` | Listed free | ✅ Candidate |
| `north-mini-code-free` | Listed free | ✅ Candidate |
| `laguna-s-2.1-free` | Listed free | ✅ Candidate |
| `ling-3.0-flash-free` | Listed free | ✅ Candidate |
| `deepseek-v4-flash-free` | 429 rate limited | ⚠️ Backup only |
| `kimi-k3` | 401 Paid | ❌ Avoid |

## Fallback Priority Logic

1. **NVIDIA (6 keys)** → Primary, 40 RPM, ~1000 req/day
2. **OpenCode Zen (12 keys)** → 2nd priority, softer limits, free tier works
3. **Gemini (2 keys)** → 3rd priority, 1500/day/account
4. **KiloCode (1 key)** → 4th priority, aggregates free models
5. **OpenAI (1 key)** → Last resort, needs billing

## Key Insight

OpenCode Zen has **2x more keys than NVIDIA** (12 vs 6) and softer rate limits, making it the ideal first fallback. The free model `nemotron-3-ultra-free` is confirmed working with `cost: '0'`.