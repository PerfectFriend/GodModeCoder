# Hermes Desktop: Stack Overflow Reproduction & Recovery

## Error Signature

```
[hermes] [renderer console] RangeError: Maximum call stack size exceeded (file:///C:/Users/.../vendor-react-....js:8)
[hermes] [renderer console] [error-boundary:contrib:session-tile:SESSION_ID] RangeError: Maximum call stack size exceeded
```

## Root Cause Confirmed (This Session)

| Factor | Value |
|--------|-------|
| Session ID | `20260804_001755_b303b7` |
| Title | "Анализ кодовой базы ParanoidX и план Windows версии" |
| Message count | 177 |
| Last assistant message size | 81,221 chars |
| Trigger | Large final response written to file + massive tool_call history |
| Component | `session-tile` (session list item) |

## Reproduction Recipe

1. Accumulate 100+ messages in a session
2. Have final assistant message > 50KB (tool calls + large content)
3. Open session list in Hermes Desktop
4. React attempts to render `session-tile` for this session
5. Recursive render of message preview / tool call tree exceeds JS stack

## Recovery Commands (Executed & Verified)

```bash
# 1. Export session data (preserves everything)
hermes sessions export 20260804_001755_b303b7 --output ~/paranoidx-session-backup.jsonl

# 2. Delete from UI index (removes render target)
hermes sessions delete 20260804_001755_b303b7

# 3. Restart desktop
hermes desktop
```

**Result:** Desktop launches cleanly. Data preserved in `~/paranoidx-session-backup.jsonl`.

## Prevention Config Applied

```yaml
# ~/.hermes/config.yaml
session:
  auto_compress_threshold: 80
  compression_keep_recent: 15
display:
  max_message_preview_chars: 5000
```

## Log Locations (Windows)

```
C:\Users\<user>\AppData\Local\hermes\logs\desktop.log     # Renderer console
C:\Users\<user>\AppData\Local\hermes\logs\agent.log       # Main process
C:\Users\<user>\AppData\Local\hermes\logs\errors.log      # Aggregated
C:\Users\<user>\AppData\Local\hermes\state.db             # SQLite sessions
```

## SQL Verification Query

```sql
-- Find sessions likely to cause stack overflow
SELECT id, title, message_count, last_activity_at
FROM sessions
WHERE message_count > 100
ORDER BY message_count DESC;
```