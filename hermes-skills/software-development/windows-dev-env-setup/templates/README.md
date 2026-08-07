# =============================================================================
# README: Multi-Bot Gateway Structure
# =============================================================================

## Structure
```
gateways/
├── template/           # Template for new bots
│   ├── .env.template
│   ├── Hermes_Gateway.cmd
│   └── Hermes_Gateway.vbs
├── Cathedral/          # Primary bot (personal)
│   ├── .env
│   ├── Hermes_Gateway.cmd
│   ├── Hermes_Gateway.vbs
│   └── hermes.db       # Auto-created
├── SuperGuard/         # SuperGuard alarm bot
│   ├── .env
│   ├── Hermes_Gateway.cmd
│   ├── Hermes_Gateway.vbs
│   └── hermes.db       # Auto-created
├── register_tasks.ps1  # Register all as Scheduled Tasks (run as Admin)
└── README.md           # This file
```

## Adding a New Bot

```powershell
# 1. Copy template
cp -r gateways/template gateways/<bot-name>

# 2. Edit .env with bot token
notepad gateways/<bot-name>\.env

# 3. Update paths in .cmd and .vbs (replace <bot-name>)
notepad gateways/<bot-name>\Hermes_Gateway.cmd
notepad gateways/<bot-name>\Hermes_Gateway.vbs

# 4. Add to register_tasks.ps1 (optional - or run manually)
# Edit register_tasks.ps1 and add entry to $gateways array

# 5. Register (run as Administrator)
powershell -ExecutionPolicy Bypass -File gateways\register_tasks.ps1

# 6. Start
Start-ScheduledTask -TaskName "Hermes-Gateway-<bot-name>"
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

## Current Bots

| Bot | Task Name | Token | Cron | DB |
|-----|-----------|-------|------|-----|
| Main | `Hermes-Gateway-Main` | `8883516682:...` | ✅ | `gateways\main\hermes.db` |
| SuperGuard | `Hermes-Gateway-SuperGuard` | *from sguard.env* | ❌ | `gateways\superguard\hermes.db` |

## Management Commands

```powershell
# Status
Get-ScheduledTask -TaskName "Hermes-Gateway-*"

# Start
Start-ScheduledTask -TaskName "Hermes-Gateway-Main"
Start-ScheduledTask -TaskName "Hermes-Gateway-SuperGuard"

# Stop
Stop-ScheduledTask -TaskName "Hermes-Gateway-Main"

# Restart
Restart-ScheduledTask -TaskName "Hermes-Gateway-Main"

# Unregister all
powershell -ExecutionPolicy Bypass -File gateways\register_tasks.ps1 -Unregister
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Conflict: terminated by other getUpdates` | Only ONE process per token. Check Task Manager for duplicates. |
| Bot doesn't respond | Check `TELEGRAM_ALLOWED_USERS` includes your ID. Check Task is Running. |
| Cron not firing | Only enable `CRON_ENABLED=true` in ONE bot (main). |
| DB locked | Each bot has own DB path. Don't share `HERMES_DB_PATH`. |
| Skills not loading | Skills are shared (code), but each bot has own config/state. |