---
name: hermes-multi-bot-gateway
description: Run isolated Telegram bot gateways for Hermes on Windows.
category: hermes-agent
tags: [hermes, gateway, telegram, multi-bot, windows, scheduled-tasks]
---

# Hermes Multi-Bot Gateway Setup

## Trigger
Use when you need to run multiple isolated Telegram bot gateways for Hermes Agent on the same machine without conflicts. Each bot gets its own token, database, cron settings, and allowed users.

## Prerequisites
- Windows with Hermes Agent installed
- Python venv at `C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv`
- Telegram bot tokens from @BotFather

## Structure Created
```
gateways/
├── template/           # Template for new bots
│   ├── .env.template
│   ├── Hermes_Gateway.cmd
│   └── Hermes_Gateway.vbs
├── main/               # Primary bot (personal)
│   ├── .env
│   ├── Hermes_Gateway.cmd
│   ├── Hermes_Gateway.vbs
│   └── hermes.db       # Auto-created
├── superguard/         # SuperGuard alarm bot
│   ├── .env
│   ├── Hermes_Gateway.cmd
│   ├── Hermes_Gateway.vbs
│   └── hermes.db       # Auto-created
├── register_tasks.ps1  # Register all as Scheduled Tasks (run as Admin)
└── README.md           # Documentation
```

## Isolation Guarantees

| Resource | Isolation |
|----------|-----------|
| **Telegram token** | Separate `.env` per bot |
| **Database** | Separate `HERMES_DB_PATH` (SQLite) |
| **Cron jobs** | `CRON_ENABLED=false` in secondary bots |
| **Logs** | Separate process = separate stdout/stderr |
| **Allowed users** | Per-bot `TELEGRAM_ALLOWED_USERS` |
| **Home channel** | Per-bot `TELEGRAM_HOME_CHANNEL` |

## Adding a New Bot (3 steps)

```powershell
# 1. Copy template
cp -r gateways/template gateways/<bot-name>

# 2. Edit .env with bot token
notepad gateways/<bot-name>\.env

# 3. Update paths in .cmd and .vbs (replace <bot-name>)
notepad gateways/<bot-name>\Hermes_Gateway.cmd
notepad gateways/<bot-name>\Hermes_Gateway.vbs

# 4. Add to register_tasks.ps1 $gateways array (optional)
# 5. Register (run as Administrator)
powershell -ExecutionPolicy Bypass -File gateways\register_tasks.ps1

# 6. Start
Start-ScheduledTask -TaskName "Hermes-Gateway-<bot-name>"
```

## Key Configuration Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | From @BotFather | ✅ |
| `TELEGRAM_ALLOWED_USERS` | Comma-separated user IDs | ✅ |
| `TELEGRAM_HOME_CHANNEL` | Default chat for cron | ⭕ |
| `TELEGRAM_HOME_CHANNEL_THREAD_ID` | Forum topic ID | ⭕ |
| `TELEGRAM_CLEANUP_CHAT_ID` | For trashclean skill | ⭕ |
| `HERMES_DB_PATH` | Separate SQLite per bot | ✅ |
| `CRON_ENABLED` | `true` only for ONE bot | ✅ |
| `NVIDIA_API_KEY` etc. | LLM providers (can inherit) | ⭕ |

## Management Commands

```powershell
# Status
Get-ScheduledTask -TaskName "Hermes-Gateway-*"

# Start/Stop/Restart
Start-ScheduledTask -TaskName "Hermes-Gateway-Main"
Stop-ScheduledTask -TaskName "Hermes-Gateway-SuperGuard"
Restart-ScheduledTask -TaskName "Hermes-Gateway-Main"

# Unregister all
powershell -ExecutionPolicy Bypass -File gateways\register_tasks.ps1 -Unregister
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Conflict: terminated by other getUpdates` | Only ONE process per token. Kill duplicates in Task Manager. |
| Bot doesn't respond | Check `TELEGRAM_ALLOWED_USERS` includes your ID. Check Task is Running. |
| Cron not firing | Only enable `CRON_ENABLED=true` in ONE bot (main). |
| DB locked | Each bot has own DB path. Don't share `HERMES_DB_PATH`. |
| Skills not loading | Skills are shared (code), but each bot has own config/state. |

## Files Created by This Skill

All files under `C:\Users\<user>\AppData\Local\hermes\gateways\`:
- `template/.env.template` — env template with all options documented
- `template/Hermes_Gateway.cmd` — launcher template
- `template/Hermes_Gateway.vbs` — hidden launcher template
- `main/.env` — main bot config (token, users, DB, cron enabled)
- `main/Hermes_Gateway.cmd` — main bot launcher
- `main/Hermes_Gateway.vbs` — main bot hidden launcher
- `superguard/.env` — SuperGuard bot config (token placeholder, cron disabled)
- `superguard/Hermes_Gateway.cmd` — SuperGuard launcher
- `superguard/Hermes_Gateway.vbs` — SuperGuard hidden launcher
- `register_tasks.ps1` — PowerShell script to register Scheduled Tasks
- `README.md` — full documentation