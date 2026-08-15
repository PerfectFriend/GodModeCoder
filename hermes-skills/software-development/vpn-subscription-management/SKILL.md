---
name: vpn-subscription-management
description: Parse v2rayNG/clash subs → auto-integrate VPN configs.
trigger: Need to ingest subscription URLs, parse server configs, merge into VPN manager.
---
# VPN Subscription Management (v2rayNG/clash compatible)

## Overview
Handles subscription URLs from GitHub, Telegram, or custom sources. Parses base64-encoded payloads and URI schemes (vmess://, vless://, trojan://, ss://, wireguard://). Auto-fetches on schedule or manual trigger, merges parsed servers into VPN config manager.

## Core Components

### SubscriptionManager (`internal/vpn/vpn.go`)
- **Storage**: JSON file (`vpn_subscriptions.json`) with name, URL, enabled, last_fetched, server_count, error
- **FetchAndParse(name)**: Downloads with 30s timeout, User-Agent "v2rayNG/1.8.5 (ParanoidX)", tries std/URL base64 decode
- **parseSubscription(raw)**: Splits lines, skips comments/empty, dispatches to parseSingleConfig
- **parseSingleConfig(uri)**:
  - `vmess://` → base64 decode → JSON parse → extract add, port, id, ps (name)
  - `vless://`, `trojan://`, `ss://` → URL parse → scheme→type, host:port, fragment=name
  - `wireguard://` → custom handler
  - Clash YAML: not handled line-by-line (multi-line)

### API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/vpn/subscriptions` | List all subscriptions |
| POST | `/api/vpn/subscriptions` | Add subscription (url, name?, enabled?) |
| POST | `/api/vpn/subscriptions/{name}` | Fetch & parse, auto-add to VPN configs |
| DELETE | `/api/vpn/subscriptions/{name}` | Remove subscription |
| POST | `/api/vpn/subscriptions/fetch-all` | Fetch all enabled subscriptions |

### Frontend (dashboard.html)
Bridge & VPN tab → "VPN Subscriptions" section:
- Add form: URL input + optional name
- List: name, server count, last fetch, error, Fetch Now/Delete buttons
- "Fetch All Enabled Subscriptions" bulk button

## Verification Commands
```bash
# Add subscription
curl -b cookies.txt -X POST http://localhost:8080/api/vpn/subscriptions \
  -H "Content-Type: application/json" \
  -d '{"url":"https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub","name":"pawdroid-free","enabled":true}'

# Fetch & parse
curl -b cookies.txt -X POST http://localhost:8080/api/vpn/subscriptions/pawdroid-free

# Verify parsed configs added
curl -b cookies.txt http://localhost:8080/api/vpn/configs
```

## Session 2026-08-05 Implementation Details

### Exact API Endpoints Created
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/vpn/subscriptions` | user | List all subscriptions |
| POST | `/api/vpn/subscriptions` | user | Add `{url, name?, enabled?}` |
| POST | `/api/vpn/subscriptions/{name}` | user | Fetch & parse → auto-add to VPN Manager |
| DELETE | `/api/vpn/subscriptions/{name}` | user | Remove subscription |
| POST | `/api/vpn/subscriptions/fetch-all` | user | Fetch all enabled subscriptions |

### Parse Flow Implementation
```go
// SubscriptionManager in internal/vpn/vpn.go
func (m *SubscriptionManager) FetchAndParse(name string) ([]*Config, error) {
    // 1. GET URL with 30s timeout, UA "v2rayNG/1.8.5 (ParanoidX)"
    // 2. Try base64.StdEncoding.DecodeString, then URLEncoding
    // 3. Split by \n, skip empty/comment lines
    // 4. parseSingleConfig per line
}

func parseSingleConfig(uri string) *Config {
    switch {
    case strings.HasPrefix(uri, "vmess://"):
        // base64 decode → JSON → extract add, port, id, ps
    case strings.HasPrefix(uri, "vless://"), strings.HasPrefix(uri, "trojan://"), strings.HasPrefix(uri, "ss://"):
        // url.Parse → scheme→type, host:port, fragment=name
    case strings.HasPrefix(uri, "wireguard://"):
        // custom handler
    }
}
```

### Dashboard UI (Bridge tab)
- Add form: URL input + optional name
- List: name, server count, last fetch, error, Fetch Now/Delete buttons
- "Fetch All Enabled Subscriptions" bulk button

### Verified Live (2026-08-05)
- Pawdroid GitHub sub → 13 servers parsed
- 9 vmess/vless/trojan/ss auto-added to VPN configs
- tor/wg/ovpn/socks5 remain manual (no URI scheme)
- Health check: `xray_native` port 10812 OK

## Pitfalls & Fixes
- **vmess base64 padding**: Use `base64.StdEncoding.DecodeString` then `URLEncoding` fallback
- **vless/trojan/ss as URLs**: `url.Parse` handles query params (security, sni, type, headerType, etc.)
- **ss:// scheme**: Maps to `shadowsocks` type internally
- **Duplicate servers**: VPN manager upserts by type+name — safe to re-fetch
- **GitHub raw URLs**: Work directly, no auth needed for public repos
- **Base64 subscription payloads**: Single string with newlines → decode → split lines

## Integration Points
- VPN configs auto-added via `vpnMgr.Set(cfg)` after fetch
- Toggle/enable/disable per protocol via `/api/vpn/toggle`
- Health checks include `xray_native` (port 10812) — verify after adding servers

## Future Extensions
- Clash YAML parsing (multi-line, proxies: array)
- Subscription auto-refresh cron (hourly/daily)
- Latency testing & auto-sort by ping
- Export to Sing-box / Clash / Surge formats