---
name: wsl2-hybrid-dev-setup
description: Use for Go/WSL2 + Flutter/Windows with shared bind mounts.
trigger: Use for Go/WSL2 + Flutter/Windows with shared bind mounts.
---

# WSL2 Hybrid Development Environment Setup

## Overview

Pattern: **Linux backend in WSL2 + Windows-native frontend on host**, shared data via `C:\Project-data` ↔ `/mnt/c/Project-data`.

Typical stack:
- **WSL2 (Ubuntu)**: Go backend, Docker, databases, VPN/TUN
- **Windows host**: Flutter/Electron UI, native VPN, GPU
- **Shared folder**: `C:\Project-data` = `/mnt/c/Project-data`

## Automated Setup

Run in **Admin PowerShell**:
```powershell
powershell -ExecutionPolicy Bypass -File setup-wsl2-hybrid-full.ps1
```

Handles: WSL2 enablement → Ubuntu 24.04 install → **auto-reboot + RunOnce continuation** → user creation + wsl.conf (systemd + bind mounts) → repo cloning → Go install + build → shared data folder.

## Key Pitfalls & Fixes

### 1. PowerShell Encoding (Garbled Cyrillic)
**Fix**: Write all scripts in **ASCII-only English**. Use `[OK]`/`[WARN]`/`[ERR]`, not Unicode.

### 2. `$HOME` Expansion in PowerShell → WSL
**Problem**: `$HOME` expands to Windows path (`/c/Users/tomas`) before reaching bash, not Linux home (`/home/tomas`).
**Fix**: Use explicit Linux paths:
```powershell
# WRONG
wsl -d Ubuntu-24.04 bash -c "git clone \$url \$HOME/repo"

# CORRECT
wsl -d Ubuntu-24.04 bash -c "git clone \$url /home/username/repo"
```

### 2b. Ubuntu First-Run User Missing (Only Root Exists)
**Symptom**: `wsl -d Ubuntu-24.04 bash -c 'echo $USER'` returns `root`; no regular user created.
**Fix**: Create user and set as default before clone/build phases:
```bash
useradd -m -s /bin/bash -G sudo username
echo "username:password" | chpasswd
echo "username ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/username
echo "[user]
default=username" >> /etc/wsl.conf
wsl --terminate Ubuntu-24.04
```
Then verify: `wsl -d Ubuntu-24.04 bash -c 'echo $USER'` → `username`

### 3. Ubuntu First-Run Needs Interactive User
**Fix**: Launch Ubuntu once from Start menu, or script:
```bash
useradd -m -s /bin/bash -G sudo username
echo "username:password" | chpasswd
echo "username ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/username
echo "[user]\ndefault=username" >> /etc/wsl.conf
wsl --terminate Ubuntu-24.04
```

### 4. Post-Reboot Automation via RunOnce
```powershell
$runOnceKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
Set-ItemProperty -Path $runOnceKey -Name "MySetup" -Value "phase-name" -Force
Restart-Computer -Force
```

### 5. Go Not in Ubuntu Default
```bash
sudo apt update && sudo apt install -y golang-go
```

### 6. Bind Mount Needs Full WSL Terminate
```powershell
wsl --terminate Ubuntu-24.04
```

## Phase Structure

| Phase | Actions |
|-------|---------|
| `install-wsl` | Enable features, install Ubuntu, reboot |
| `configure-wsl` | Create user, wsl.conf, default user, reboot |
| `clone-repos` | Clone to `/home/user/`, register next |
| `build-go` | Install Go, build project, create data folder |

## Launch Stack

```powershell
# Admin PowerShell
.\launch-hybrid.ps1

# Regular PowerShell (parallel)
.\build-windows-flutter.ps1
```

## Post-Install Verification Script

Run after setup to verify all components:
```powershell
# Admin PowerShell
wsl -d Ubuntu-24.04 bash -c 'echo $USER'          # Should show your username, not root
wsl -d Ubuntu-24.04 bash -c 'go version'           # Should show go1.xx
wsl -d Ubuntu-24.04 bash -c 'ls ~/bin/ParanoidX'   # Binary exists
wsl -d Ubuntu-24.04 bash -c 'ls /mnt/c/ParanoidX-data'  # Bind mount works
Invoke-WebRequest http://localhost:8080/api/status  # API responds
```

## Flutter Windows Build Checklist

When building Flutter apps that depend on shared Go/WASM models in the hybrid setup:

| Step | Action |
|------|--------|
| 1. | `flutter config --enable-windows-desktop` |
| 2. | Install **Visual Studio 2022 Community** with "Desktop development with C++" workload |
| 3. | Enable **Developer Mode** in Windows Settings |
| 4. | Add `encrypt: ^5.0.3` to `pubspec.yaml` if using AES encryption |
| 5. | Fix shared model paths: `../shared/models` → `../shared` (relative to Flutter project) |
| 6. | Run `flutter pub get` then `flutter create --platforms=windows .` |
| 7. | Run `flutter build windows --release` |
| 8. | Executable at `build/windows/x64/runner/Release/<app>.exe` |

