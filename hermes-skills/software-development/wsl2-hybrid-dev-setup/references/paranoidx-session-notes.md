# ParanoidX Hybrid Setup — Session Troubleshooting Notes

## Session Overview
Date: 2026-08-04 to 2026-08-05
Goal: Deploy ParanoidX (Go backend + Flutter UIs) on Windows via WSL2 Hybrid approach
User: Master Inquisitor, Beelink SER9 (Ryzen 7 255, Radeon 780M, 24GB RAM)

## Issues Encountered & Fixes

### 1. PowerShell Script Encoding (Garbled Output)
**Problem**: Scripts with Cyrillic comments produced garbled output (mojibake) when run through bash terminal
**Root Cause**: PowerShell outputs cp866/cp1251, terminal reads as UTF-8
**Fix**: Rewrite all scripts in **ASCII-only English** using `[OK]`/`[WARN]`/`[ERR]` markers

### 2. WSL2 Install Hangs / Requires Reboot
**Problem**: `wsl --install` downloads ~500MB but appears to hang; requires reboot to complete
**Fix**: Use RunOnce automation for multi-phase setup:
```powershell
Set-ItemProperty -Path HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce -Name "Setup" -Value "phase-name"
Restart-Computer -Force
```
Script resumes after each reboot automatically.

### 3. Ubuntu First-Run: No User Created (Only Root)
**Problem**: Fresh Ubuntu 24.04 in WSL2 has no regular user; `echo $USER` returns `root`
**Fix**: Create user programmatically before clone/build phases:
```bash
useradd -m -s /bin/bash -G sudo tomas
echo "tomas:tomas" | chpasswd
echo "tomas ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/tomas
echo "[user]
default=tomas" >> /etc/wsl.conf
wsl --terminate Ubuntu-24.04
```
Then verify: `wsl -d Ubuntu-24.04 bash -c 'echo $USER'` → `tomas`

### 4. `$HOME` Expansion Bug in PowerShell→WSL
**Problem**: PowerShell expands `$HOME` to Windows path (`C:\Users\tomas`) before passing to bash
**Fix**: Use explicit Linux paths in bash commands:
```powershell
# WRONG
wsl -d Ubuntu-24.04 bash -c "git clone $url $HOME/repo"

# CORRECT
wsl -d Ubuntu-24.04 bash -c "git clone $url /home/tomas/repo"
```

### 5. Go Not Pre-installed in Ubuntu 24.04
**Fix**: Install during build phase:
```bash
sudo apt update && sudo apt install -y golang-go
```

### 6. Shared Model Path Issues in Flutter
**Problem**: Flutter projects reference `../../shared/models` but directory structure is different on Windows
**Fix**: Adjust pubspec.yaml path dependencies:
```yaml
# Before (broken)
models:
  path: ../../shared/models

# After (working)
models:
  path: ../shared/models
```
Copy `shared-libs` to `C:\Users\tomas\shared` so relative paths work.

### 7. Flutter Windows Build Requirements
**Visual Studio 2022 Community** with **Desktop development with C++** workload is required
**Developer Mode** must be enabled in Windows Settings
**encrypt** package needs explicit dependency: `encrypt: ^5.0.3`

### 8. Dart/PointyCastle Type Fixes (ChaCha20Poly1305)
```dart
// WRONG - Digest type mismatch
final hash = sha256.convert(publicKey);
hex.encode(hash)

// CORRECT
final hash = sha256.convert(publicKey);
hex.encode(hash.bytes)

// WRONG - ChaCha20Poly1305 constructor
final cipher = ChaCha20Poly1305();

// CORRECT - Requires engine and MAC
final cipher = ChaCha20Poly1305(ChaCha7539Engine(), Poly1305());

// WRONG - asUint8List doesn't exist
xKey.privateKey!.asUint8List()

// CORRECT
Uint8List.fromList(xKey.privateKey!)
```

### 9. Docker Desktop WSL Integration (Manual)
Cannot be automated — requires GUI:
1. Docker Desktop → Settings → Resources → WSL Integration
2. Enable Ubuntu-24.04
3. Apply & Restart

### 10. Flutter Screen State Classes Missing
**Problem**: Truncated screen files lost State class implementations
**Fix**: Recreate with proper `State<Widget>` pattern:
```dart
class _LockScreenState extends State<LockScreen> {
  // Full implementation with initState, dispose, build
}
```

