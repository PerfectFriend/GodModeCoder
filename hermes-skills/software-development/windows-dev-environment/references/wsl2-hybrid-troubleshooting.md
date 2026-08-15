# WSL2 Hybrid Troubleshooting

## Encoding Issues with PowerShell from git-bash/MSYS

**Problem**: Calling `powershell.exe` or `.ps1` scripts from git-bash/MSYS produces garbled UTF-16 output (mojibake like `Р'РµСЂСЃРёСЏ` instead of `Версия`).

**Root cause**: MSYS pipes handle PowerShell output incorrectly (UTF-16LE with BOM vs UTF-8 expectation).

**Solution**: Always run PowerShell scripts from a **native PowerShell terminal** (Admin or User), NOT from git-bash/MSYS terminal.

```bash
# WRONG - from git-bash
powershell.exe -ExecutionPolicy Bypass -File script.ps1

# CORRECT - from native PowerShell (Win+X → Terminal Admin)
powershell -ExecutionPolicy Bypass -File "C:\Users\tomas\script.ps1"
```

## First-Run Ubuntu Interactive Setup

**Problem**: `wsl -d Ubuntu-24.04 bash -c "echo ready"` hangs indefinitely after fresh install.

**Root cause**: First Ubuntu launch requires interactive user creation (username/password). Root user doesn't exist yet.

**Solution**: User must open Ubuntu once manually:
1. Start Menu → "Ubuntu 24.04"
2. Enter username and password at prompts
3. Type `exit` after reaching bash prompt
4. Then script can proceed with root commands

**Script behavior**: Our setup script handles this by:
- Waiting up to 120s for `wsl -d Ubuntu-24.04 -u root bash -c "echo ready"` to succeed
- If timeout, user must manually run Ubuntu once
- After manual setup, script continues automatically

## RunOnce Auto-Resume After Reboot

**Mechanism**: Script registers itself in `HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce` with a phase value.

**Phases**:
- `init` → `install-wsl` (enables WSL features, installs Ubuntu, reboots if needed)
- `install-wsl` → `configure-wsl` (after first reboot, configures wsl.conf, reboots for systemd)
- `configure-wsl` → `clone-repos` (after second reboot, clones 5 repos)
- `clone-repos` → `build-go` (builds Go server)
- `build-go` → complete

**To trigger continuation**: Run the script again in **admin PowerShell** after each reboot. It reads the RunOnce value and continues from the correct phase.

```powershell
# After reboot, run in Admin PowerShell:
cd C:\Users\tomas
powershell -ExecutionPolicy Bypass -File "C:\Users\tomas\setup-paranoidx-hybrid-full.ps1"
```

## Admin Rights Required

**Problem**: Script exits with "Administrator rights required!" 

**Reason**: 
- `dism.exe /online /enable-feature` needs elevation
- `wsl --install` needs elevation
- RunOnce only works for current user (not SYSTEM), so user must run admin PowerShell manually after each reboot

**Solution**: Always use **Win+X → Terminal (Admin)** or **PowerShell (Admin)**.

## WSL Stuck / Timeout

**Symptoms**: `wsl -d Ubuntu-24.04` commands timeout, `vmmemWSL` process running but unresponsive.

**Diagnosis**:
```powershell
# Check WSL processes
Get-Process -Name '*wsl*','*ubuntu*','*vmmem*'

# Check if first-run is pending
wsl -d Ubuntu-24.04 -u root bash -c "echo ready"
# If hangs → first-run not done
```

**Fixes**:
1. `wsl --terminate Ubuntu-24.04` then retry
2. If still stuck → restart computer
3. If first-run pending → open Ubuntu from Start Menu manually

## Bind Mount Not Working

**Check**:
```bash
# In WSL2
cat /etc/wsl.conf
# Must have [automount] section with enabled=true, root=/mnt/

ls -la /mnt/c/ParanoidX-data
# Should show backups/ logs/ radio/ dc/ config/
```

**Fix**: Reboot WSL after wsl.conf change: `wsl --terminate Ubuntu-24.04` then restart from Windows.

## Docker in WSL2 Not Working

**Requirements**:
- Docker Desktop Settings → General → "Use WSL 2 based engine" ✓
- Settings → Resources → WSL Integration → Ubuntu-24.04 ✓
- Restart Docker Desktop after enabling

## Flutter Build Fails with Tor Proxy

**Problem**: `flutter pub get` hangs/fails when system has `HTTP_PROXY=socks5://127.0.0.1:9050` set.

**Fix**: Unset all proxy vars before Flutter commands:
```powershell
$env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""; $env:http_proxy = ""; 
$env:https_proxy = ""; $env:ALL_PROXY = ""; $env:all_proxy = ""
flutter pub get
flutter build windows --release
```