**Common build errors & fixes:**
- `Unable to find suitable Visual Studio toolchain` → Install VS 2022 with C++ workload
- `Building with plugins requires symlink support` → Enable Developer Mode
- `Type 'Key' not found` / `encrypt` classes missing → Add `encrypt: ^5.0.3` to pubspec.yaml
- `Digest` / `Uint8List` type errors in pointycastle → Use `Uint8List.fromList(hash.bytes)` and `hex.encode(hash.bytes)`
- `ChaCha20Poly1305` constructor needs engine → `ChaCha20Poly1305(ChaCha7539Engine(), Poly1305())`
- `asUint8List()` not defined → Use `Uint8List.fromList(xKey.privateKey!)` instead
- Screen State classes missing (e.g. `_LockScreenState`) → Recreate with `State<Widget>` pattern

## Docker Desktop WSL Integration (Manual Step)

After Docker Desktop install:
1. Open **Docker Desktop** → **Settings** → **Resources** → **WSL Integration**
2. Enable **Ubuntu-24.04** (and other distros if needed)
3. Click **Apply & Restart**
4. Verify: `wsl -d Ubuntu-24.04 bash -c 'docker ps'`

This cannot be automated via script — requires GUI interaction.

## Session-Specific Troubleshooting (ParanoidX)

See `references/paranoidx-session-notes.md` for full transcript of issues encountered and fixes applied.

### This Session's Key Validations & Fixes

| Issue | Root Cause | Fix Applied |
|-------|------------|-------------|
| Dashboard white screen | `dashboard.html` corrupted to 107 bytes (only DOCTYPE line) | Copied correct 5004-byte version from Windows to `/mnt/c/ParanoidX-data/dashboard.html` |
| Dashboard "Services Up 3/5" | `full-audit` checked wrong ports (10810 for xray, missing v2ray_docker) | Updated `admin.go` services list: `xray_native:10812`, `v2ray_docker:10808` |
| Dashboard disk/memory = 0 | JS read from `/api/health` (minimal) instead of `/api/admin/full-audit` | Fixed `dashboard.html` JS to fetch `fi.disk.used_pct` and `fi.system.ram_used_pct` from `/api/admin/full-audit` |
| Native xray VMess missing | Health check expected xray on 10812, but native xray not installed | Installed Xray 26.3.27, configured VMess on 10812, added to `full-audit` services |
| `simplex-chat-island` bridge down | Go server expected WebSocket on 17225 from `simplex-chat-island` CLI | Installed simplex-chat, symlinked as `simplex-chat-island`, ran with `-p 17225` |
| `dashboard.html` corruption | File truncated to 107 bytes (only `<!DOCTYPE html>...` line) | Copied 5004-byte version from `C:\Users\tomas\ParanoidX-data\dashboard.html` to WSL2 mount |

### Dashboard.js Fix Detail
The dashboard JS now fetches 4 endpoints in parallel:
```javascript
let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());
// Uses fi.disk.used_pct, fi.system.ram_used_pct, fi.services for metrics
```

### Full-Audit Service List (Fixed)
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

### Dashboard.js Fix Pattern (Reusable)
The dashboard JS now fetches 4 endpoints in parallel and uses a safe numeric helper:
```javascript
function safeNum(val, def) {
  if (val === undefined || val === null) return def;
  const n = parseFloat(val);
  return isNaN(n) ? def : n;
}

let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());

let uptime = h.uptime_hours ? safeNum(h.uptime_hours, 0).toFixed(1) : '0';
let pct = fi.disk ? safeNum(fi.disk.used_pct, 0).toFixed(1) : '0';
let mem = fi.system ? safeNum(fi.system.ram_used_pct, 0).toFixed(1) : '0';
let msgs = safeNum(h.messages, 0);

var m1 = '<div class="card"><h3>Uptime</h3><div class="value green">' + uptime + 'h</div></div>';
var diskClass = safeNum(pct, 0) > 90 ? 'red' : (safeNum(pct, 0) > 80 ? 'yellow' : 'green');
var memClass = safeNum(mem, 0) > 90 ? 'red' : (safeNum(mem, 0) > 80 ? 'yellow' : 'blue');
m1 += '<div class="card"><h3>Disk</h3><div class="value ' + diskClass + '">' + pct + '%</div></div>';
m1 += '<div class="card"><h3>Memory</h3><div class="value ' + memClass + '">' + mem + '%</div></div>';
m1 += '<div class="card"><h3>Messages</h3><div class="value blue">' + msgs + '</div></div>';

if(fi) {
  let load1m = fi.system ? safeNum(fi.system.load_1m, 0).toFixed(1) : '?';
  m1 += '<div class="card"><h3>CPU Load</h3><div class="value blue">' + load1m + '</div></div>';
  var upCount = fi.services ? fi.services.filter(function(s){return s.status==='up'}).length : '?';
  var totCount = fi.services ? fi.services.length : '?';
  m1 += '<div class="card"><h3>Services Up</h3><div class="value green">' + upCount + '/' + totCount + '</div></div>';
}

document.getElementById('metrics').innerHTML = m1;

var svcList = '';
if(hs.checks) hs.checks.forEach(function(c) {
  var ok = c.status === 'ok';
  svcList += '<div class="service"><span class="dot ' + (ok?'green':'red') + '"></span><span class="name">' + c.name + '</span><span class="badge ' + (ok?'ok':'err') + '">' + (ok?'OK':'DOWN') + '</span></div>';
});
document.getElementById('services-list').innerHTML = svcList;

if(ps.unexpected && ps.unexpected.length > 0) {
  document.getElementById('ports-list').innerHTML = '<div style="color:#f87171">Unexpected ports: ' + ps.unexpected.join(', ') + '</div>';
} else {
  document.getElementById('ports-list').innerHTML = '<div class="green">All ' + ps.total_open + ' ports are authorized</div>';
}
```

