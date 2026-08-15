# NSSM Service Configuration for SuperGuard Alarm

## Service Creation (setup_autostart.ps1)

```powershell
nssm install SuperGuardAlarm "C:\SuperGuard\venv\Scripts\python.exe" "C:\SuperGuard\panic_mode.py"
nssm set SuperGuardAlarm AppDirectory "C:\SuperGuard"
nssm set SuperGuardAlarm AppStdout "C:\SuperGuard\superguard.log"
nssm set SuperGuardAlarm AppStderr "C:\SuperGuard\superguard_err.log"
nssm set SuperGuardAlarm Start SERVICE_AUTO_START
nssm set SuperGuardAlarm Description "SuperGuard Alarm - AI video surveillance + Telegram bot + Tuya plug"
```

## Recovery Configuration

```powershell
# Restart on any exit code
nssm set SuperGuardAlarm AppExit Default Restart

# Throttle: minimum 10 seconds between restarts
nssm set SuperGuardAlarm AppThrottle 10000

# Delay before restart: 5 seconds
nssm set SuperGuardAlarm AppRestartDelay 5000
```

## Run As LocalSystem

```powershell
nssm set SuperGuardAlarm ObjectName "LocalSystem"
```

LocalSystem has network access (unlike default LocalService).

## Log Files

- **stdout**: `C:\SuperGuard\superguard.log`
- **stderr**: `C:\SuperGuard\superguard_err.log`

Rotated by NSSM automatically.

## Verification Commands

```powershell
# Check service status
Get-Service SuperGuardAlarm

# View recent logs
Get-Content C:\SuperGuard\superguard.log -Tail 50
Get-Content C:\SuperGuard\superguard_err.log -Tail 50

# Check service config
nssm get SuperGuardAlarm Application
nssm get SuperGuardAlarm AppDirectory
nssm get SuperGuardAlarm Start
nssm get SuperGuardAlarm ObjectName
```

## Firewall Rules (Port 6668 for Tuya Plug)

```powershell
New-NetFirewallRule -DisplayName "SuperGuard Tuya Plug Out" -Direction Outbound -Protocol TCP -LocalPort 6668 -Action Allow
New-NetFirewallRule -DisplayName "SuperGuard Tuya Plug In"  -Direction Inbound  -Protocol TCP -LocalPort 6668 -Action Allow
```

## Manual Service Control

```powershell
# Start
Start-Service SuperGuardAlarm

# Stop
Stop-Service SuperGuardAlarm -Force

# Restart
Restart-Service SuperGuardAlarm

# Remove service (if needed)
nssm remove SuperGuardAlarm confirm
```

## Requirements

- **Run as Administrator** — required for service creation
- **NSSM installed** — auto-downloaded to `C:\Program Files\NSSM\nssm.exe`
- **Python venv** — `C:\SuperGuard\venv\Scripts\python.exe` with all dependencies
- **sguard.env** — must exist with valid credentials

## Troubleshooting

| Issue | Check |
|-------|-------|
| Service won't start | `superguard_err.log` for Python import errors |
| Bot not responding | `superguard.log` for Telegram connection errors |
| Plug not switching | Verify Tuya credentials in `sguard.env` |
| Camera not loading | Check `superguard.log` for OpenCV connection errors |