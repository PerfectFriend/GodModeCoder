# WSL2 Networking Reference

## Key Concept: WSL2 Has Its Own Network Stack

WSL2 runs a real Linux kernel with its own network namespace. This means:

- `127.0.0.1` inside WSL2 ≠ `127.0.0.1` in Windows
- WSL2 gets its own IP on a virtual ethernet adapter (`eth0`)
- Windows accesses WSL2 services via the WSL2 IP, not localhost

## Network Interfaces

| Interface | IP Range | Purpose |
|-----------|----------|---------|
| `lo` (loopback) | `127.0.0.1/8`, `10.255.255.254/32` | Internal WSL2 only |
| `eth0` | `172.25.x.x/20` (dynamic) | Windows ↔ WSL2 communication |

## Getting Current WSL2 IP

```bash
# From Windows:
wsl -- ip addr show eth0 | grep "inet "

# From inside WSL2:
ip addr show eth0 | grep "inet "
```

Example output: `inet 172.25.101.187/20 brd 172.25.111.255 scope global eth0`

## Port Access

| From | To | Works? |
|------|-----|--------|
| Windows browser | `https://172.25.101.187:8080` | ✅ Yes |
| Windows browser | `https://127.0.0.1:8080` | ❌ No (different namespace) |
| WSL2 curl | `https://127.0.0.1:8080` | ✅ Yes |
| WSL2 curl | `https://172.25.101.187:8080` | ✅ Yes |

## Port Forwarding (Optional)

If you want `https://127.0.0.1:8080` to work from Windows:

```powershell
# Run as Administrator:
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=127.0.0.1 connectport=8080 connectaddress=172.25.101.187
```

Remove:
```powershell
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=127.0.0.1
```

## IP Changes on Reboot

WSL2 `eth0` IP is assigned via DHCP and **changes on reboot**. Solutions:

1. **Use current IP each time** (recommended): `wsl -- ip addr show eth0 | grep inet`
2. **Static IP in `.wslconfig`**: Add to `C:\Users\<user>\.wslconfig`:
   ```ini
   [wsl2]
   networkingMode=mirrored
   ```
   (Requires Windows 11 22H2+)

## Certificate SAN

Include all possible IPs in cert:
```
subjectAltName=DNS:localhost,IP:127.0.0.1,IP:172.25.101.187,IP:10.255.255.254
```

Regenerate cert if eth0 IP changes significantly.