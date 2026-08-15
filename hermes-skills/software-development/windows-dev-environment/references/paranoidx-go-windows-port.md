# Go Server Windows Port for ParanoidX

## Required Code Changes for Native Windows

### 1. Path Abstraction Layer (`internal/config/paths.go`)
```go
package config

import (
	"os"
	"path/filepath"
	"runtime"
)

func DataDir() string {
	if runtime.GOOS == "windows" {
		// %LOCALAPPDATA%\ParanoidX
		return filepath.Join(os.Getenv("LOCALAPPDATA"), "ParanoidX")
	}
	// ~/.local/share/paranoidx
	return filepath.Join(os.Getenv("HOME"), ".local/share/paranoidx")
}

func ConfigPath() string {
	return filepath.Join(DataDir(), "paranoidx.json")
}

func USBBackupMountPoint() string {
	if runtime.GOOS == "windows" {
		// Scan drive letters E: through Z: for SIMPLEX-USB label
		for _, drive := range []string{"E:", "F:", "G:", "H:", "I:", "J:", "K:", "L:", "M:", "N:", "O:", "P:", "Q:", "R:", "S:", "T:", "U:", "V:", "W:", "X:", "Y:", "Z:"} {
			vol, _ := GetVolumeLabel(drive)
			if vol == "SIMPLEX-USB" || vol == "SIMPLEX-BACKUP" {
				return drive + "\\"
			}
		}
		return ""
	}
	return "/run/media/tomas/SIMPLEX-USB"
}

// GetVolumeLabel returns the volume label for a Windows drive letter
func GetVolumeLabel(drive string) (string, error) {
	// Use GetVolumeInformation from kernel32.dll via syscall
	// Implementation in paths_windows.go (build tag)
	return "", nil
}
```

### 2. Build Tags for Platform-Specific Files
- `paths.go` - common interface
- `paths_linux.go` - `//go:build linux` implementation
- `paths_windows.go` - `//go:build windows` implementation
- `paths_darwin.go` - `//go:build darwin` implementation

### 3. Replace Bash Commands with Cross-Platform Go
| Linux Pattern | Windows Equivalent |
|---------------|-------------------|
| `exec.Command("bash", "-c", script)` | `exec.Command("cmd", "/C", script)` or use Go stdlib |
| `exec.Command("docker", "compose", ...)` | Use Docker SDK (`github.com/docker/docker/client`) |
| `exec.Command("systemctl", ...)` | Windows Services API (`golang.org/x/sys/windows/svc/mgr`) |
| `exec.Command("apt-get", ...)` | Skip on Windows (package manager not available) |
| `exec.Command("journalctl", ...)` | Windows Event Log API |
| `exec.Command("snap", ...)` | Skip on Windows |
| `syscall.SIGTERM` / `syscall.SIGINT` | `os.Interrupt` (Ctrl+C), `os.Kill` |

### 4. Signal Handling (Windows Compatible)
```go
// main.go - replace syscall signals
sigCh := make(chan os.Signal, 1)
signal.Notify(sigCh, os.Interrupt, os.Kill)  // Works on Windows + Linux
// On Windows, os.Intercept = Ctrl+C, os.Kill = process termination
```

### 5. Cron Jobs - Use Go-based Scheduler Instead of Bash
Replace bash cron scripts with Go cron library (`github.com/robfig/cron/v3`):
- Disk cleanup cron → Go function with `runtime.GOOS` guards
- Backup cron → Go function, detect USB via `USBBackupMountPoint()`
- Docker health cron → Use Docker SDK instead of `docker compose` CLI

### 6. File Paths in main.go - Replace Hardcoded Paths
```go
// Before (line 207):
dataDir := flag.String("data", filepath.Join(os.Getenv("HOME"), ".local/share/paranoidx"), "data dir")

// After:
dataDir := flag.String("data", config.DataDir(), "data dir")

// Before (line 505):
usbDir := "/run/media/tomas/SIMPLEX-USB"

// After:
usbDir := config.USBBackupMountPoint()
if usbDir == "" {
    slog.Info("USB backup drive not found, skipping")
    continue
}
```

### 7. Docker Compose Directory (line 585)
```go
// Before:
dockerComposeDir := filepath.Join(os.Getenv("HOME"), "ParanoidX", "docker")

// After:
dockerComposeDir := filepath.Join(config.ProjectRoot(), "docker")
// where ProjectRoot() returns the repo root (configurable or auto-detected)
```

### 8. Backup Script Path (line 499, admin.go)
```go
// Before:
backupScript := filepath.Join(home, "ParanoidX/scripts/backup-to-usb.sh")

// After:
// Embed backup logic in Go, or call PowerShell script on Windows
```

## Build for Windows

```bash
# Cross-compile from Linux/macOS or build on Windows
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -ldflags="-X main.buildVersion=win-01" -o ParanoidX.exe ./cmd/ParanoidX/

# On Windows (git-bash):
$env:GOOS="windows"; $env:GOARCH="amd64"; $env:CGO_ENABLED="0"
go build -ldflags="-X main.buildVersion=win-01" -o ParanoidX.exe ./cmd/ParanoidX/
```

## Runtime Dependencies on Windows

| Component | Windows Binary | Source |
|-----------|----------------|--------|
| Tor | `tor.exe` (Expert Bundle) | https://www.torproject.org/download/tor/ |
| xray/V2Ray | `xray.exe` | https://github.com/XTLS/Xray-core/releases |
| coturn | Docker (WSL2) or native compile | Docker Desktop recommended |
| SMP/XFTP | Docker (WSL2) | Docker Desktop |
| SQLite | `modernc.org/sqlite` (pure Go, CGO-free) | Works natively |

## Windows Service Installation (NSSM)

```powershell
# Install as Windows Service
nssm install ParanoidX "C:\Path\ParanoidX.exe" "-data C:\Users\<user>\AppData\Local\ParanoidX"
nssm set ParanoidX Description "ParanoidX Sovereign Network Daemon"
nssm set ParanoidX AppDirectory "C:\Path\"
nssm set ParanoidX AppStdout "C:\Path\logs\ParanoidX-out.log"
nssm set ParanoidX AppStderr "C:\Path\logs\ParanoidX-err.log"
nssm start ParanoidX

# Or use native Go service: github.com/kardianos/service
```

## Distribution

1. **Zip**: `ParanoidX.exe` + `config/` + `docker/` + `scripts/` (PowerShell versions)
2. **MSIX**: Modern packaging, auto-update capable
3. **Inno Setup**: Classic installer with service registration

## Testing Checklist

- [ ] Go server starts and serves HTTP on `:8080`
- [ ] Data directory created at `%LOCALAPPDATA%\ParanoidX`
- [ ] SQLite DB works (`modernc.org/sqlite` is CGO-free)
- [ ] Tor Expert Bundle connects, SOCKS5 on 9050
- [ ] xray connects, API accessible
- [ ] Docker Desktop (WSL2) runs SMP, XFTP, coturn
- [ ] Flutter apps (Windows build) connect to server
- [ ] USB backup detects drive letter with label
- [ ] Graceful shutdown on Ctrl+C / service stop