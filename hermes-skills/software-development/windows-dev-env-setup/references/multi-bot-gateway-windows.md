# Multi-Bot Telegram Gateway Setup on Windows

## Overview

Running multiple isolated Telegram bot gateways for Hermes Agent on Windows requires careful isolation to prevent polling conflicts and resource contention. This reference documents the complete setup for running 15+ bots simultaneously.

## Architecture

Each bot gets its own:
- **Process** - Independent `python -m hermes_cli.main gateway run`
- **Configuration** - Separate `.env` file with unique `TELEGRAM_BOT_TOKEN`
- **Database** - Separate SQLite file (`HERMES_DB_PATH`)
- **Logs** - Separate stdout/stderr via process isolation
- **Cron** - Only ONE bot has `CRON_ENABLED=true`

## Directory Structure

```
C:\Users\<user>\AppData\Local\hermes\gateways\
├── template/
│   ├── .env.template
│   ├── Hermes_Gateway.cmd
│   └── Hermes_Gateway.vbs
├── Cathedral/          # Main bot (CRON_ENABLED=true)
├── Torquemada/
├── Nexus/
├── ...
├── SuperGuard/         # Alarm bot (CRON_ENABLED=false)
├── register_tasks.ps1  # Registers all as Scheduled Tasks
└── README.md
```

## Key Configuration Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | From @BotFather | ✅ |
| `TELEGRAM_ALLOWED_USERS` | Comma-separated user IDs | ✅ |
| `TELEGRAM_HOME_CHANNEL` | Default chat for cron | ⭕ |
| `TELEGRAM_HOME_CHANNEL_THREAD_ID` | Forum topic ID | ⭕ |
| `HERMES_DB_PATH` | Separate SQLite per bot | ✅ |
| `CRON_ENABLED` | `true` only for ONE bot | ✅ |
| `DOTENV_PATH` | Path to bot's .env (set by launcher) | ✅ |

## Launcher Files

### Hermes_Gateway.cmd (per bot)
```cmd
@echo off
cd /d C:\Users\<user>\AppData\Local\hermes
set "HERMES_HOME=C:\Users\<user>\AppData\Local\hermes"
set "DOTENV_PATH=C:\Users\<user>\AppData\Local\hermes\gateways\<bot-dir>\.env"
set "PYTHONIOENCODING=utf-8"
set "HERMES_GATEWAY_DETACHED=1"
set "VIRTUAL_ENV=C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv"
set "PYTHONPATH=C:\Users\<user>\AppData\Local\hermes\hermes-agent;%PYTHONPATH%"
C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe -m hermes_cli.main gateway run
```

### Hermes_Gateway.vbs (hidden launcher)
```vbs
Option Explicit
Dim sh, env, existing_pp, target, dotenv
target = "C:\Users\<user>\AppData\Local\hermes\gateways\<bot-dir>\Hermes_Gateway.cmd"
dotenv = "C:\Users\<user>\AppData\Local\hermes\gateways\<bot-dir>\.env"
Set sh = CreateObject("WScript.Shell")
Set env = sh.Environment("PROCESS")
env.Item("HERMES_HOME") = "C:\Users\<user>\AppData\Local\hermes"
env.Item("DOTENV_PATH") = dotenv
env.Item("PYTHONIOENCODING") = "utf-8"
env.Item("HERMES_GATEWAY_DETACHED") = "1"
env.Item("VIRTUAL_ENV") = "C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv"
existing_pp = env.Item("PYTHONPATH")
If Len(existing_pp) > 0 Then
  env.Item("PYTHONPATH") = "C:\Users\<user>\AppData\Local\hermes\hermes-agent;" & existing_pp
Else
  env.Item("PYTHONPATH") = "C:\Users\<user>\AppData\Local\hermes\hermes-agent"
End If
sh.CurrentDirectory = "C:\Users\<user>\AppData\Local\hermes"
sh.Run "wscript.exe //B " & target, 0, False
```

## Scheduled Task Registration

Run as Administrator:
```powershell
powershell -ExecutionPolicy Bypass -File gateways\register_tasks.ps1
```

This creates tasks named `Hermes-Gateway-<BotName>` with:
- Trigger: At startup
- Action: Run VBS launcher (hidden window)
- Restart: 3 attempts, 2 min interval
- User: Interactive, Highest privileges

## Management Commands

```powershell
# Status
Get-ScheduledTask -TaskName "Hermes-Gateway-*"

# Start/Stop/Restart
Start-ScheduledTask -TaskName "Hermes-Gateway-Cathedral"
Stop-ScheduledTask -TaskName "Hermes-Gateway-SuperGuard"
Restart-ScheduledTask -TaskName "Hermes-Gateway-Cathedral"

# Check gateway status
hermes gateway status

# Unregister all
powershell -ExecutionPolicy Bypass -File gateways\register_tasks.ps1 -Unregister
```

## Resource Usage (Measured)

| Bots | Working Set | Private Memory | Virtual Space |
|------|-------------|----------------|---------------|
| 1 active | ~39 MB | ~215 MB | ~4.5 GB |
| 15 projected | ~291 MB | ~1.6 GB | ~65 GB |

**Note**: Virtual space is reserved address space, not physical RAM. On 24 GB system, 15 bots use ~8% RAM.

## Adding a New Bot

```powershell
# 1. Copy template
cp -r gateways/template gateways/<bot-name>

# 2. Edit .env with real token
notepad gateways\<bot-name>\.env

# 3. Update paths in .cmd and .vbs (replace <bot-name>)
notepad gateways\<bot-name>\Hermes_Gateway.cmd
notepad gateways\<bot-name>\Hermes_Gateway.vbs

# 4. Add to register_tasks.ps1 $gateways array
# 5. Register (as Administrator)
powershell -ExecutionPolicy Bypass -File gateways\register_tasks.ps1

# 6. Start
Start-ScheduledTask -TaskName "Hermes-Gateway-<bot-name>"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Conflict: terminated by other getUpdates` | Only ONE process per token. Kill duplicates in Task Manager. |
| Bot doesn't respond | Check `TELEGRAM_ALLOWED_USERS` includes your ID. Check Task is Running. |
| Cron not firing | Only enable `CRON_ENABLED=true` in ONE bot (main). |
| DB locked | Each bot has own DB path. Don't share `HERMES_DB_PATH`. |
| Skills not loading | Skills are shared (code), but each bot has own config/state. |

## Sending Test Messages

```bash
# Via main gateway
hermes send -t telegram "Test message"

# Or with file
echo "Test message" > test.txt
hermes send -t telegram -f test.txt

# List available targets
hermes send --list telegram
```

## Common Pitfalls

1. **Token masking** - Files show `***` but real tokens must be in `.env`
2. **Multiple processes same token** - Causes 409 Conflict, kills callbacks
3. **Cron on multiple bots** - Duplicate deliveries, only enable on main
4. **Shared DB path** - Causes locking, each bot needs unique `HERMES_DB_PATH`
4. **Windows path encoding** - Use `C:\\Users\\...` in .cmd/.vbs, not `/c/Users/...`