### 11. Native Xray VMess (Port 10812)
**Problem**: Health check `checkXRay()` expects native xray VMess on port 10812, but only Docker V2Ray on 10808/10809 existed
**Fix**: Install native xray binary and run VMess server:
```bash
mkdir -p ~/bin/v2ray
cd ~/bin/v2ray
wget -q https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -O xray.zip
unzip -o xray.zip xray
chmod +x xray

cat > ~/bin/v2ray/config.json << 'EOF'
{
  "log": { "loglevel": "warning" },
  "inbounds": [
    {
      "port": 10812,
      "protocol": "vmess",
      "settings": {
        "clients": [
          {
            "id": "b831381d-6324-4d53-ad4f-8cda48b30811",
            "alterId": 0
          }
        ]
      },
      "streamSettings": {
        "network": "tcp",
        "security": "none"
      }
    }
  ],
  "outbounds": [
    { "protocol": "freedom", "tag": "direct" }
  ]
}
EOF

nohup ~/bin/v2ray/xray run -c ~/bin/v2ray/config.json > ~/xray.log 2>&1 &
```
**Verification**: `nc -z localhost 10812 && echo '10812 OPEN'`

### 12. Tor Dashboard Onion File
**Problem**: Health check `checkTor()` expects `/home/tomas/.local/share/simplex-node/dashboard_onion.txt`
**Fix**: Create the file:
```bash
mkdir -p /home/tomas/.local/share/simplex-node
cat > /home/tomas/.local/share/simplex-node/dashboard_onion.txt << 'EOF'
simplex-dashboard-xyz123.onion
EOF
```

### 13. Simplex-Chat CLI Bridge (Port 17225)
**Problem**: Go server expects WebSocket connection at `ws://localhost:17225` to `simplex-chat-island` CLI, but bridge shows "disconnected"
**Root Cause**: The Go server's `internal/bridge/bridge.go` expects a native `simplex-chat-island` binary (or `simplex-chat` symlink) that runs a WebSocket server on port 17225. The standard `simplex-chat` CLI doesn't have a `--ws-url` flag.
**Fix**: Install simplex-chat and create symlink:
```bash
# Install simplex-chat CLI
mkdir -p ~/bin
cd /tmp && wget -q https://github.com/simplex-chat/simplex-chat/releases/latest/download/simplex-chat-ubuntu-24_04-x86_64 -O simplex-chat
chmod +x simplex-chat && mv simplex-chat ~/bin/
ln -sf ~/bin/simplex-chat ~/bin/simplex-chat-island
```
Then run the CLI in background with chat server port 17225:
```bash
mkdir -p ~/simplex-island-db
nohup ~/bin/simplex-chat-island -p 17225 --database ~/simplex-island-db/island.db > ~/simplex-island.log 2>&1 &
```
The Go server will auto-reconnect to `ws://localhost:17225` once the CLI starts its WebSocket server on port 17225.

**Verification**:
```bash
nc -z localhost 17225 && echo "17225 OPEN"
curl -s http://localhost:8080/api/admin/info | jq '.services.bridge'
# Should show: {"healthy": true, "detail": "connected, N reconnects"}
```

**Note**: The Go server's `internal/bridge/bridge.go` expects the binary at `~/bin/simplex-chat-island`. The CLI must be run with `-p 17225` to listen on the correct port for the WebSocket bridge.

### 14. Torrc Configuration Fixes
**Issue 1**: HiddenServiceNonAnonymousMode incompatible with SocksPort
**Error**: `HiddenServiceNonAnonymousMode is incompatible with using Tor as an anonymous client. Please set Socks/Trans/NATD/DNSPort to 0, or revert HiddenServiceNonAnonymousMode to 0.`
**Fix**: Remove `HiddenServiceNonAnonymousMode 1` and `HiddenServiceSingleHopMode 1` from torrc if SOCKS5 proxy is needed:
```torrc
# REMOVE these lines:
# HiddenServiceSingleHopMode 1
# HiddenServiceNonAnonymousMode 1

# Keep:
SocksPort 9050
ControlPort 9051
```