## Go Build Fails in WSL2

**Check**:
```bash
# In WSL2
cd ~/ParanoidX
go version
go mod tidy
go build -o ~/bin/ParanoidX ./cmd/ParanoidX/
```

**Common issues**:
- Missing dependencies → run `go mod tidy`
- Go version mismatch → check `go version` (needs 1.21+)
- Path issues → ensure GOPATH/GOMODCACHE set correctly

## Script Not Continuing After Reboot

**Check RunOnce**:
```powershell
Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce' -Name 'ParanoidX-WSL2-Setup' -ErrorAction SilentlyContinue
```

If empty → script already completed or never registered. Run script manually to restart.

## User Creation & Default User Issues

**Problem**: After fresh Ubuntu 24.04 install, only `root` user exists. Scripts running via `wsl -d Ubuntu-24.04` execute as root, so `$HOME` expands to `/root`, not the intended user's home directory. Git clones and Go builds end up in `/root/` instead of `/home/tomas/`.

**Root cause**: First-run interactive setup (username/password prompt) was skipped or not completed. The `root` user is the default until a regular user is created and set as default in `/etc/wsl.conf`.

**Fix - Create user and set as default**:
```powershell
# 1. Create user with sudo access
wsl -d Ubuntu-24.04 --user root bash -c '
  useradd -m -s /bin/bash -G sudo tomas
  echo "tomas:tomas" | chpasswd
  echo "tomas ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/tomas
  chmod 440 /etc/sudoers.d/tomas
'

# 2. Set default user in wsl.conf
wsl -d Ubuntu-24.04 --user root bash -c '
  cat > /etc/wsl.conf << "EOF"
[user]
default=tomas

[automount]
enabled = true
root = /mnt/
options = "metadata,uid=1000,gid=1000,umask=0022"

[network]
generateHosts = true
generateResolvConf = true

[boot]
systemd = true
EOF
'

# 3. Restart WSL to apply
wsl --terminate Ubuntu-24.04
Start-Sleep 3
# Now wsl -d Ubuntu-24.04 runs as 'tomas' user
```

## PowerShell Variable Escaping for Bash

**Problem**: PowerShell expands `$HOME` before passing to bash, causing git clone to target `C:\Users\tomas\ParanoidX` (Windows path) instead of bash's `$HOME` (`/home/tomas`).

**Root cause**: In PowerShell double-quoted strings, `$HOME` is a PowerShell variable (expands to Windows user profile). Bash never sees the literal `$HOME`.

**Fix**: Escape with backtick so PowerShell passes literal `$HOME` to bash:
```powershell
# WRONG - PowerShell expands $HOME
wsl -d Ubuntu-24.04 bash -c "git clone $url \$HOME/ParanoidX"

# CORRECT - backtick escapes $ so bash gets literal $HOME
wsl -d Ubuntu-24.04 bash -c "git clone $url `$HOME/ParanoidX"
```

Similarly for other bash variables: `` `$USER ``, `` `$PWD ``, etc.

## Running Commands as Non-Root User

**Problem**: `wsl -d Ubuntu-24.04` runs as the default user (root until changed). Operations like `git clone` should run as the regular user to put files in `/home/tomas/`.

**Fix**: After setting default user in wsl.conf and restarting WSL:
```powershell
# Verify current user
wsl -d Ubuntu-24.04 bash -c 'whoami'  # Should return 'tomas'

# Now commands run as tomas, $HOME = /home/tomas
wsl -d Ubuntu-24.04 bash -c "git clone $url `$HOME/ParanoidX"
wsl -d Ubuntu-24.04 bash -c "cd `$HOME/ParanoidX && go build -o ~/bin/ParanoidX ./cmd/ParanoidX/"
```

If you must run a specific command as root explicitly:
```powershell
wsl -d Ubuntu-24.04 --user root bash -c "apt update && apt install -y git"
```

## Updated Correct Workflow

1. **Admin PowerShell** (Win+X → Terminal Admin)
2. Run setup script: `.\\setup-paranoidx-hybrid-full.ps1`
3. If reboots happen → **open admin PowerShell again** and re-run same script
4. When Ubuntu first-run needed → **open Ubuntu from Start Menu**, create user, exit
5. **If user creation was skipped**: Run the user creation commands above (create user, update wsl.conf, restart WSL)
6. Re-run script in admin PowerShell
7. After "COMPLETE" → run `.\\launch-hybrid.ps1` (User PowerShell OK)
8. Parallel: run `.\\build-windows-flutter.ps1` (User PowerShell OK)