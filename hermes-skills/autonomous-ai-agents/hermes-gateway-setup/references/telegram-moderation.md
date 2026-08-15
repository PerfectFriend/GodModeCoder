# Telegram Bot API Moderation (trashclean) — Deployment Notes

## Context
User wanted auto-deletion of spam/flood messages in a Telegram group where Hermes gateway is already running with a bot.

## Environment
- Hermes home: `C:\Users\tomas\AppData\Local\hermes`
- Gateway running with Telegram bot token
- Bot added to group with admin rights (Delete messages permission)

## Group ID Discovery
Found in gateway logs (`logs/gateway.log`):
```
WARNING ... [Telegram] Blocked unauthorized user 8863122561 in chat -1004431090317
INFO ... inbound message: platform=telegram chat=-1004431090317 ...
```
Group ID: **`-1004431090317`**

## .env Configuration
Added to `C:\Users\tomas\AppData\Local\hermes\.env`:
```bash
TELEGRAM_CLEANUP_CHAT_ID=-1004431090317
```

## Cron Job Setup
```bash
hermes cron create \
  --name trashclean \
  --schedule "every 1m" \
  --prompt "Run trashclean on the Telegram group" \
  --skills trashclean \
  --deliver local
```

Job ID: `f1923a54f2db`

## Key Learnings

### 1. TrashClean operates independently of gateway's `TELEGRAM_ALLOWED_USERS`
- Uses direct Bot API (`getUpdates` + `deleteMessage`)
- Sees **ALL** messages in the group, not just authorized users
- Gateway's allowlist only controls which messages reach the LLM agent

### 2. Long-polling conflict with gateway
- Both gateway and trashclean use `getUpdates` (long polling)
- Only one consumer gets each update — race condition
- **Current setup**: gateway runs continuously, trashclean runs via cron every 1 min
- **Risk**: gateway may consume updates before trashclean sees them
- **Solutions**:
  - Switch gateway to webhook mode (`TELEGRAM_WEBHOOK_URL`) — frees long polling for trashclean
  - Or stop gateway if pure moderation bot is needed
  - Or accept some missed messages (current trade-off)

### 3. First run behavior
- `getUpdates` with offset=0 returns only *new* updates after the call
- No historical messages retrieved — fine for forward-looking moderation

### 4. Dry-run mode for testing
Set `TELEGRAM_CLEANUP_DRY_RUN=true` to log matches without deleting.

### 5. Patterns used
Default patterns catch:
- Repeated characters (5+): `(.)\1{4,}`
- ALL CAPS (10+): `[A-ZА-Я]{10,}`
- Bare links: `https?://\S+`
- Spam keywords + numbers: `(купи|продам|заработ|крипт|биткоин|казино|ставки|лотерея|выигрыш|бонус|промокод|скидка|акция).{0,3}\d`
- Emoji spam: `^\s*[💰💵💎🚀🔥⚡️✨🎁💸🤑]{3,}\s*$`

## Log Evidence
Gateway logs showed unauthorized users (8863122561, 8640937344) posting in the group — their messages were blocked from reaching the LLM but visible in gateway logs. Trashclean would catch and delete these via direct API.

---

## Session 2026-08-04: 409 Conflict Resolution

### Problem Encountered
- Cron job `trashclean` (every 1m) was failing with "The read operation timed out" after 409 Conflict retries
- Multiple Hermes gateway processes were running and holding the bot's `getUpdates` long-poll connection
- The script's 30s timeout was shorter than Telegram's long-poll hold (30-60s), causing timeouts that looked like conflicts

### Solution Applied
1. Killed competing Hermes gateway processes (`taskkill /PID ...`)
2. Patched `scripts/trashclean.py`:
   - Increased `getUpdates` timeout from 30s to 65s
   - Added verbose logging for debugging
   - Improved 409 retry logic with better error reporting
3. Verified multiple consecutive successful runs

### Key Insight
**Only one process per bot token can call `getUpdates` at a time.** The Hermes gateway runs a webhook/polling loop that conflicts with the cron job's polling. Either:
- Run trashclean via the gateway (webhook mode), OR
- Ensure gateway is stopped when cron runs, OR
- Use separate bot tokens for different services