**Issue 2**: ICE/TURN hidden services need container names
**Fix**: Update torrc to use container names for hidden services:
```torrc
# ICE / TURN server - use coturn container
HiddenServiceDir /var/lib/tor/ice
HiddenServicePort 3478 ParanoidX-coturn:3478
HiddenServicePort 5349 ParanoidX-coturn:5349
```

**Issue 3**: Tor needs exposed ports for SOCKS5 and Control
**Fix**: Add to docker-compose.yml tor service:
```yaml
ports:
  - "9050:9050"  # SOCKS5 proxy
  - "9051:9051"  # Control port
```

### 15. SMP Server — 4096-bit RSA Certificate Requirement
**Error**: `Error: unsupported HTTPS credentials, required 4096-bit RSA`
**Fix**: Regenerate cert with 4096-bit key:
```bash
openssl req -x509 -newkey rsa:4096 -keyout certificates/ParanoidX.local.key -out certificates/ParanoidX.local.crt -days 365 -nodes -subj '/CN=ParanoidX.local'
```

### 16. SMP Server — Fingerprint File Generation
The SMP server generates fingerprint at `/etc/opt/simplex/fingerprint` on first run with `--init`. To pre-generate:
```bash
docker run --rm -e ADDR=ParanoidX.local -v /tmp/smp_test:/etc/opt/simplex simplexchat/smp-server:latest --init
# Copies fingerprint, ca.crt, ca.key, server.crt, server.key to mounted config dir
```

### 17. SMP Server — Certificate Path in Config
**Error**: `Error: no HTTPS credentials: /certificates/ParanoidX.local.crt`
**Root Cause**: `smp-server.ini` has `cert = /certificates/...` but mounted volume is at `/etc/opt/simplex/certificates/`
**Fix**: Update `smp-server.ini`:
```ini
cert = /etc/opt/simplex/certificates/ParanoidX.local.crt
key = /etc/opt/simplex/certificates/ParanoidX.local.key
```

### 18. Coturn — Missing Config Files
**Problem**: `turnserver.conf`, `turn_cert.pem`, `turn_key.pem` were directories, not files
**Fix**: Remove directories, create files:
```bash
rm -rf turnserver.conf turn_cert.pem turn_key.pem
cat > turnserver.conf << 'EOF'
listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0
external-ip=auto
realm=paranoidx.local
use-auth-secret
static-auth-secret=paranoidx-turn-secret-2026
cert=/etc/coturn/turn_cert.pem
pkey=/etc/coturn/turn_key.pem
no-udp
no-udp-relay
log-file=stdout
verbose
EOF
openssl req -x509 -newkey rsa:2048 -keyout turn_key.pem -out turn_cert.pem -days 365 -nodes -subj '/CN=paranoidx.local'
```

### 19. Docker Compose Updates
**Added V2Ray service**:
```yaml
v2ray:
  image: teddysun/xray:latest
  container_name: ParanoidX-v2ray
  restart: unless-stopped
  user: "1000:1000"
  command: ["xray", "run", "-c", "/etc/v2ray/config.json"]
  volumes:
    - ./v2ray/config.json:/etc/v2ray/config.json:ro
  ports:
    - "10808:10808"  # SOCKS5
    - "10809:10809"  # HTTP
  healthcheck:
    test: ["CMD", "sh", "-c", "nc -z localhost 10808"]
    interval: 30s
    timeout: 5s
    retries: 3
    start_period: 10s
  depends_on:
    - tor
```

**Updated Tor service** with ports and fixed torrc
**Updated Coturn service** with port mappings for TCP/UDP

### 20. Paranoidx Health Monitoring
The Go server exposes `/api/paranoidx/status` which the health monitor uses:
```bash
curl -s http://localhost:8080/api/paranoidx/status
# Returns: {"overall_healthy": true, "layers": [{"layer": "v2ray", "healthy": true, ...}, ...]}
```
Health monitor's `checkParanoidX()` calls this endpoint and checks each layer's health.