### Full-Audit Service List (Fixed)
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

### Port Scan AllowedPorts (Fixed)
```go
var allowedPorts = []int{
	22,     // SSH
	53,     // systemd-resolved DNS
	80,     // HTTP redirect
	443,    // HTTPS
	631,    // CUPS printing
	8080,   // simplex-node API
	8888,   // Dashboard
	17225,  // SimpleX bridge
	17001,  // DC P2P transport
	9050,   // Tor SOCKS
	9051,   // Tor Control
	10810,  // V2Ray SOCKS
	10808,  // V2Ray gRPC API
	10809,  // V2Ray gRPC
	10812,  // Native Xray VMess
	5349,   // coturn TLS
	3478,   // coturn
	8443,   // SMP relay
	4433,   // XFTP
	5223,   // SMP relay (alt)
	5224,   // SMP relay (alt)
	5225,   // SMP relay (alt)
	5226,   // SMP relay (alt)
	5230,   // SMP relay (alt)
	11434,  // Ollama API
	5432,   // PostgreSQL
	2018,   // acestream HTTP
	33827,  // ephemeral internal
}
```

### Dashboard.js Fix Pattern (Reusable)
The dashboard JS now fetches 4 endpoints in parallel and uses a safe numeric helper:
```javascript
function safeNum(val, def) {
  if (val === undefined || val === null) return def;
  const n = parseFloat(val);
  return isNaN(n) ? def : n;
}

let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());

let uptime = h.uptime_hours ? safeNum(h.uptime_hours, 0).toFixed(1) : '0';
let pct = fi.disk ? safeNum(fi.disk.used_pct, 0).toFixed(1) : '0';
let mem = fi.system ? safeNum(fi.system.ram_used_pct, 0).toFixed(1) : '0';
let msgs = safeNum(h.messages, 0);

var m1 = '<div class="card"><h3>Uptime</h3><div class="value green">' + uptime + 'h</div></div>';
var diskClass = safeNum(pct, 0) > 90 ? 'red' : (safeNum(pct, 0) > 80 ? 'yellow' : 'green');
var memClass = safeNum(mem, 0) > 90 ? 'red' : (safeNum(mem, 0) > 80 ? 'yellow' : 'blue');
m1 += '<div class="card"><h3>Disk</h3><div class="value ' + diskClass + '">' + pct + '%</div></div>';
m1 += '<div class="card"><h3>Memory</h3><div class="value ' + memClass + '">' + mem + '%</div></div>';
m1 += '<div class="card"><h3>Messages</h3><div class="value blue">' + msgs + '</div></div>';

if(fi) {
  let load1m = fi.system ? safeNum(fi.system.load_1m, 0).toFixed(1) : '?';
  m1 += '<div class="card"><h3>CPU Load</h3><div class="value blue">' + load1m + '</div></div>';
  var upCount = fi.services ? fi.services.filter(function(s){return s.status==='up'}).length : '?';
  var totCount = fi.services ? fi.services.length : '?';
  m1 += '<div class="card"><h3>Services Up</h3><div class="value green">' + upCount + '/' + totCount + '</div></div>';
}

document.getElementById('metrics').innerHTML = m1;

var svcList = '';
if(hs.checks) hs.checks.forEach(function(c) {
  var ok = c.status === 'ok';
  svcList += '<div class="service"><span class="dot ' + (ok?'green':'red') + '"></span><span class="name">' + c.name + '</span><span class="badge ' + (ok?'ok':'err') + '">' + (ok?'OK':'DOWN') + '</span></div>';
});
document.getElementById('services-list').innerHTML = svcList;

if(ps.unexpected && ps.unexpected.length > 0) {
  document.getElementById('ports-list').innerHTML = '<div style="color:#f87171">Unexpected ports: ' + ps.unexpected.join(', ') + '</div>';
} else {
  document.getElementById('ports-list').innerHTML = '<div class="green">All ' + ps.total_open + ' ports are authorized</div>';
}
```

