# Session 2026-08-05 Implementation Details

## Summary
Recovered dead ParanoidX node after WSL reboot (Docker containers stopped), fixed xray port check (10812 vs 10810), implemented:
1. Forced password change on `123456`
2. Invite-only registration with token management
3. 10 VPN protocol configs (vmess, vless, vless_reality, trojan, shadowsocks, wireguard, openvpn, tor, socks5, ssh)
4. Single 27KB dashboard.html with all 16 tabs functional

## Files Created/Modified

### Backend
- `internal/auth/invites.go` — InviteStore (142 lines)
- `internal/vpn/vpn.go` — VPN Manager with 10 protocols (116 lines)
- `cmd/ParanoidX/feature_routes.go` — All new API routes (auth register with invite, invite CRUD, VPN config CRUD)
- `cmd/ParanoidX/auth_routes.go` — Removed duplicate `/api/auth/register` (conflicted with feature_routes.go)
- `cmd/ParanoidX/main.go` — Added `registerFeatureRoutes()` + `registerInviteAwareRegister()`
- `internal/api/admin.go` — Fixed xray port check: 10810 → 10812 (2 locations)

### Dashboard
- `C:\ParanoidX-data\dashboard.html` — Single file, 27KB, 16 tabs, node --check passes

## Docker Recovery
After WSL reboot (due to .wslconfig memory change):
```bash
# Containers were stopped, not removed
docker ps -a --format "{{.Names}} {{.Status}}"
docker compose -f ~/ParanoidX/docker/docker-compose.yml up -d
# All 5 containers healthy: tor, v2ray, coturn, simplex-bridge, (no postgres)
```

## Port Status (post-recovery)
| Service | Ports | Status |
|---------|-------|--------|
| Tor | 9050 (SOCKS), 9051 (Control) | ✅ |
| V2Ray (Docker) | 10808, 10809 | ✅ |
| Native Xray VMess | 10812 | ✅ |
| Coturn | 3478, 5349 (TCP/UDP) | ✅ |
| SMP | 5223 | ✅ |
| XFTP | 5225 | ✅ |
| P2P Transport | 17001 | ✅ |
| SimpleX Bridge | 17225 | ✅ |
| API | 8080 | ✅ |

## API Endpoints Verified
```
GET  /api/health                   → healthy: false (ollama down), bridge: true
GET  /api/admin/full-audit         → all services up except ollama
POST /login (123456)               → 302 Location: /change-password, force: true
POST /api/invite/create (admin)    → returns token (16 hex chars)
POST /api/auth/register (invite)   → 200 created
POST /api/auth/register (no invite)→ 403
POST /api/invite/revoke            → consumes invite
GET  /api/vpn/protocols            → 10 protocols
GET  /api/vpn/configs              → 10 configs
PUT  /api/vpn/config/:type         → saves config
```

## Build & Deploy
```bash
# Build from CORRECT dir
cd /mnt/c/Users/tomas/ParanoidX-backup/codebase
go build -o /home/tomas/bin/ParanoidX ./cmd/ParanoidX/

# Restart systemd
sudo systemctl restart paranoidx
systemctl is-active paranoidx  # → active

# Verify dashboard served from RIGHT path
curl -s http://127.0.0.1:8080/ | md5sum
md5sum /mnt/c/ParanoidX-data/dashboard.html  # must match
```

## Key Learnings
- **Duplicate route registration kills server** (Go 1.22+ panic). Remove old handler before adding new one.
- **`strings` import unused after removing handler** → remove import.
- **Dashboard file path trap**: server serves `C:\ParanoidX-data\dashboard.html`, NOT `C:\Users\tomas\ParanoidX-data\dashboard.html`. Always verify with md5sum.
- **WSL reboot kills Docker containers** — they don't auto-restart. Need compose up after every WSL restart.
- **xray native port is 10812** — hardcoded 10810 in admin.go was wrong.

## Next Steps (if needed)
- Add systemd dependency on docker.service so containers start before paranoidx
- Or add `ExecStartPre=docker compose -f /home/tomas/ParanoidX/docker/docker-compose.yml up -d` to service unit
- Implement actual VPN protocol connections (currently just config storage)
- Add auto-restart of Docker containers via systemd drop-in