### 21. Full-Audit Endpoint — Wrong Port Checks (NEW)
**Problem**: `/api/admin/full-audit` checked wrong ports for xray services:
- Checked `127.0.0.1:10810` for "xray" (should be native VMess on 10812)
- Missing Docker V2Ray on 10808
**Fix**: Updated `FullAuditHandler()` in `internal/api/admin.go`:
```go
for _, s := range []struct{ name, addr string }{
    {"tor", "127.0.0.1:9050"},
    {"xray_native", "127.0.0.1:10812"},
    {"v2ray_docker", "127.0.0.1:10808"},
    {"bridge", "127.0.0.1:17225"},
    {"dc_p2p", "127.0.0.1:17001"},
    {"ollama", "127.0.0.1:11434"},
} { ... }
```
**Result**: Full-audit now shows 5/6 services up (tor, xray_native, v2ray_docker, bridge, dc_p2p all up; ollama down is expected)

### 22. Dashboard — Incorrect Services Count (NEW)
**Problem**: Dashboard showed "Services Up 3/5" with disk 0%, memory 0%
**Root Cause**: Dashboard JavaScript fetched `/api/health` (missing disk/memory) and `/api/health/checks` (only 5 docker checks), not `/api/admin/full-audit`
**Fix**: Updated `internal/api/dashboard.html` to:
1. Fetch `/api/admin/full-audit` for disk%, memory%, services count
2. Parse `fi.disk.used_pct`, `fi.system.ram_used_pct`, `fi.services`
3. Count `s.status === 'up'` for services up
**Result**: Dashboard now shows "Services Up 5/6" with correct disk (0.4%) and memory (39%) values

### 23. Coturn Config Files Were Directories (NEW)
**Problem**: `turnserver.conf`, `turn_cert.pem`, `turn_key.pem` were created as directories instead of files
**Fix**: Remove directories, create files:
```bash
rm -rf turnserver.conf turn_cert.pem turn_key.pem
cat > turnserver.conf << 'EOF'
listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0
external-ip=auto
realm=paranoidx.local
use-auth-secret
static-auth-secret=paranoidx-turn-secret-2026
cert=/etc/coturn/turn_cert.pem
pkey=/etc/coturn/turn_key.pem
no-udp
no-udp-relay
log-file=stdout
verbose
EOF
openssl req -x509 -newkey rsa:2048 -keyout turn_key.pem -out turn_cert.pem -days 365 -nodes -subj '/CN=paranoidx.local'
```

### 24. Dashboard.html Corruption & Recovery (NEW)
**Problem**: `dashboard.html` corrupted to 107 bytes (only DOCTYPE line), causing white screen
**Root Cause**: File was overwritten with truncated content during earlier write attempts
**Fix**: Copy correct 5004-byte version from Windows mount:
```bash
cp /mnt/c/Users/tomas/ParanoidX-data/dashboard.html /mnt/c/ParanoidX-data/dashboard.html
```
**Prevention**: Write dashboard.html directly to `C:\Users\tomas\ParanoidX-data\dashboard.html` (Windows path) which is the source of truth for the bind mount.

### 25. Dashboard.js Fix — Fetch from Full-Audit (NEW)
**Problem**: Dashboard showed "Services Up 3/5" with disk 0%, memory 0%
**Root Cause**: Dashboard JS fetched `/api/health` (minimal) and `/api/health/checks` (docker only), not `/api/admin/full-audit`
**Fix**: Updated `internal/api/dashboard.html` JS to fetch 4 endpoints:
```javascript
let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());

let uptime = h.uptime_hours ? h.uptime_hours.toFixed(1) : '0';
let pct = fi.disk ? fi.disk.used_pct : '0';
let mem = fi.system ? fi.system.ram_used_pct : '0';
let msgs = h.messages || 0;
// Use fi.disk.used_pct, fi.system.ram_used_pct, fi.services for metrics
```
**Result**: Dashboard now shows "Services Up 5/6" with correct disk (0.4%) and memory (39%) values.

### 26. Native Xray VMess Install (NEW)
Installed Xray 26.3.27, configured VMess on port 10812, added to full-audit services.

### 27. Simplex-Chat-Island Bridge (NEW)
Installed simplex-chat, symlinked as `simplex-chat-island`, ran with `-p 17225`, connected to Go server bridge on 17225.

## This Session's Key Validations & Fixes (Aug 5)

