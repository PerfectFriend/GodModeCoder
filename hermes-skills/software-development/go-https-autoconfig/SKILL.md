---
name: go-https-autoconfig
description: Auto-enable TLS for Go HTTP servers via cert/key in data dir
category: software-development
tags: [go, https, tls, http, server, wsl2]
version: 1.0.0
---

# Go HTTPS Auto-Configuration Pattern

## Trigger
Use when building a Go HTTP server that should optionally serve HTTPS if certificates are present in a data directory, without requiring external CA or complex config.

## Core Pattern

```go
// TLS config - auto-detect from data directory
certPath := filepath.Join(*dataDir, "certs", "cert.pem")
keyPath := filepath.Join(*dataDir, "certs", "key.pem")
useTLS := false

if _, err := os.Stat(certPath); err == nil {
    if _, err := os.Stat(keyPath); err == nil {
        useTLS = true
        slog.Info("TLS enabled", "cert", certPath, "key", keyPath)
    }
} else {
    slog.Info("TLS cert not found", "certPath", certPath, "err", err)
}

// Later: start server with or without TLS
slog.Info("serving", "addr", srv.Addr, "data", *dataDir, "tls", useTLS)
var err error
if useTLS {
    err = srv.ListenAndServeTLS(certPath, keyPath)
} else {
    err = srv.ListenAndServe()
}
if err != nil && err != http.ErrServerClosed {
    slog.Error("listen failed", "error", err)
}
```

## Certificate Generation (Self-Signed)

```bash
mkdir -p /path/to/data/certs
cd /path/to/data/certs
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:<wsl2-eth0-ip>,IP:<wsl2-lo-alias>"
```

## WSL2 Network Considerations

WSL2 has its own network stack. The server listening on `0.0.0.0:8080` is accessible via:

| Interface | IP | Accessible From |
|-----------|-----|-----------------|
| `lo` (WSL2) | `127.0.0.1` | Inside WSL2 only |
| `eth0` (WSL2) | `172.x.x.x` | **From Windows host** |
| `lo` alias | `10.255.255.254` | Inside WSL2 only |

**For Windows browser access:** Use the `eth0` IP (e.g., `https://172.25.101.187:8080`) or configure port forwarding:

```powershell
# Run as Administrator in PowerShell
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=127.0.0.1 connectport=8080 connectaddress=172.25.101.187
```

Then import `cert.pem` into Windows "Trusted Root Certification Authorities" via `certmgr.msc`.

## Pitfalls

1. **Indentation bugs** - The TLS config block must be at the same scope as `srv` declaration, not nested inside another block where `srv` isn't visible
2. **Certificate path resolution** - Use `filepath.Join(*dataDir, "certs", "cert.pem")` for cross-platform compatibility (Windows/WSL2 paths)
3. **SAN entries** - Include all IPs the server will be accessed from (127.0.0.1, WSL2 eth0 IP, WSL2 lo alias)
4. **Self-signed warnings** - Browsers will show "Not Secure" until cert is trusted. Import into OS trust store.
5. **WSL2 IP changes** - The eth0 IP may change after reboot. Update port forwarding rule or use dynamic detection.
6. **Browser hitting HTTP on HTTPS port** - Log shows `http: TLS handshake error from 127.0.0.1:XXXXX: client sent an HTTP request to an HTTPS server`. This means client (browser/curl without -k) is sending plain HTTP to TLS port. **Cause**: Browser cache, HSTS from previous HTTP run, or wrong URL (http:// instead of https://). **Fix**: Clear browser cache, use `https://` explicitly, test with `curl -k https://<ip>:8080` first.
7. **"Not Secure" but HTTPS works** - Self-signed cert causes browser warning, NOT connection failure. Connection IS encrypted (TLS 1.3). Check DevTools → Security tab: "Connection secure" + "Certificate: self-signed". Fix: Import cert.pem into Windows "Trusted Root CA" via `certmgr.msc` or `certutil -addstore -f ROOT cert.pem` (Admin).
8. **Windows localhost vs WSL2 localhost** - `https://127.0.0.1:8080` in Windows browser hits Windows loopback, NOT WSL2. **Fix**: Use `https://<wsl2-eth0-ip>:8080` (e.g. `https://172.25.101.187:8080`) or configure port forwarding: `netsh interface portproxy add v4tov4 listenport=8080 listenaddress=127.0.0.1 connectport=8080 connectaddress=172.25.101.187` (requires Admin).
9. **Cookie SameSite=Lax with cross-origin fetch** - If login page and API are on different origins (e.g., port forwarding), cookie may not send. **Fix**: Use `SameSite=None; Secure` in production, or ensure same origin.

## References

- `references/wsl2-network.md` — WSL2 networking deep dive
- `references/bip39-auth.md` — BIP39 authentication flow (related but separate)

## Related Skills

- `windows-dev-environment` — WSL2 setup prerequisites
- `paranoidx-dashboard-engineering` — Full ParanoidX dashboard implementation (user-owned)