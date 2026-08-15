---
name: llm-api-key-rotation
description: "Use when adding/rotating LLM API keys into credential pools."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [llm, api-keys, providers, rotation, auth-pools, free-tier]
---

# LLM API Key Rotation & Provider Pools

Add API keys from many LLM providers into Hermes credential pools, validate they actually work, estimate free-tier capacity, and wire rotation so the agent survives exhausted quotas.

## Trigger

- User hands over a batch of API keys ("add to rotation", "добавь в ротацию", "check what's free")
- Need to identify which provider a key belongs to
- Need to validate keys, estimate capacity, or build a fallback chain

## Step 1 — Identify provider by key prefix

| Prefix | Provider | Typical env var |
|---|---|---|
| `nvapi-` | NVIDIA NIM | `NVIDIA_API_KEY` |
| `sk-proj-` | OpenAI (project key) | `OPENAI_API_KEY` |
| `sk-or-v1-` | OpenRouter | `OPENROUTER_API_KEY` |
| `gsk_` | Groq | `GROQ_API_KEY` |
| `AIza` | Google Gemini | `GOOGLE_API_KEY` |
| `xai-` | xAI | `XAI_API_KEY` |
| `hf_` | HuggingFace | `HF_TOKEN` |
| JWT (`eyJ...`) | KiloCode | `KILOCODE_API_KEY` |
| `sk-` (ambiguous) | DeepSeek / OpenCode Zen / Moonshot / others | validate (Step 2) |

Ambiguous `sk-` keys MUST go through Step 2 — prefix alone can't tell DeepSeek from OpenCode Zen.

## Step 2 — Validate with a REAL chat/completions call

**CRITICAL PITFALL: a `GET /v1/models` returning 200 proves NOTHING.** OpenRouter's `/api/v1/models`, `api.opencode.ai/v1/models`, and several others return 200 (or 404-with-200) to unauthenticated or wrong-key requests. The only reliable validation is a minimal completion:

```bash
curl -s -w "\nHTTP:%{http_code}" --max-time 30 "$BASE/v1/chat/completions" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0" \
  -d '{"model":"<cheap-model>","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
```

**OpenCode Zen specific validation** (tested 2026-08):
- **Free models that work**: `nemotron-3-ultra-free` (200, cost: 0), `mimo-v2.5-free`, `kimi-k2.7-code`, `big-pickle`, `longcat-2.0-free`, `north-mini-code-free`, `laguna-s-2.1-free`
- **Paid models**: `gpt-5.6-*`, `claude-*`, `grok-*` → 401 without payment method
- **Rate limited free**: `deepseek-v4-flash-free` (429), `kimi-k3` (paid: 401)
- **Validation pattern**: Always test a free model (`nemotron-3-ultra-free` recommended) with `max_tokens:5-10`
- **Cloudflare UA-block**: opencode.ai returns 403 `error code: 1010` to non-browser User-Agent — always send `Mozilla/5.0...Chrome/126.0`

## OpenCode Zen duplicate key detection & removal (2026-08):
- **Problem**: Multiple keys with identical values in pool (e.g., `zen-master-4` = `opencode-new-4`, `zen-master-6` = `opencode-new-5`, etc.)
- **Detection**: `hermes auth list opencode-zen` → compare key prefixes (first 10 chars + last 10 chars) OR use script to extract all keys and find exact duplicates
- **Common duplicate patterns found** (2026-08):
  - `zen-master-4` = `opencode-new-4` (sk-B86...)
  - `zen-master-6` = `opencode-new-5` (sk-fKf...)
  - `zen-master-10` = `opencode-new-7` (sk-fKf...)
  - `zen-master-7` = `opencode-new-6` (sk-4jh...)
  - `zen-master-9` = `opencode-new-8` (sk-lGc...)
  - `zen-master-11` = `opencode-new-9` (sk-ZJs...)
  - `zen-master-12` = `opencode-new-10` (sk-6bO...)
  - `opencode-new-11` = `zen-master-5` (sk-lGc...)
  - `opencode-new-12` = `zen-master-12` (sk-6bO...)