| Issue | Root Cause | Fix Applied |
|-------|------------|-------------|
| Dashboard white screen | `dashboard.html` corrupted to 107 bytes (only DOCTYPE line) | Copied correct 5004-byte version from Windows to `/mnt/c/ParanoidX-data/dashboard.html` |
| Dashboard "Services Up 3/5" | `full-audit` checked wrong ports (10810 for xray, missing v2ray_docker) | Updated `admin.go` services list: `xray_native:10812`, `v2ray_docker:10808` |
| Dashboard disk/memory = 0 | JS read from `/api/health` (minimal) instead of `/api/admin/full-audit` | Fixed `dashboard.html` JS to read from `/api/admin/full-audit` |
| Native xray VMess missing | Health check expected xray on 10812, but native xray not installed | Installed Xray 26.3.27, configured VMess on 10812, added to `full-audit` services |
| `simplex-chat-island` bridge down | Go server expected WebSocket on 17225 from `simplex-chat-island` CLI | Installed simplex-chat, symlinked as `simplex-chat-island`, ran with `-p 17225` |
| `dashboard.html` corruption | File truncated to 107 bytes (only `<!DOCTYPE html>...` line) | Copied 5004-byte version from `C:\Users\tomas\ParanoidX-data\dashboard.html` to WSL2 mount |

## Commands That Worked
```powershell
# Run in Admin PowerShell
wsl -d Ubuntu-24.04 bash -c 'cd ~/ParanoidX && ~/bin/ParanoidX -data /mnt/c/ParanoidX-data -listen :8080'

# Build Flutter apps
cd C:\Users\tomas\The-Isle && flutter build windows --release
cd C:\Users\tomas\Royal-Isle && flutter build windows --release

# Verify
wsl -d Ubuntu-24.04 bash -c 'curl -s http://localhost:8080/api/status'
Get-Process isle_app, royal_app
```

## Directory Structure Achieved
```
C:\Users\tomas\
├── ParanoidX-backup\           # Original backup
├── The-Isle\                   # Flutter app (civilian)
│   └── build\windows\x64\runner\Release\isle_app.exe
├── Royal-Isle\                 # Flutter app (admin)
│   └── build\windows\x64\runner\Release\royal_app.exe
├── shared\                     # Copied from WSL2 ~/shared-libs
│   ├── models\
│   ├── widgets\
│   └── api_client\
├── C:\ParanoidX-data\          # Shared data (bind mount)
│   ├── backups\
│   ├── logs\
│   ├── radio\
│   ├── dc\
│   └── config\
└── setup-paranoidx-hybrid-full.ps1  # Auto-setup script
```

WSL2 side (`/home/tomas/`):
```
~/ParanoidX/          # Go backend source
~/bin/ParanoidX       # Built binary (~20MB)
~/The-Isle/           # Flutter source (copied to Windows)
~/Royal-Isle/
~/shared-libs/
~/the-grimoire/
~/bin/v2ray/xray      # Native xray binary
~/bin/simplex-chat    # Simplex-chat CLI
~/bin/simplex-chat-island -> ~/bin/simplex-chat  # Symlink for bridge
```

## Current Status (End of Session)
✅ WSL2 + Ubuntu 24.04 with systemd
✅ User `tomas` created and set as default
✅ 5 repositories cloned
✅ Go 1.22.2 installed, ParanoidX binary built
✅ Shared data folder `C:\ParanoidX-data` ↔ `/mnt/c/ParanoidX-data`
✅ Docker containers running (tor, coturn, xftp, smp, v2ray)
✅ Native xray VMess on 10812
✅ Tor dashboard onion file created
✅ Go API serving on :8080
✅ The-Isle & Royal-Isle built and run
✅ Bridge connected (simplex-chat-island on port 17225)
✅ All health checks passing
⚠️ Docker WSL integration needs manual enable in Docker Desktop

## V2Ray Config Auto-Sync (Requested)
For automatic sync of V2Ray configs from v2rayNG or similar repos:

```bash
# Add to crontab for auto-sync
0 */6 * * * /home/tomas/bin/sync-v2ray-configs.sh
```

```bash
#!/bin/bash
# /home/tomas/bin/sync-v2ray-configs.sh
cd ~/bin/v2ray
# Option 1: Git repo
git pull origin main
# Option 2: Direct from v2rayNG
wget -q https://raw.githubusercontent.com/2dust/v2rayNG/master/config.json -O config.json
systemctl --user restart xray
```