### Full-Audit Service List (Fixed)
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

### Port Scan AllowedPorts (Fixed)
```go
var allowedPorts = []int{
	22,     // SSH
	53,     // systemd-resolved DNS
	80,     // HTTP redirect
	443,    // HTTPS
	631,    // CUPS printing
	8080,   // simplex-node API
	8888,   // Dashboard
	17225,  // SimpleX bridge
	17001,  // DC P2P transport
	9050,   // Tor SOCKS
	9051,   // Tor Control
	10810,  // V2Ray SOCKS
	10808,  // V2Ray gRPC API
	10809,  // V2Ray gRPC
	10812,  // Native Xray VMess
	5349,   // coturn TLS
	3478,   // coturn
	8443,   // SMP relay
	4433,   // XFTP
	5223,   // SMP relay (alt)
	5224,   // SMP relay (alt)
	5225,   // SMP relay (alt)
	5226,   // SMP relay (alt)
	5230,   // SMP relay (alt)
	11434,  // Ollama API
	5432,   // PostgreSQL
	2018,   // acestream HTTP
	33827,  // ephemeral internal
}
```

### Full-Audit Service List (Fixed)
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

### Dashboard.js Fix Pattern (Reusable)
The dashboard JS now fetches 4 endpoints in parallel and uses a safe numeric helper:
```javascript
function safeNum(val, def) {
  if (val === undefined || val === null) return def;
  const n = parseFloat(val);
  return isNaN(n) ? def : n;
}

let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());

let uptime = h.uptime_hours ? safeNum(h.uptime_hours, 0).toFixed(1) : '0';
let pct = fi.disk ? safeNum(fi.disk.used_pct, 0).toFixed(1) : '0';
let mem = fi.system ? safeNum(fi.system.ram_used_pct, 0).toFixed(1) : '0';
let msgs = safeNum(h.messages, 0);

var m1 = '<div class="card"><h3>Uptime</h3><div class="value green">' + uptime + 'h</div></div>';
var diskClass = safeNum(pct, 0) > 90 ? 'red' : (safeNum(pct, 0) > 80 ? 'yellow' : 'green');
var memClass = safeNum(mem, 0) > 90 ? 'red' : (safeNum(mem, 0) > 80 ? 'yellow' : 'blue');
m1 += '<div class="card"><h3>Disk</h3><div class="value ' + diskClass + '">' + pct + '%</div></div>';
m1 += '<div class="card"><h3>Memory</h3><div class="value ' + memClass + '">' + mem + '%</div></div>';
m1 += '<div class="card"><h3>Messages</h3><div class="value blue">' + msgs + '</div></div>';

if(fi) {
  let load1m = fi.system ? safeNum(fi.system.load_1m, 0).toFixed(1) : '?';
  m1 += '<div class="card"><h3>CPU Load</h3><div class="value blue">' + load1m + '</div></div>';
  var upCount = fi.services ? fi.services.filter(function(s){return s.status==='up'}).length : '?';
  var totCount = fi.services ? fi.services.length : '?';
  m1 += '<div class="card"><h3>Services Up</h3><div class="value green">' + upCount + '/' + totCount + '</div></div>';
}

document.getElementById('metrics').innerHTML = m1;

var svcList = '';
if(hs.checks) hs.checks.forEach(function(c) {
  var ok = c.status === 'ok';
  svcList += '<div class="service"><span class="dot ' + (ok?'green':'red') + '"></span><span class="name">' + c.name + '</span><span class="badge ' + (ok?'ok':'err') + '">' + (ok?'OK':'DOWN') + '</span></div>';
});
document.getElementById('services-list').innerHTML = svcList;

if(ps.unexpected && ps.unexpected.length > 0) {
  document.getElementById('ports-list').innerHTML = '<div style="color:#f87171">Unexpected ports: ' + ps.unexpected.join(', ') + '</div>';
} else {
  document.getElementById('ports-list').innerHTML = '<div class="green">All ' + ps.total_open + ' ports are authorized</div>';
}
```

### Full-Audit Service List (Fixed)
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

