# WSL2 Networking for Go Services

## The Problem
WSL2 runs a real Linux kernel with its own network stack, separate from Windows. This creates a common confusion:

```
┌─────────────────────────────────────────────────────────────────┐
│  Windows Host (192.168.1.x)                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ WSL2 VM (172.25.101.187/20)                              │  │
│  │   lo:      127.0.0.1        ← localhost INSIDE WSL2      │  │
│  │   eth0:    172.25.101.187   ← Windows reaches WSL2 HERE  │  │
│  │   lo alias: 10.255.255.254  ← Additional WSL2 address    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Implications

| From | To | Works? |
|------|-----|--------|
| Windows browser | `localhost:8080` | ❌ No - hits Windows loopback |
| Windows browser | `172.25.101.187:8080` | ✅ Yes - reaches WSL2 eth0 |
| WSL2 curl | `localhost:8080` | ✅ Yes - hits WSL2 loopback |
| WSL2 curl | `172.25.101.187:8080` | ✅ Yes - hits WSL2 eth0 |

## Solution 1: Port Forwarding (Recommended for Dev)
```powershell
# Run as Administrator in PowerShell
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=127.0.0.1 connectport=8080 connectaddress=172.25.101.187
```
Then `https://localhost:8080` works from Windows browser.

## Solution 2: Use WSL2 IP Directly
```bash
# Get current WSL2 eth0 IP
wsl -- ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
# Use in browser: https://172.25.101.187:8080
```

## Certificate SAN Requirements
For self-signed certs to work without browser warnings on all access paths, include ALL IPs in SAN:
```
subjectAltName=DNS:localhost,IP:127.0.0.1,IP:172.25.101.187,IP:10.255.255.254
```

## Dynamic IP Handling
WSL2 eth0 IP changes on reboot. Options:
1. Re-run port forwarding after reboot
2. Use a script to detect and update
3. Configure static IP in `.wslconfig` (advanced)

## Verification Commands
```bash
# Inside WSL2 - check server listening
ss -tlnp | grep :8080

# From Windows - test connectivity
curl -k https://172.25.101.187:8080/login.html
curl -k https://localhost:8080/login.html  # Only works with port forwarding
```