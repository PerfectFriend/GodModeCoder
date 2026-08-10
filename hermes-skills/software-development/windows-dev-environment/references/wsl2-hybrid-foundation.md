# WSL2 Hybrid Foundation for ParanoidX

## Overview
This document describes the **WSL2 Hybrid** deployment pattern for ParanoidX on Windows:
- **Go server** runs in WSL2 (Ubuntu 24.04) with full Linux environment
- **Flutter apps** (The-Isle, Royal-Isle) run natively on Windows
- **Shared data** via bind mount: `C:\ParanoidX-data` ↔ `/mnt/c/ParanoidX-data`
- **Docker services** (SMP, XFTP, coturn) run in WSL2 Docker Desktop integration

## Why Hybrid?
| Approach | Pros | Cons |
|----------|------|------|
| **Hybrid WSL2 + Native Flutter** | Go server works unchanged; Flutter native performance; Docker just works | Two environments to manage |
| **Full Native Windows** | Single environment | Go code changes needed (paths, signals, services); Docker Desktop still needed; Tor/xray binaries |
| **WSL2 Only** | Single Linux env | Flutter Windows builds don't work in WSL2; no native UI integration |

**Recommendation**: Hybrid for development/production; Full Native for distribution (MSIX/Inno Setup)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WINDOWS HOST                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │  The-Isle.exe    │  │  Royal-Isle.exe  │  │ Docker       │   │
│  │  (Flutter Win)   │  │  (Flutter Win)   │  │ Desktop      │   │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘   │
│           │                     │                     │          │
│           ▼                     ▼                     ▼          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              C:\ParanoidX-data (shared)                     │  │
│  │  backups/  logs/  radio/  dc/  config/                      │  │
│  └────────────────────────────┬────────────────────────────────┘  │
│                               │                                   │
│              ┌────────────────┴────────────────┐                  │
│              │  Bind Mount (WSL2 automount)    │                  │
│              └────────────────┬────────────────┘                  │
└───────────────────────────────│───────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        WSL2 (Ubuntu 24.04)                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │  ParanoidX       │  │  Docker Compose  │  │  Systemd     │   │
│  │  (Go Server)     │  │  SMP, XFTP,      │  │  (enabled)   │   │
│  │  -data /mnt/c/   │  │  coturn          │  │              │   │
│  │  ParanoidX-data  │  │                  │  │              │   │
│  └──────────────────┘  └──────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites
- Windows 10/11 Pro/Enterprise (WSL2 requires Pro+)
- Admin rights for initial setup
- 16GB+ RAM recommended (WSL2 + Docker + Go + Flutter)
- x64 CPU (WSL2 requirement)

## Setup Scripts (in `templates/`)

| Script | Purpose | Run As |
|--------|---------|--------|
| `setup-wsl2-hybrid.ps1` | Full WSL2 + Ubuntu + repos + Go build | **Admin** |
| `build-windows-flutter.ps1` | Build Flutter apps + Go server for Windows | User |
| `launch-hybrid.ps1` | Launch full stack (Docker + Go + Flutter apps) | User |

## Step-by-Step Setup

### 1. Run Setup (Admin PowerShell)
```powershell
cd C:\Users\tomas
.\setup-wsl2-hybrid.ps1
```

This does:
- Enables WSL2 + Virtual Machine Platform
- Installs Ubuntu 24.04
- Configures `/etc/wsl.conf` (systemd, bind mount)
- Creates `C:\ParanoidX-data` with subdirs
- Clones 5 repos in WSL2: `~/ParanoidX`, `~/The-Isle`, `~/Royal-Isle`, `~/shared-libs`, `~/the-grimoire`
- Builds Go server in WSL2

### 2. Start Docker Desktop (Windows)
- Install Docker Desktop from docker.com
- Enable "Use WSL 2 based engine" in Settings → General
- Enable Ubuntu-24.04 integration in Settings → Resources → WSL Integration

### 3. Build Flutter Apps (User PowerShell)
```powershell
cd C:\Users\tomas
.\build-windows-flutter.ps1
```

