# WSL2 Network Gotcha — 127.0.0.1 vs eth0 IP (2026-08-06)

## Problem
WSL2 has its own isolated network stack. `127.0.0.1` inside WSL2 ≠ `127.0.0.1` in Windows.

## Server Binding
Server binds to `0.0.0.0:8080` — accessible at multiple interfaces:

| Interface | IP | Accessible From |
|-----------|-----|-----------------|
| `lo` (WSL2) | `127.0.0.1:8080` | Inside WSL2 only |
| `eth0` (WSL2) | `172.25.101.187:8080` | **From Windows** |
| `lo` (WSL2) | `10.255.255.254:8080` | Inside WSL2 |

## For Windows Browser
Use the eth0 IP: `http://172.25.101.187:8080`

Get current IP:
```bash
wsl -- bash -c 'ip addr show eth0 | grep "inet " | awk "{print \$2}" | cut -d/ -f1'
```

## Permanent Fix — Port Forwarding (run once as admin in PowerShell)
```powershell
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=127.0.0.1 connectport=8080 connectaddress=172.25.101.187
```

After this, `http://127.0.0.1:8080` works from Windows.

## Verification
```bash
# From WSL2
curl -s http://127.0.0.1:8080/login.html

# From Windows (PowerShell)
curl.exe -s http://172.25.101.187:8080/login.html
curl.exe -s http://127.0.0.1:8080/login.html  # only works after portproxy
```