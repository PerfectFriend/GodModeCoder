# Dashboard.js Fix Pattern — Reusable Template

## Problem
Dashboard showed incorrect metrics:
- "Services Up 3/5" instead of actual count
- Disk usage: 0%
- Memory usage: 0%
- White screen when dashboard.html corrupted

## Root Causes
1. Dashboard JS fetched `/api/health` (minimal) instead of `/api/admin/full-audit` for disk/memory/services
2. `fi.system.load_1m` was a string, `.toFixed()` failed on string
3. `fi.disk.used_pct` and `fi.system.ram_used_pct` could be strings
4. `dashboard.html` corrupted to 107 bytes (only DOCTYPE line)

## Solution Pattern

### 1. Safe Numeric Helper (Required)
```javascript
function safeNum(val, def) {
  if (val === undefined || val === null) return def;
  const n = parseFloat(val);
  return isNaN(n) ? def : n;
}
```

### 2. Fetch 4 Endpoints in Parallel
```javascript
let h = await fetch('/api/health').then(r=>r.json());
let hs = await fetch('/api/health/checks').then(r=>r.json());
let ps = await fetch('/api/admin/port-scan').then(r=>r.json());
let fi = await fetch('/api/admin/full-audit').then(r=>r.json());
```

### 3. Safe Numeric Extraction
```javascript
let uptime = h.uptime_hours ? safeNum(h.uptime_hours, 0).toFixed(1) : '0';
let pct = fi.disk ? safeNum(fi.disk.used_pct, 0).toFixed(1) : '0';
let mem = fi.system ? safeNum(fi.system.ram_used_pct, 0).toFixed(1) : '0';
let msgs = safeNum(h.messages, 0);
let load1m = fi.system ? safeNum(fi.system.load_1m, 0).toFixed(1) : '?';
```

### 4. Dynamic Services Count
```javascript
var upCount = fi.services ? fi.services.filter(function(s){return s.status==='up'}).length : '?';
var totCount = fi.services ? fi.services.length : '?';
```

### 5. Services List from Health Checks
```javascript
var svcList = '';
if(hs.checks) hs.checks.forEach(function(c) {
  var ok = c.status === 'ok';
  svcList += '<div class="service"><span class="dot ' + (ok?'green':'red') + '"></span><span class="name">' + c.name + '</span><span class="badge ' + (ok?'ok':'err') + '">' + (ok?'OK':'DOWN') + '</span></div>';
});
document.getElementById('services-list').innerHTML = svcList;
```

### 6. Port Scan Results
```javascript
if(ps.unexpected && ps.unexpected.length > 0) {
  document.getElementById('ports-list').innerHTML = '<div style="color:#f87171">Unexpected ports: ' + ps.unexpected.join(', ') + '</div>';
} else {
  document.getElementById('ports-list').innerHTML = '<div class="green">All ' + ps.total_open + ' ports are authorized</div>';
}
```

## Full-Audit Service List (Canonical)
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

## Port Scan AllowedPorts (Canonical)
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

## Dashboard.html Corruption Recovery
If `dashboard.html` is corrupted (107 bytes, only DOCTYPE):
```bash
# Copy from Windows source of truth
cp /mnt/c/Users/tomas/ParanoidX-data/dashboard.html /mnt/c/ParanoidX-data/dashboard.html

# Or write correct version directly
cat > /mnt/c/ParanoidX-data/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<!-- ... full 5000+ byte version ... -->
EOF
```

## Prevention
- Write dashboard.html to Windows path `C:\Users\tomas\ParanoidX-data\dashboard.html` (source of truth for bind mount)
- Use `safeNum()` helper for all numeric API responses
- Always fetch `/api/admin/full-audit` for disk/memory/services metrics