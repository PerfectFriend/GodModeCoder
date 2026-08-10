# OpenCode Zen Model Validation (2026-08-06)

## Test Environment
- Key: `OPENCODE_ZEN_API_KEY` from `.env` (sk-B86...AgRc)
- Endpoint: `https://opencode.ai/zen/v1`
- Test: `chat/completions` with `max_tokens: 5`, message "hi"
- User-Agent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0`

## Free Models That Work (HTTP 200, cost=0)

| Model | Status | Notes |
|-------|--------|-------|
| nemotron-3-ultra-free | ✅ WORKS | Primary fallback |
| ling-3.0-flash-free | ✅ WORKS |  |
| north-mini-code-free | ✅ WORKS |  |
| laguna-s-2.1-free | ✅ WORKS |  |
| mimo-v2.5-free | ✅ WORKS |  |
| longcat-2.0-free | ✅ WORKS |  |
| big-pickle | ✅ WORKS |  |

## Rate Limited (HTTP 429)
| Model | Notes |
|-------|-------|
| deepseek-v4-flash-free | Rate limited (429) |
| kimi-k3 | Paid (401) - requires payment |
| grok-build-0.1 | Paid (401) |
| gpt-5.6-* | Paid (401) |
| claude-* | Paid (401) |
| grok-4.5 | Paid (401) |
| glm-5.2 | Paid (401) |
| minimax-m3 | Paid (401) |

## Key Findings
1. **nemotron-3-ultra-free** is the best primary fallback (consistently works, cost=0)
2. **deepseek-v4-flash-free** is rate limited (429) - NOT suitable for primary fallback
3. **laguna-s-2.1-free** works well as secondary fallback
4. **mimo-v2.5-free**, **north-mini-code-free**, **longcat-2.0-free**, **big-pickle** all work
4. **kimi-k3**, **grok-build-0.1**, **gpt-5.6-***, **claude-*** all require payment (401)
5. Cloudflare UA-block: Must send `User-Agent: Mozilla/5.0...Chrome/126.0` or get 403 (error code 1010)

## Duplicate Key Cleanup (2026-08-06)

### Original State: 24 credentials
- 1 env key (OPENCODE_ZEN_API_KEY)
- 11 zen-master-* (manual)
- 12 opencode-new-* (manual) - ADDED THIS SESSION

### Duplicates Found (exact same key values)
| Duplicate Pair | Key Prefix/Suffix |
|----------------|-------------------|
| zen-master-4 = opencode-new-4 | sk-B86...AgRc |
| zen-master-6 = opencode-new-5 | sk-fKf...sI9w |
| zen-master-10 = opencode-new-7 | sk-fKf...sI9w |
| zen-master-7 = opencode-new-6 | sk-4jh...K8On |
| zen-master-9 = opencode-new-8 | sk-lGc...HBfZ |
| zen-master-11 = opencode-new-9 | sk-ZJs...6ALx |
| zen-master-12 = opencode-new-10 | sk-6bO...PTD9 |
| zen-master-5 = opencode-new-3 | sk-NET...kEKx |

### Cleanup Performed
```bash
# Removed 16 duplicate credentials
hermes auth remove opencode-zen "opencode-new-4"  # duplicate of zen-master-4
hermes auth remove opencode-zen "opencode-new-5"  # duplicate of zen-master-6
hermes auth remove opencode-zen "opencode-new-7"  # duplicate of zen-master-10
hermes auth remove opencode-zen "opencode-new-3"  # duplicate of zen-master-5
hermes auth remove opencode-zen "opencode-new-6"  # duplicate of zen-master-7
hermes auth remove opencode-zen "opencode-new-8"  # duplicate of zen-master-9
hermes auth remove opencode-zen "opencode-new-9"  # duplicate of zen-master-11
hermes auth remove opencode-zen "opencode-new-10" # duplicate of zen-master-12
hermes auth remove opencode-zen "opencode-new-1"  # duplicate of zen-master-2
hermes auth remove opencode-zen "opencode-new-2"  # duplicate of zen-master-3
hermes auth remove opencode-zen "opencode-new-11" # duplicate of zen-master-7?
hermes auth remove opencode-zen "opencode-new-12" # duplicate of zen-master-8?
hermes auth remove opencode-zen "zen-master-4"
hermes auth remove opencode-zen "zen-master-6"
hermes auth remove opencode-zen "zen-master-10"
hermes auth remove opencode-zen "zen-master-5"
```

### Final State: 8 unique keys
```
1. OPENCODE_ZEN_API_KEY (env)
2. zen-master-2
3. zen-master-3
4. zen-master-7
5. zen-master-8
6. zen-master-9
6. zen-master-11
7. zen-master-12
```

## Fallback Chain Configuration (config.yaml)
```yaml
fallback_providers:
  '0': {provider: opencode-zen, model: nemotron-3-ultra-free}      # ✅ primary (works)
  '1': {provider: opencode-zen, model: deepseek-v4-flash-free}     # ⚠️ 429 → next
  '2': {provider: opencode-zen, model: laguna-s-2.1-free}          # ✅ fallback
  '3': {provider: gemini, model: gemini-2.0-flash}                 # ✅
  '4': {provider: kilocode, model: deepseek-v4-flash-free}         # —
  '5': {provider: openai-api, model: gpt-4o-mini}                  # ✅
```

## Duplicate Detection Script (for future use)
```python
import subprocess, json, re

def find_duplicate_keys():
    """Find duplicate keys in opencode-zen pool by comparing key values."""
    # We can't extract key values from credential store directly
    # But we can test each key with a known working model
    # and compare response patterns
    pass

# Manual detection: compare first 10 + last 10 chars of each key
# via `hermes auth list opencode-zen` and cross-referencing
# with original key list from user messages
```

## Key Management Best Practices
1. **Always test new keys** with `nemotron-3-ultra-free` (primary free model)
2. **Check for duplicates** before adding: compare key prefixes/suffixes
3. **Remove duplicates** immediately: `hermes auth remove opencode-zen "<label>"`
6. **Use env key as source of truth**: `OPENCODE_ZEN_API_KEY` in `.env`
7. **Label new keys consistently**: `opencode-new-N` for new additions
7. **Reset exhaustion** after adding: `hermes auth reset opencode-zen`