# HTTPS Browser Access from Windows to WSL2

## The Problem

WSL2 has its own network stack. A server listening on `0.0.0.0:8080` inside WSL2 is accessible at:
- `https://127.0.0.1:8080` — **inside WSL2 only**
- `https://172.25.101.187:8080` — **from Windows host** (eth0 IP)
- `https://10.255.255.254:8080` — **inside WSL2 only** (lo alias)

**Windows browser at `https://127.0.0.1:8080` hits Windows loopback, NOT WSL2.** Connection fails.

## Solutions

### Option 1: Use WSL2 eth0 IP Directly (No Admin Required
```
https://172.25.101.187:8080/login.html
```
Get current IP: `wsl -- ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1`

### Option 2: Port Forwarding (Requires Admin)
```powershell
# PowerShell as Administrator
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=127.0.0.1 connectport=8080 connectaddress=172.25.101.187
```
Then: `https://localhost:8080/login.html` works from Windows.

### Option 3: HTTPS Self-Signed Certificate Trust
Even with correct URL, browser shows "Not Secure" for self-signed cert.

**Import cert.pem into Windows Trusted Root CA:**
```cmd
# 1. Copy cert to Windows
copy \\wsl$\Ubuntu\mnt\c\ParanoidX-data\certs\cert.pem C:\cert.pem

# 2. Import (Admin cmd)
certutil -addstore -f "ROOT" "C:\cert.pem"

# 3. Verify
certutil -store ROOT | findstr localhost
```
Or via PowerShell Admin:
```powershell
Import-Certificate -FilePath "C:\cert.pem" -CertStoreLocation "Cert:\LocalMachine\Root"
```

## Common Browser Errors & Meaning

| Browser Message | Real Cause | Fix |
|----------------|------------|-----|
| "Connection refused" / "Can't connect" | Wrong IP (Windows localhost) | Use `https://172.25.101.187:8080` or portproxy |
| "Not Secure" (red warning) | Self-signed cert | Import cert.pem to Trusted Root CA |
| "Connection error" in fetch | Mixed content / CORS / SameSite | Use `credentials: 'include'`, check Origin |
| TLS handshake error in server log | Client sending HTTP to HTTPS port | Clear browser cache, use `https://` explicitly |

## Verification Commands

```bash
# Inside WSL2 - verify server listening on TLS
ss -tlnp | grep :8080
# Should show: LISTEN 0 4096 *:8080 users:(("ParanoidX",pid=XXXXX,fd=XX))

# From WSL2 - test all interfaces
curl -k https://127.0.0.1:8080/login.html
curl -k https://172.25.101.187:8080/login.html
curl -k https://10.255.255.254:8080/login.html

# From Windows cmd
curl -k https://172.25.101.187:8080/login.html
```

## Server Log Indicators

**Good (TLS working):**
```
listening addr=0.0.0.0:8080 data=/mnt/c/ParanoidX-data tls=true
serving addr=0.0.0.0:8080 data=/mnt/c/ParanoidX-data tls=true
```

**Client error (not server error):**
```
http: TLS handshake error from 127.0.0.1:XXXXX: client sent an HTTP request to an HTTPS server
```
This means HTTPS IS working — a client sent plain HTTP to the TLS port.

## 2026-08-06 Session: ParanoidX Full Verification

**Result: 40/40 tests PASSED including HTTPS on all 3 WSL2 interfaces**

| Test | URL | Result |
|------|-----|--------|
| Login page | `https://127.0.0.1:8080/login.html` | ✅ |
| Login page | `https://172.25.101.187:8080/login.html` | ✅ |
| Login page | `https://10.255.255.254:8080/login.html` | ✅ |
| Register + Login + Dashboard | All interfaces | ✅ |
| All 16 dashboard tabs | All interfaces | ✅ |

**Certificate:** Self-signed, 365 days, SAN: `localhost, 127.0.0.1, 172.25.101.187, 10.255.255.254`
**TLS:** TLS 1.3
**Server:** Go `http.Server.ListenAndServeTLS` with auto-detect from `/data/certs/`