- **Removal**: `hermes auth remove opencode-zen "<label>"` — run for each duplicate (note: indices shift after each removal, always use current index #13 for next opencode-new-*)
- **Result**: Reduced from 24 keys to 8 unique (1 env + 7 master)
- **Automation tip**: Script to compare key values and auto-remove duplicates before adding to pool

**OpenCode Zen validation script (2026-08 session)**:
```python
# Quick validation of all keys against nemotron-3-ultra-free
import requests, re

env_path = r'C:\Users\tomas\AppData\Local\hermes\.env'
with open(env_path, 'r') as f:
    content = f.read()
m = re.search(r'OPENCODE_ZEN_API_KEY=(sk-[^\s]+)', content)
env_key = m.group(1) if m else None

headers_base = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0'}

def test_key(label, key):
    if not key:
        return None
    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'User-Agent': headers_base['User-Agent']}
    r = requests.post('https://opencode.ai/zen/v1/chat/completions', headers=headers, json={'model': 'nemotron-3-ultra-free', 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5}, timeout=15)
    return r.status_code

# Test env key first
print('Testing env key...')
print(f'  nemotron-3-ultra-free: {test_key("env", env_key)}')

# For manual keys in credential store, use hermes auth list to get labels, then test each
# hermes auth list opencode-zen | grep "manual" | awk '{print $2}'
```
- **Result**: Validated 8 unique keys, all working for `nemotron-3-ultra-free` (cost: 0)

**OpenCode Zen key pool rotation** (tested 2026-08):
- 12 keys in pool (`zen-master-2` through `zen-master-12` + `OPENCODE_ZEN_API_KEY`)
- All keys in Hermes credential pool via `hermes auth add opencode-zen --type api-key --api-key "sk-..." --label "zen-master-N"`
- **Free tier**: `nemotron-3-ultra-free` works (200, cost: 0), `deepseek-v4-flash-free` rate limited (429), `kimi-k3` requires payment (401)
- **Fallback chain**: Primary NVIDIA → OpenCode Zen (free models) → Gemini → KiloCode → OpenAI
- **Fallback config** in `config.yaml`:
```yaml
fallback_providers:
  '0': { provider: opencode-zen, model: nemotron-3-ultra-free }
  '1': { provider: opencode-zen, model: deepseek-v4-flash-free }
  '2': { provider: opencode-zen, model: kimi-k3 }
  '3': { provider: gemini, model: gemini-2.0-flash }
  '4': { provider: kilocode, model: deepseek-v4-flash-free }
  '5': { provider: openai-api, model: gpt-4o-mini }
```
- **Auto-reset**: `hermes auth reset opencode-zen` clears exhaustion after quota refresh

Interpretation:
- **200** → key works (check body `cost: 0` to confirm free tier)
- **401** → wrong provider / invalid key
- **403** → either truly forbidden OR **Cloudflare UA-block (`error code: 1010`)** — retry with a browser User-Agent before declaring the key dead (see pitfall below)
- **429 + `insufficient_quota`** → key valid but account has no billing (common for OpenAI `sk-proj-`). Store it anyway in `.env`; it activates when balance appears. Hermes skips it on 429, so it never breaks rotation.
- **429 rate-limit** → key works, burst-limited (see Step 4)
- **Gemini 404** → model name retired for v1beta (e.g. `gemini-2.5-flash` gone by late 2026) — retry with a current name (`gemini-2.0-flash` still resolves); 404 ≠ dead key. Then a 429 quota-exceeded = valid key, free quota exhausted.
- Note: `hermes auth list` statuses (`auth failed (401)`, `rate-limited`) can be STALE — a live probe is the only truth (7 nvidia keys shown as failed in auth list all returned 200).

## Step 3 — Add to pool (Hermes)

```bash
hermes auth add <provider> --type api-key --api-key "$KEY" --label "name-N"
hermes auth list
hermes auth status <provider>
hermes auth remove <provider> <index-or-label>   # positional arg, NOT --index
hermes auth reset <provider>                     # clear exhaustion after quota refresh
```

- Multiple keys per provider = **automatic rotation on 429**. Hermes marks exhausted creds `rate-limited (429) (Xm left)` and skips them until the reset window.
- Cross-provider fallback chain: `hermes fallback add` — **interactive picker only, no CLI flags**; `hermes fallback list`.
- `hermes auth add` accepts only registered model-provider ids (e.g. `opencode-zen`, `nvidia`, `openrouter`, `kilocode`, `anthropic`, `openai-codex`). There is **no `openai` or `custom` provider id** — OpenAI API keys go into `.env` as `OPENAI_API_KEY` instead.
- `opencode-zen` has aliases `opencode`, `opencode_zen`, `zen`; base `https://opencode.ai/zen/v1`.

## Step 4 — Capacity estimation (free tiers)

Per-key daily budgets (rough, mid-2026, verify by burst test): NVIDIA ~1000 req/day (~40 RPM — 429 on rapid fire, verified); OpenCode Zen ~1000+/day, softer limit (25 rapid calls OK); Groq ~14,400/day; Gemini ~1500/day per account; KiloCode aggregates free models (thousands/day). One continuously-running subagent ≈ 4–5k req/day, so 3 concurrent agents need ~15k req/day. **Burst test** to find RPM: fire 5–25 sequential `max_tokens:5` calls, count 429s.

## Pitfalls

- On Windows git-bash `python3` may be missing — use `python`.
- Never write actual API keys into skills or memory — only prefixes and patterns.
- A key that 200s on another provider's `/models` endpoint is not proof it works there (no-auth endpoints). Always test chat/completions.
- Batch-test keys against a candidate endpoint list with a short script (see references/provider-catalog.md) before touching `hermes auth` — it saves dozens of manual curls.

## Support files

- `references/provider-catalog.md` — provider endpoints, key prefixes, free-model lists, quota quirks.
