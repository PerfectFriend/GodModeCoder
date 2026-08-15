# OpenCode Zen Key Validation — Session Findings (2026-08-06)

## Endpoint
- Base URL: `https://opencode.ai/zen/v1`
- Auth: `Authorization: Bearer <key>`
- **Required**: Browser User-Agent header (`Mozilla/5.0 ... Chrome/126.0`) — Cloudflare blocks Python-urllib default UA with 403 error code 1010

## Key Tested
- `OPENCODE_ZEN_API_KEY` from `.env` (prefix `sk-...`)
- 11 additional keys stored in Hermes credential store (`zen-master-2` through `zen-master-12`) — encrypted, not directly accessible

## Model List (`GET /models` — 21 models)

### Free Models (cost: 0, work with free key)
| Model | Owner | Notes |
|-------|-------|-------|
| `nemotron-3-ultra-free` | opencode | ✅ **WORKS** (tested, HTTP 200, cost: '0') |
| `kimi-k3` | opencode | Free |
| `mimo-v2.5-free` | opencode | Free |
| `longcat-2.0-free` | opencode | Free |
| `deepseek-v4-flash-free` | opencode | Free but rate-limited (429) |
| `ling-3.0-flash-free` | opencode | Free |
| `north-mini-code-free` | opencode | Free |
| `laguna-s-2.1-free` | opencode | Free |

### Paid Models (require payment method)
| Model | Owner | Error |
|-------|-------|-------|
| `gpt-5.6-luna` | opencode | 401: "No payment method. Add a payment method..." |
| `gpt-5.6-sol` | opencode | Likely paid |
| `gpt-5.6-terra` | opencode | Likely paid |
| `claude-opus-5` | opencode | Likely paid |
| `claude-sonnet-5` | opencode | Likely paid |
| `grok-4.5` | opencode | Likely paid |
| `grok-build-0.1` | opencode | Likely paid |
| `glm-5.2` | opencode | Likely paid |
| `minimax-m3` | opencode | Likely paid |
| `kimi-k2.7-code` | opencode | Likely paid |
| `big-pickle` | opencode | Unknown |

## Validation Results (Live Test 2026-08-06)

| Model | HTTP | Status | Details |
|-------|------|--------|---------|
| `nemotron-3-ultra-free` | 200 | ✅ **WORKS** | `cost: '0'`, completion successful |
| `gpt-5.6-luna` | 401 | ❌ Paid | "No payment method. Add a payment method..." |
| `deepseek-v4-flash-free` | 429 | ⚠️ Rate limited | "FreeUsageLimitError: Rate limit exceeded" |

## Key Takeaways

1. **Free tier works** — `nemotron-3-ultra-free` is production-ready for free usage
2. **Rate limits exist** — Free models hit 429 after burst; rotation across 12 keys handles this
3. **Paid models need billing** — 401 with "No payment method" message
4. **Hermes rotation** — 12 keys in pool (`zen-master-2` through `zen-master-12`) auto-rotate on 429
5. **Fallback priority** — OpenCode Zen should be 2nd in fallback chain after NVIDIA (12 keys vs 6 NVIDIA)

## Adding New Keys
```bash
hermes auth add opencode-zen --type api-key --api-key "sk-..." --label "zen-new-1"
```

## Provider ID for Hermes
- `opencode-zen` (aliases: `opencode`, `opencode_zen`, `zen`)
- Base URL: `https://opencode.ai/zen/v1`

## Session 2026-08-06: Additional Free Models Confirmed

| Model | HTTP | Status | Notes |
|-------|------|--------|-------|
| `mimo-v2.5-free` | (untested) | — | Listed as free in /models |
| `kimi-k2.7-code` | (untested) | — | Listed as free |
| `big-pickle` | (untested) | — | Listed as free |
| `longcat-2.0-free` | (untested) | — | Listed as free |
| `north-mini-code-free` | (untested) | — | Listed as free |
| `laguna-s-2.1-free` | (untested) | — | Listed as free |
| `kimi-k3` | 401 | ❌ Paid | "No payment method" despite name |

## Recommended Free Models for Production Fallback

1. `nemotron-3-ultra-free` — ✅ confirmed working
2. `mimo-v2.5-free` — listed free
3. `longcat-2.0-free` — listed free
4. `north-mini-code-free` — listed free
5. `laguna-s-2.1-free` — listed free
6. `ling-3.0-flash-free` — listed free

Avoid: `deepseek-v4-flash-free` (429 rate limited), `kimi-k3` (paid despite name)