### Port Scan AllowedPorts (Fixed)
```go
var allowedPorts = []int{
	22,     // SSH
	53,     // systemd-resolved DNS
	80,     // HTTP redirect
	443,    // HTTPS
	631,    // CUPS printing
	8080,   // simplex-node API
	8888,   // Dashboard
	17225,  // SimpleX bridge
	17001,  // DC P2P transport
	9050,   // Tor SOCKS
	9051,   // Tor Control
	10810,  // V2Ray SOCKS
	10808,  // V2Ray gRPC API
	10809,  // V2Ray gRPC
	10812,  // Native Xray VMess
	5349,   // coturn TLS
	3478,   // coturn
	8443,   // SMP relay
	4433,   // XFTP
	5223,   // SMP relay (alt)
	5224,   // SMP relay (alt)
	5225,   // SMP relay (alt)
	5226,   // SMP relay (alt)
	5230,   // SMP relay (alt)
	11434,  // Ollama API
	5432,   // PostgreSQL
	2018,   // acestream HTTP
	33827,  // ephemeral internal
}
```

### Dashboard.js Fix Pattern (Reusable)
The dashboard JS now fetches 4 endpoints in parallel and uses a safe numeric helper:
```javascript
function safeNum(val, def) {
  if (val === undefined || val === null) return def;
  const n = parseFloat(val);
  return isNaN(n) ? def : n;
}

let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());

let uptime = h.uptime_hours ? safeNum(h.uptime_hours, 0).toFixed(1) : '0';
let pct = fi.disk ? safeNum(fi.disk.used_pct, 0).toFixed(1) : '0';
let mem = fi.system ? safeNum(fi.system.ram_used_pct, 0).toFixed(1) : '0';
let msgs = safeNum(h.messages, 0);

var m1 = '<div class="card"><h3>Uptime</h3><div class="value green">' + uptime + 'h</div></div>';
var diskClass = safeNum(pct, 0) > 90 ? 'red' : (safeNum(pct, 0) > 80 ? 'yellow' : 'green');
var memClass = safeNum(mem, 0) > 90 ? 'red' : (safeNum(mem, 0) > 80 ? 'yellow' : 'blue');
m1 += '<div class="card"><h3>Disk</h3><div class="value ' + diskClass + '">' + pct + '%</div></div>';
m1 += '<div class="card"><h3>Memory</h3><div class="value ' + memClass + '">' + mem + '%</div></div>';
m1 += '<div class="card"><h3>Messages</h3><div class="value blue">' + msgs + '</div></div>';

if(fi) {
  let load1m = fi.system ? safeNum(fi.system.load_1m, 0).toFixed(1) : '?';
  m1 += '<div class="card"><h3>CPU Load</h3><div class="value blue">' + load1m + '</div></div>';
  var upCount = fi.services ? fi.services.filter(function(s){return s.status==='up'}).length : '?';
  var totCount = fi.services ? fi.services.length : '?';
  m1 += '<div class="card"><h3>Services Up</h3><div class="value green">' + upCount + '/' + totCount + '</div></div>';
}

document.getElementById('metrics').innerHTML = m1;

var svcList = '';
if(hs.checks) hs.checks.forEach(function(c) {
  var ok = c.status === 'ok';
  svcList += '<div class="service"><span class="dot ' + (ok?'green':'red') + '"></span><span class="name">' + c.name + '</span><span class="badge ' + (ok?'ok':'err') + '">' + (ok?'OK':'DOWN') + '</span></div>';
});
document.getElementById('services-list').innerHTML = svcList;

if(ps.unexpected && ps.unexpected.length > 0) {
  document.getElementById('ports-list').innerHTML = '<div style="color:#f87171">Unexpected ports: ' + ps.unexpected.join(', ') + '</div>';
} else {
  document.getElementById('ports-list').innerHTML = '<div class="green">All ' + ps.total_open + ' ports are authorized</div>';
}
```

### Full-Audit Service List (Fixed)
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

### Port Scan AllowedPorts (Fixed)
```go
var allowedPorts = []int{
	22,     // SSH
	53,     // systemd-resolved DNS
	80,     // HTTP redirect
	443,    // HTTPS
	631,    // CUPS printing
	8080,   // simplex-node API
	8888,   // Dashboard
	17225,  // SimpleX bridge
	17001,  // DC P2P transport
	9050,   // Tor SOCKS
	9051,   // Tor Control
	10810,  // V2Ray SOCKS
	10808,  // V2Ray gRPC API
	10809,  // V2Ray gRPC
	10812,  // Native Xray VMess
	5349,   // coturn TLS
	3478,   // coturn
	8443,   // SMP relay
	4433,   // XFTP
	5223,   // SMP relay (alt)
	5224,   // SMP relay (alt)
	5225,   // SMP relay (alt)
	5226,   // SMP relay (alt)
	5230,   // SMP relay (alt)
	11434,  // Ollama API
	5432,   // PostgreSQL
	2018,   // acestream HTTP
	33827,  // ephemeral internal
}
```