### Troubleshooting Checklist for 409 Conflict

**Symptom:** `getUpdates` returns 409 "Conflict: terminated by other getUpdates request" or times out

**Diagnosis:**
```bash
# Quick test - should return immediately with empty result if path is clear
curl "https://api.telegram.org/bot<TOKEN>/getUpdates?offset=-1&timeout=10&limit=1"
```

**Fixes (in order):**
1. **Stop Hermes gateway** if running: `taskkill /IM hermes.exe /F` (Windows) or `pkill hermes` (Linux)
2. **Pause competing cron jobs** using same bot token
3. **Check for webhook** blocking long polling:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   # If url is set, delete it:
   curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook?drop_pending_updates=true"
   ```
4. **Wait 30-60s** after stopping competing process for Telegram to release the connection
5. **Use longer timeout** in script (65s > Telegram's max long-poll hold)

### Script Fix Applied (trashclean.py)
```python
# In telegram_api() function:
timeout = 65 if method == "getUpdates" else 30  # Longer than Telegram's long-poll

# Added verbose logging:
print(f"Calling {method} (attempt {attempt + 1}/{max_retries}, timeout={timeout}s)...")
# On success:
print(f"{method} OK: {len(result.get('result', []))} updates")
# On 409:
print(f"409 Conflict on {method}: {result.get('description', 'unknown')}")
# On exception:
print(f"Exception on {method}: {e}")
```

### Verification
After fix, multiple consecutive runs succeeded:
- Run 1: Deleted 1 spam message (matched repeated-char pattern)
- Runs 2-5: "No new updates" cleanly
- State file (`state/last_update_id.txt`) persists offset correctly
- Cron job resumed and active

---

## Session 2026-08-06: Observed Conflict in Production

### Observation
During normal operation with Hermes gateway running (connected to Telegram) and trashclean cron job running every 1 minute, the gateway logs showed continuous "Telegram polling conflict" warnings at approximately 1-minute intervals, correlating with trashclean runs.

### Gateway Log Pattern
```
WARNING ... [Telegram] Telegram polling conflict (1/5) — previous session still held open on Telegram's servers. Waiting 20s for it to expire. Error: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running
INFO ... [Telegram] Telegram polling restarted after conflict retry 1/5; health pending getUpdates progress
```

### Impact Assessment
- **Gateway**: Experiences ~20s polling interruption every minute, auto-recovers
- **Trashclean**: May miss updates consumed by gateway during its brief polling window
- **Messages**: Some spam messages may slip through if gateway consumes the update before trashclean sees it

### Current Trade-off
Accepting the conflict because:
1. Gateway must stay running for LLM chat functionality
2. Webhook mode requires public HTTPS endpoint (not available in current setup)
3. Separate bot token would require re-adding bot to group and re-configuring
4. Current spam volume is low; missed messages are acceptable risk

### Recommended Production Architecture
For production deployments requiring reliable spam filtering:
1. **Integrate moderation into gateway pipeline** — Process every message in the gateway's message handler, before the allowlist check. Zero latency, no polling conflict.
2. **Or use webhook mode** — Deploy gateway to cloud (Fly.io, Railway) with public HTTPS, set `TELEGRAM_WEBHOOK_URL`, freeing `getUpdates` for dedicated moderation bot.
3. **Or run dedicated moderation bot** — Second bot token via @BotFather, added to group as admin, used exclusively for trashclean. Gateway and moderation bot operate on separate tokens.

### Implementation Pattern: Gateway-Integrated Moderation
```python
# In hermes_plugins/telegram_platform/adapter.py, in handle_update():
async def handle_update(self, update: Update):
    message = update.message or update.edited_message
    if message and message.chat.id == CLEANUP_CHAT_ID:
        if is_spam(message.text or message.caption or ""):
            await message.delete()
            logger.info(f"Deleted spam message {message.message_id}")
            return  # Don't process further
    # Continue normal gateway processing...
```
This approach eliminates the dual-polling architecture entirely.