This builds:
- `C:\Projects\ParanoidX\ParanoidX.exe` (Go server)
- `C:\Projects\dist\The-Isle\isle_app.exe` (Civilian app)
- `C:\Projects\dist\Royal-Isle\royal_app.exe` (Admin app)

### 4. Launch Full Stack (User PowerShell)
```powershell
cd C:\Users\tomas
.\launch-hybrid.ps1
```

This starts:
- WSL2 Docker Compose (SMP, XFTP, coturn)
- Go server in WSL2 (`-data /mnt/c/ParanoidX-data`)
- The-Isle native Windows app
- Royal-Isle native Windows app

## Data Flow

| Data | Location | Access |
|------|----------|--------|
| Go server DB, logs | `/mnt/c/ParanoidX-data` (WSL2) | WSL2 Go process |
| Flutter app settings | `C:\ParanoidX-data` (Windows) | Native Flutter apps |
| Backups | `C:\ParanoidX-data\backups` | Both |
| Radio cache | `C:\ParanoidX-data\radio` | Both |
| DC cloud data | `C:\ParanoidX-data\dc` | Both |

## Network

| Service | Port | Access |
|---------|------|--------|
| Go API | 8080 | `http://localhost:8080` (Windows) |
| Tor SOCKS | 9050 | localhost only |
| xray API | 10085 | localhost only |
| SMP/XFTP | Docker ports | localhost |
| coturn | 3478, 5349 | UDP/TCP |

## RunOnce Auto-Resume Limitations

**Problem**: The setup script uses `HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce` to auto-resume after reboot, but this has a critical limitation:

- **RunOnce only triggers when the SAME USER logs in interactively** (Windows Explorer shell start)
- **Admin PowerShell opened via Win+X does NOT trigger RunOnce** — the user must manually re-run the script
- The script reads the phase from RunOnce, but if the user doesn't run it again, the phase is lost

**Workaround**: After each reboot, user MUST:
1. Open **Admin PowerShell** (Win+X → Terminal Admin)
2. Navigate to script directory
3. Re-run the setup script — it will detect the RunOnce phase and continue

```powershell
cd C:\Users\tomas
powershell -ExecutionPolicy Bypass -File "C:\Users\tomas\setup-paranoidx-hybrid-full.ps1"
```

**Better approach for future**: Use a Scheduled Task with `RunLevel=Highest` and `Trigger=AtLogOn` (requires admin to create initially), or document the manual re-run requirement clearly.

## PowerShell from git-bash/MSYS Encoding Fix

**Problem**: Calling `powershell.exe` or `.ps1` scripts from git-bash/MSYS produces garbled UTF-16 output (mojibake).

**Root cause**: MSYS pipes handle PowerShell output incorrectly (UTF-16LE with BOM vs UTF-8 expectation).

**Solution**: Always run PowerShell scripts from a **native PowerShell terminal** (Admin or User), NOT from git-bash/MSYS terminal.

```bash
# WRONG - from git-bash
powershell.exe -ExecutionPolicy Bypass -File script.ps1

# CORRECT - from native PowerShell (Win+X → Terminal Admin)
powershell -ExecutionPolicy Bypass -File "C:\Users\tomas\script.ps1"
```

---

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

## Production Distribution

For distributing to end users, build **Full Native Windows** (see `references/paranoidx-go-windows-port.md`):
1. Apply Go code changes (path abstraction, signals, Windows Services)
2. Build Go: `GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -o ParanoidX.exe ./cmd/ParanoidX/`
3. Bundle `tor.exe` (Expert Bundle), `xray.exe`
4. Package with MSIX / Inno Setup / NSIS
5. Install as Windows Service via NSSM or `github.com/kardianos/service`

## Related Files

| File | Description |
|------|-------------|
| `templates/setup-wsl2-hybrid.ps1` | WSL2 + Ubuntu + repos + Go build |
| `templates/build-windows-flutter.ps1` | Flutter Windows builds + Go cross-compile |
| `templates/launch-hybrid.ps1` | Full stack launcher |
| `references/paranoidx-go-windows-port.md` | Full Native Windows port guide |
| `references/flutter-windows-build.md` | Flutter Windows build details |