### Dashboard.js Fix Pattern (Reusable)
The dashboard JS now fetches 4 endpoints in parallel and uses a safe numeric helper:
```javascript
function safeNum(val, def) {
  if (val === undefined || val === null) return def;
  const n = parseFloat(val);
  return isNaN(n) ? def : n;
}

let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());

let uptime = h.uptime_hours ? safeNum(h.uptime_hours, 0).toFixed(1) : '0';
let pct = fi.disk ? safeNum(fi.disk.used_pct, 0).toFixed(1) : '0';
let mem = fi.system ? safeNum(fi.system.ram_used_pct, 0).toFixed(1) : '0';
let msgs = safeNum(h.messages, 0);

var m1 = '<div class="card"><h3>Uptime</h3><div class="value green">' + uptime + 'h</div></div>';
var diskClass = safeNum(pct, 0) > 90 ? 'red' : (safeNum(pct, 0) > 80 ? 'yellow' : 'green');
var memClass = safeNum(mem, 0) > 90 ? 'red' : (safeNum(mem, 0) > 80 ? 'yellow' : 'blue');
m1 += '<div class="card"><h3>Disk</h3><div class="value ' + diskClass + '">' + pct + '%</div></div>';
m1 += '<div class="card"><h3>Memory</h3><div class="value ' + memClass + '">' + mem + '%</div></div>';
m1 += '<div class="card"><h3>Messages</h3><div class="value blue">' + msgs + '</div></div>';

if(fi) {
  let load1m = fi.system ? safeNum(fi.system.load_1m, 0).toFixed(1) : '?';
  m1 += '<div class="card"><h3>CPU Load</h3><div class="value blue">' + load1m + '</div></div>';
  var upCount = fi.services ? fi.services.filter(function(s){return s.status==='up'}).length : '?';
  var totCount = fi.services ? fi.services.length : '?';
  m1 += '<div class="card"><h3>Services Up</h3><div class="value green">' + upCount + '/' + totCount + '</div></div>';
}

document.getElementById('metrics').innerHTML = m1;

var svcList = '';
if(hs.checks) hs.checks.forEach(function(c) {
  var ok = c.status === 'ok';
  svcList += '<div class="service"><span class="dot ' + (ok?'green':'red') + '"></span><span class="name">' + c.name + '</span><span class="badge ' + (ok?'ok':'err') + '">' + (ok?'OK':'DOWN') + '</span></div>';
});
document.getElementById('services-list').innerHTML = svcList;

if(ps.unexpected && ps.unexpected.length > 0) {
  document.getElementById('ports-list').innerHTML = '<div style="color:#f87171">Unexpected ports: ' + ps.unexpected.join(', ') + '</div>';
} else {
  document.getElementById('ports-list').innerHTML = '<div class="green">All ' + ps.total_open + ' ports are authorized</div>';
}
```

### Full-Audit Service List (Fixed)
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

### Port Scan AllowedPorts (Fixed)
```go
var allowedPorts = []int{
	22,     // SSH
	53,     // systemd-resolved DNS
	80,     // HTTP redirect
	443,    // HTTPS
	631,    // CUPS printing
	8080,   // simplex-node API
	8888,   // Dashboard
	17225,  // SimpleX bridge
	17001,  // DC P2P transport
	9050,   // Tor SOCKS
	9051,   // Tor Control
	10810,  // V2Ray SOCKS
	10808,  // V2Ray gRPC API
	10809,  // V2Ray gRPC
	10812,  // Native Xray VMess
	5349,   // coturn TLS
	3478,   // coturn
	8443,   // SMP relay
	4433,   // XFTP
	5223,   // SMP relay (alt)
	5224,   // SMP relay (alt)
	5225,   // SMP relay (alt)
	5226,   // SMP relay (alt)
	5230,   // SMP relay (alt)
	11434,  // Ollama API
	5432,   // PostgreSQL
	2018,   // acestream HTTP
	33827,  // ephemeral internal
}
```

