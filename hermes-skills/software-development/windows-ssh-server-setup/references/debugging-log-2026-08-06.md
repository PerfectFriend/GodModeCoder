# Windows SSH Server Setup - Debugging & Troubleshooting Log

## Session: 2026-08-06 (this session)

### Problem: SSH key auth fails for admin user with "Server accepts key" then "Permission denied"

**Environment:** Windows 11, OpenSSH Preview 10.0, git-bash/MSYS terminal

**Timeline:**
1. Installed `Microsoft.OpenSSH.Preview` via winget
2. Generated host keys with `ssh-keygen -A`
3. Fixed host key permissions with elevated `icacls`
4. Set `PasswordAuthentication yes` in sshd_config
5. Created `administrators_authorized_keys` with public key
6. Started sshd service
7. Key auth test: `ssh -i ~/.ssh/id_ed25519 tomas@localhost` → "Server accepts key" but then "Permission denied"

**Root cause:** `administrators_authorized_keys` file had:
- CRLF line endings (from PowerShell `Out-File`/`Set-Content`)
- BOM (UTF-8 BOM from PowerShell)
- Extra whitespace lines

**Fix:** Used elevated batch file with simple `echo` redirection:
```bat
@echo off
echo ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP8t5XQD4SOBiXtz38H0UT54dCW2GOUMrwp3oLxMOv+p tomas@INQUIZITOR > C:\ProgramData\ssh\administrators_authorized_keys
```

**Alternative fix:** Comment out `Match Group administrators` block in sshd_config so admins use their user `~/.ssh/authorized_keys` instead.

### Problem: Microsoft Account user (tomas) cannot use password auth

**Cause:** Microsoft Account users have no local password. `net user tomas` shows "Password required: No".

**Solution:** Use key-based auth only, or create a local user with password.

### Problem: Gateway process not running

**Cause:** Startup VBS script points to `C:\Users\tomas\AppData\Local\hermes\gateway-service\Hermes_Gateway.vbs` but the process wasn't running (unclean shutdown earlier).

**Fix:** Started gateway manually:
```cmd
cmd /c "cd /d C:\Users\tomas\AppData\Local\hermes && C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe -m hermes_cli.main gateway run"
```
Running in background as `proc_b0380abb8b8c`. Telegram polling conflict resolved after ~2 minutes.

### Commands that worked (elevated)

```cmd
# Install
winget install Microsoft.OpenSSH.Preview

# Host keys
C:\Program Files\OpenSSH\ssh-keygen.exe -A

# Permissions (elevated)
icacls C:\ProgramData\ssh\ssh_host_* /reset

# Config edit (elevated batch)
# See fix_sshd_config.bat in session

# Service
sc start sshd
sc query sshd

# Firewall
netsh advfirewall firewall add rule name="OpenSSH Server" dir=in action=allow protocol=TCP localport=22

# User creation (elevated)
net user Администратор /active:yes
net user Администратор TempPass123!
```

### Key insight: Elevated batch files for file writes to ProgramData

PowerShell redirection (`>`, `Out-File`, `Set-Content`) mangles `administrators_authorized_keys` with CRLF/BOM. Simple `cmd /c echo ... > file` from elevated context works cleanly.

### Files created this session
- `C:\Users\tomas\fix_sshd_config.bat` — comments out Match block
- `C:\Users\tomas\fix_auth_keys.bat` — writes administrators_authorized_keys correctly
- `C:\Users\tomas\fix_match_block.bat` / `fix_match_block2.bat` — attempts