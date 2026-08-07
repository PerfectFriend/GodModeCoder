# TLS Auto-Detection Reference

## Implementation in main.go

Auto-TLS detection occurs during server startup:

```go
// TLS config
certPath := filepath.Join(*dataDir, "certs", "cert.pem")
keyPath := filepath.Join(*dataDir, "certs", "key.pem")
useTLS := false
if _, err := os.Stat(certPath); err == nil {
    if _, err := os.Stat(keyPath); err == nil {
        useTLS = true
        slog.Info("TLS enabled", "cert", certPath, "key", keyPath)
    }
}
```

## Certificate Requirements

- Path: `{dataDir}/certs/cert.pem` and `{dataDir}/certs/key.pem`
- Self-signed X.509 with RSA 2048-bit key
- SAN must include: localhost, 127.0.0.1, WSL2 eth0 IP, 10.255.255.254
- Valid for 365 days

## Server Startup

```go
if useTLS {
    err := srv.ListenAndServeTLS(certPath, keyPath)
} else {
    err := srv.ListenAndServe()
}
```

## Log Messages

- `TLS enabled` - certs found and loaded
- `TLS cert not found` - certs missing, falling back to HTTP

## Regenerating Certs

```bash
mkdir -p /mnt/c/ParanoidX-data/certs
cd /mnt/c/ParanoidX-data/certs
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:172.25.101.187,IP:10.255.255.254"
# Rebuild and restart server
```