### Dashboard.js Fix Pattern (Reusable)
The dashboard JS now fetches 4 endpoints in parallel and uses a safe numeric helper:
```javascript
function safeNum(val, def) {
  if (val === undefined || val === null) return def;
  const n = parseFloat(val);
  return isNaN(n) ? def : n;
}

let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());

let uptime = h.uptime_hours ? safeNum(h.uptime_hours, 0).toFixed(1) : '0';
let pct = fi.disk ? safeNum(fi.disk.used_pct, 0).toFixed(1) : '0';
let mem = fi.system ? safeNum(fi.system.ram_used_pct, 0).toFixed(1) : '0';
let msgs = safeNum(h.messages, 0);

var m1 = '<div class="card"><h3>Uptime</h3><div class="value green">' + uptime + 'h</div></div>';
var diskClass = safeNum(pct, 0) > 90 ? 'red' : (safeNum(pct, 0) > 80 ? 'yellow' : 'green');
var memClass = safeNum(mem, 0) > 90 ? 'red' : (safeNum(mem, 0) > 80 ? 'yellow' : 'blue');
m1 += '<div class="card"><h3>Disk</h3><div class="value ' + diskClass + '">' + pct + '%</div></div>';
m1 += '<div class="card"><h3>Memory</h3><div class="value ' + memClass + '">' + mem + '%</div></div>';
m1 += '<div class="card"><h3>Messages</h3><div class="value blue">' + msgs + '</div></div>';

if(fi) {
  let load1m = fi.system ? safeNum(fi.system.load_1m, 0).toFixed(1) : '?';
  m1 += '<div class="card"><h3>CPU Load</h3><div class="value blue">' + load1m + '</div></div>';
  var upCount = fi.services ? fi.services.filter(function(s){return s.status==='up'}).length : '?';
  var totCount = fi.services ? fi.services.length : '?';
  m1 += '<div class="card"><h3>Services Up</h3><div class="value green">' + upCount + '/' + totCount + '</div></div>';
}

document.getElementById('metrics').innerHTML = m1;

var svcList = '';
if(hs.checks) hs.checks.forEach(function(c) {
  var ok = c.status === 'ok';
  svcList += '<div class="service"><span class="dot ' + (ok?'green':'red') + '"></span><span class="name">' + c.name + '</span><span class="badge ' + (ok?'ok':'err') + '">' + (ok?'OK':'DOWN') + '</span></div>';
});
document.getElementById('services-list').innerHTML = svcList;

if(ps.unexpected && ps.unexpected.length > 0) {
  document.getElementById('ports-list').innerHTML = '<div style="color:#f87171">Unexpected ports: ' + ps.unexpected.join(', ') + '</div>';
} else {
  document.getElementById('ports-list').innerHTML = '<div class="green">All ' + ps.total_open + ' ports are authorized</div>';
}
```

### Full-Audit Service List (Fixed)
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

### Port Scan AllowedPorts (Fixed)
```go
var allowedPorts = []int{
	22,     // SSH
	53,     // systemd-resolved DNS
	80,     // HTTP redirect
	443,    // HTTPS
	631,    // CUPS printing
	8080,   // simplex-node API
	8888,   // Dashboard
	17225,  // SimpleX bridge
	17001,  // DC P2P transport
	9050,   // Tor SOCKS
	9051,   // Tor Control
	10810,  // V2Ray SOCKS
	10808,  // V2Ray gRPC API
	10809,  // V2Ray gRPC
	10812,  // Native Xray VMess
	5349,   // coturn TLS
	3478,   // coturn
	8443,   // SMP relay
	4433,   // XFTP
	5223,   // SMP relay (alt)
	5224,   // SMP relay (alt)
	5225,   // SMP relay (alt)
	5226,   // SMP relay (alt)
	5230,   // SMP relay (alt)
	11434,  // Ollama API
	5432,   // PostgreSQL
	2018,   // acestream HTTP
	33827,  // ephemeral internal
}
```

## Persistent Daemons & Boot Autostart (WSL2)

When a Go/server process must survive terminal exit AND come back after Windows reboot:

### 1. systemd service (REQUIRED — nohup/setsid DO NOT survive)
**Pitfall**: `nohup ... &`, `setsid ... &`, `disown` all still die with `shutdown, signal: 15` in the log when the `wsl -d Distro -- bash -lc "..."` session exits — the whole process group gets SIGTERM. Only a systemd service survives.

```bash
# /etc/systemd/system/<app>.service
[Unit]
Description=...
After=docker.service network-online.target
Wants=network-online.target
[Service]
Type=simple
User=<linuxuser>
WorkingDirectory=/home/<linuxuser>/<app>
Environment=VAR=...
ExecStart=/home/<linuxuser>/bin/<app> <flags>
Restart=always
RestartSec=5
StandardOutput=append:/home/<linuxuser>/<app>.log
StandardError=append:/home/<linuxuser>/<app>.log
[Install]
WantedBy=multi-user.target
```
```bash
sudo cp <app>.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now <app>
systemctl is-active <app>   # verify
```
Verify survival: close the terminal / exit WSL session, reopen, `systemctl is-active <app>` must still be `active`.

### 2. Boot-before-login autostart (Windows Task Scheduler, SYSTEM principal)
Requires admin rights. From a NON-admin shell use the RunAs cmd-wrapper recipe (see `references/daemon-autostart-wsl2.md`):
- Task XML with `<BootTrigger>` + `<Delay>PT30S</Delay>` + `<UserId>S-1-5-18</UserId>` (SYSTEM) + `<RunLevel>HighestAvailable</RunLevel>`
- Create via `schtasks /Create /TN "Name" /XML "task.xml" /F` run through `Start-Process ... -Verb RunAs -Wait` with a `.cmd` wrapper writing output to a file (see reference — `-RedirectStandardOutput` CANNOT combine with `-Verb RunAs`)
- Russian Windows output is **cp866**: decode with `iconv -f cp866 -t utf-8`

