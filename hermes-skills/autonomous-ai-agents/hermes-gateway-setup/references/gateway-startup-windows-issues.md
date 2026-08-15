# Hermes Gateway Startup Issues on Windows (2026-08-06)

## Problem: Gateway process not running after Windows restart

**Symptoms:**
- `hermes gateway status` shows `✗ No gateway process detected`
- Startup VBS script exists in `Startup\Hermes_Gateway.vbs` but process not found
- Earlier unclean shutdown: `WARNING gateway.lifecycle_ledger: Previous gateway life (pid=...) exited UNCLEANLY (no exit path ran — SIGKILL / OOM / VM death)`

**Root cause:** The startup VBS script runs the gateway but:
1. It may not wait for Python venv to be ready
2. If Python path changes (uv/python update), `VIRTUAL_ENV` in VBS becomes stale
3. Unclean shutdown leaves Telegram polling session open → conflict on restart

## Current startup VBS (`C:\Users\tomas\AppData\Local\hermes\gateway-service\Hermes_Gateway.vbs`)

```vbs
' Hermes Agent Gateway - Messaging Platform Integration
Option Explicit
Dim sh, env, existing_pp
Set sh = CreateObject("WScript.Shell")
Set env = sh.Environment("PROCESS")

env.Item("HERMES_HOME") = "C:\Users\tomas\AppData\Local\hermes"
env.Item("PYTHONIOENCODING") = "utf-8"
env.Item("HERMES_GATEWAY_DETACHED") = "1"
env.Item("VIRTUAL_ENV") = "C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv"
existing_pp = env.Item("PYTHONPATH")
If Len(existing_pp) > 0 Then
  env.Item("PYTHONPATH") = "C:\Users\tomas\AppData\Local\hermes\hermes-agent;" & existing_pp
Else
  env.Item("PYTHONPATH") = "C:\Users\tomas\AppData\Local\hermes\hermes-agent"
End If
sh.CurrentDirectory = "C:\Users\tomas\AppData\Local\hermes"
sh.Run "C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe -m hermes_cli.main gateway run", 0, False
```

## Issues with this approach
1. **Hardcoded `VIRTUAL_ENV`** — breaks if venv path changes
2. **No health check** — starts and forgets, no verification it stayed up
3. **No restart logic** — if process dies, no auto-restart
4. **Telegram polling conflict** — if unclean shutdown, Telegram holds previous session for ~1-2 minutes

## Working manual start (this session)
```cmd
cmd /c "cd /d C:\Users\tomas\AppData\Local\hermes && C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe -m hermes_cli.main gateway run"
```
Ran in background with `notify_on_complete=true` — process `proc_b0380abb8b8c` stayed up.

## Recommended improvements

### 1. Use `hermes gateway install` (official)
Creates a Scheduled Task with proper environment, runs at login with highest privileges.

### 2. Add health check / restart wrapper
Create a wrapper batch that:
- Verifies venv exists
- Starts gateway
- Polls `hermes gateway status` or checks PID
- Restarts on failure with backoff
- Waits for Telegram polling conflict to resolve

### 3. Use webhook mode to avoid polling conflict
Set `TELEGRAM_WEBHOOK_URL` in `.env` (requires public HTTPS endpoint) — avoids `getUpdates` conflict entirely.

### 4. Update VBS to be more robust
- Resolve `HERMES_HOME` dynamically (read from registry or known location)
- Read `VIRTUAL_ENV` from a config file instead of hardcoding
- Log output to `logs/gateway-startup.log` for debugging

## Session-specific findings

### Telegram polling conflict
```
WARNING hermes_plugins.telegram_platform.adapter: [Telegram] Telegram polling conflict (1/5) — previous session still held open on Telegram's servers. Waiting 20s for it to expire. Error: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running
```
- Happens when gateway restarts < 2 min after unclean shutdown
- Auto-resolves after ~100s (5 × 20s wait)
- **Fix:** Wait before manual restart, or use webhook mode

### NVIDIA API 503 errors during gateway run
```
WARNING agent.conversation_loop: API call failed ... HTTP 503: ResourceExhausted: Worker local total request limit reached (32/32)
```
- Gateway's internal cron jobs (e.g., `trashclean`) hit NVIDIA rate limit
- Not a gateway startup issue, but visible in gateway logs
- **Fix:** Add API key rotation / pool for NVIDIA provider

### Trashclean script path errors
```
can't open file 'C:\\\\Users\\\\tomas\\\\Userstomastrashclean.py'
can't open file 'C:\\\\c\\\\Users\\\\tomas\\\\.hermes\\\\skills\\\\trashclean\\\\scripts\\\\tr'
```
- Path concatenation bug in trashclean skill
- Not blocking gateway, but pollutes logs

## Verification checklist after restart
- [ ] `hermes gateway status` → `✓ Gateway is running (PID: ...)`
- [ ] `logs/gateway.log` → `✓ telegram connected`, `Gateway running with 1 platform(s)`, `set_my_commands OK`
- [ ] Bot responds to `/start` in Telegram
- [ ] Cron deliveries work (check `TELEGRAM_HOME_CHANNEL` delivery)