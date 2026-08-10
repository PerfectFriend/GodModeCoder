---
name: trashclean
description: "Auto-delete spam in Telegram groups via Bot API cron job."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [telegram, moderation, spam, cleanup, bot-api, cron]
---

# TrashClean — Telegram Spam Cleaner

Automatically deletes messages matching spam/flood patterns in a Telegram group using the Bot API.

## Trigger

User wants to auto-moderate a Telegram group: "delete spam in group", "auto-clean flood messages", "настрой автоудаление мусора в группе".

## Configuration (in .env)

```bash
# Required
TELEGRAM_BOT_TOKEN=<from @BotFather>       # Bot must be admin in the group with "Delete messages" permission
TELEGRAM_CLEANUP_CHAT_ID=<group chat id>   # Numeric ID of the group (e.g. -1001234567890)

# Optional patterns (regex, one per line, | separated)
# Default patterns catch: repeated chars, caps lock, links without text, common spam phrases
TELEGRAM_CLEANUP_PATTERNS="\
(.)\\1{4,}|\
[A-ZА-Я]{10,}|\
https?://\\S+|\
(купи|продам|заработ|крипт|биткоин|казино|ставки|лотерея|выигрыш|бонус|промокод|скидка|акция).{0,3}\\d|\
^\\s*[💰💵💎🚀🔥⚡️✨🎁💸🤑]{3,}\\s*$"

# Optional: max message age to check (seconds, default 300 = 5 min)
TELEGRAM_CLEANUP_MAX_AGE=300

# Optional: dry run (log only, don't delete) — "true" or "false"
TELEGRAM_CLEANUP_DRY_RUN=false
```

## How it works

1. Reads config from `.env` (Hermes home)
2. Calls `getUpdates` with offset to fetch new messages since last run
3. For each message in the target chat:
   - Skips if older than `TELEGRAM_CLEANUP_MAX_AGE`
   - Tests message text against compiled regex patterns
   - If match: calls `deleteMessage` (or logs in dry-run)
4. Saves last processed `update_id` to state file for resume

## Usage

### One-shot test (dry-run)
```bash
hermes chat -q "Run trashclean in dry-run mode on the Telegram group" --skills trashclean
```

### Scheduled (recommended)
```bash
# Every 30 seconds
hermes cron create --name trashclean --schedule "30s" --prompt "Run trashclean on the Telegram group" --skills trashclean
```

## Files

- `scripts/trashclean.py` — main script (called by cron)
- `state/last_update_id.txt` — persisted offset (auto-created)

## Requirements

- Bot must be **admin** in the group with **"Delete messages"** permission
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CLEANUP_CHAT_ID` in `.env`
- Python with `requests` (stdlib `urllib` used — no deps)