### 3. On-login fallback (no admin needed — double insurance)
HKCU Run key + Startup folder `.lnk` (WScript.Shell COM), both pointing at `wsl.exe -d <Distro> -- /bin/true`. WSL boots → systemd starts → enabled service comes up.

### 4. WSL path mangling when passing Windows temp paths into WSL
`C:\Users\x\tmp\f.go` passed into `wsl bash -lc` loses backslashes (`C:Userstomas...`). Convert first: `/mnt/c/Users/x/tmp/f.go`. Bash heredocs also strip `\"` quotes — for Go test files prefer `write_file` to the Windows path (same file via bind mount), not heredoc.



### SMP Server — 4096-bit RSA Certificate Requirement
**Error**: `Error: unsupported HTTPS credentials, required 4096-bit RSA`
**Fix**: Regenerate cert with 4096-bit key:
```bash
openssl req -x509 -newkey rsa:4096 -keyout certificates/ParanoidX.local.key -out certificates/ParanoidX.local.crt -days 365 -nodes -subj '/CN=ParanoidX.local'
```

### SMP Server — Fingerprint File Generation
The SMP server generates fingerprint at `/etc/opt/simplex/fingerprint` on first run with `--init`. To pre-generate:
```bash
docker run --rm -e ADDR=ParanoidX.local -v /tmp/smp_test:/etc/opt/simplex simplexchat/smp-server:latest --init
# Copies fingerprint, ca.crt, ca.key, server.crt, server.key to mounted config dir
```

### SMP Server — Certificate Path in Config
**Error**: `Error: no HTTPS credentials: /certificates/ParanoidX.local.crt`
**Root Cause**: `smp-server.ini` has `cert = /certificates/...` but mounted volume is at `/etc/opt/simplex/certificates/`
**Fix**: Update `smp-server.ini`:
```ini
cert = /etc/opt/simplex/certificates/ParanoidX.local.crt
key = /etc/opt/simplex/certificates/ParanoidX.local.key
```

### Tor Hidden Service — Container Address for ICE
**Error**: `Unparseable address in hidden service port configuration`
**Root Cause**: Tor config used bare port `3478` instead of `ParanoidX-coturn:3478`
**Fix**: Update `tor/torrc`:
```
HiddenServicePort 3478 ParanoidX-coturn:3478
HiddenServicePort 5349 ParanoidX-coturn:5349
```

### Tor Hidden Service — SocksPort Conflict with HiddenServiceNonAnonymousMode
**Error**: `HiddenServiceNonAnonymousMode is incompatible with using Tor as an anonymous client. Please set Socks/Trans/NATD/DNSPort to 0, or revert HiddenServiceNonAnonymousMode to 0.`
**Root Cause**: Tor's `HiddenServiceNonAnonymousMode 1` (used for faster hidden services) conflicts with running a SOCKS5 proxy (`SocksPort 9050`) on the same instance.
**Fix**: Remove `HiddenServiceNonAnonymousMode 1` and `HiddenServiceSingleHopMode 1` from `torrc` if you need the SOCKS5 proxy:
```torrc
# REMOVE these lines:
# HiddenServiceSingleHopMode 1
# HiddenServiceNonAnonymousMode 1

# Keep:
SocksPort 9050
ControlPort 9051
```
This allows Tor to act as both a hidden service provider AND a SOCKS5 proxy for the chain.

### coturn — Missing Config Files
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

### SimpleX CLI Bridge — WebSocket Connection Required
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

### XFTP Server — Configuration
The XFTP server requires `ADDR` environment variable and quota. Ensure docker-compose has:
```yaml
xftp-server:
  environment:
    - ADDR=ParanoidX.local
    - QUOTA=20gb
```

## Directory Structure

```
C:\Project-data\          # Windows (shared)
~/Project/                # WSL2 source
~/bin/Project             # Built binary
```

## References

- `references/wsl2-hybrid-pattern.md`
- `references/powershell-encoding.md`
- `references/runonce-automation.md`
- `references/paranoidx-session-notes.md`
- `references/docker-container-fixes.md`
- `references/daemon-autostart-wsl2.md` — systemd service + boot-before-login task (SYSTEM principal, RunAs wrapper, cp866 decoding) + WSL path-mangling fixes
- `references/go-sync-pitfalls.md` — RWMutex reentrancy deadlock, map mutation data race, ad-hoc temp-test verification recipe
- `references/https-browser-access.md` — HTTPS self-signed cert, WSL2 interfaces, Windows browser access patterns

## Scripts

- `scripts/verify-wsl2-setup.ps1` — Run after setup to verify all components
- `scripts/fix-smp-certs.sh` — Regenerate SMP certs with 4096-bit RSA
- `scripts/fix-torrc-ice.sh` — Update torrc with container addresses
- `scripts/fix-coturn-config.sh` — Create coturn config and certs

## Directory Structure

```
C:\Project-data\          # Windows (shared)
~/Project/                # WSL2 source
~/bin/Project             # Built binary
```