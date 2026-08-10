---
name: go-web-dashboard-auth
description: Go dashboard with auth, version badges, wallet/VPN APIs.
trigger: Building Go web services with dashboard UI, auth flow, version badges, wallet/VPN/treasury APIs
---

# Go Web Dashboard with Auth Flow

## Overview
Class-level skill for building Go web services that serve a dashboard UI with authentication flow: unauthenticated users get a login page, authenticated users get the full dashboard with version badge in header.

## Core Patterns

### 1. Auth Flow (Login Page → Protected Dashboard)
- **Root handler (`/`)** checks for `dashboard_token` cookie
- **No cookie/invalid token** → serve `login.html` (not 401 text)
- **Valid token** → set `X-User` header, serve `dashboard.html`
- **Login endpoint (`/login`)** accepts form-data POST, returns session cookie
- **Logout endpoint (`/logout`)** clears cookie, redirects to `/login`

### 2. Version Badge System
- **Dashboard badge**: `<span class="version-badge" id="dashVersion">A04</span>` in sidebar brand area
- **Login page badge**: Same badge in bottom-right corner
- **Increment on every evolution cycle**: A00 → A01 → A02 → A03 → A04...
- **CSS**: Gold background, dark text, top-right positioning

### 3. Single Source of Truth
```
C:\ParanoidX\          # Go source (single codebase)
C:\ParanoidX-data\     # Data + dashboard.html + login.html
```
- Delete/rename duplicate dashboard copies in other folders
- Go binary reads `dashboard.html` and `login.html` from data directory

### 4. Wallet/VPN/Treasury API Endpoints
| Endpoint | Purpose |
|----------|---------|
| `/api/wallet/state` | Full wallet state (TL, NT, NFTs, vault, denominations) |
| `/api/wallet/send` | Send TL to address |
| `/api/wallet/receive` | Get receive address/QR |
| `/api/wallet/history` | Transaction history |
| `/api/wallet/exchange/quote` | Exchange rate with 2.28% fee |
| `/api/wallet/exchange` | Execute exchange |
| `/api/vpn/protocols` | 10 supported protocols |
| `/api/vpn/configs` | VPN configs CRUD |
| `/api/vpn/subscriptions` | Subscription CRUD + fetch/parse |
| `/api/treasury/supply` | TL supply state |
| `/api/treasury/entries` | Audit trail |

### 5. Ad-hoc Verification Scripts
- Create Python scripts in `C:\Users\tomas\AppData\Local\Temp\hermes-verify-aXX.py`
- Test: login → dashboard → all APIs → version badge
- Run via WSL: `wsl -d Ubuntu-24.04 -- bash -c 'python3 /mnt/c/Users/tomas/AppData/Local/Temp/hermes-verify-aXX.py'`
- Delete after verification

## Pitfalls & Fixes

| Issue | Fix |
|-------|-----|
| Dashboard returns "unauthorized" text | Serve `login.html` for unauthenticated GET `/` |
| Duplicate route `/api/wallet/state` | Register wallet routes **once** via `RegisterWalletRoutes()` |
| Wallet state 404 | Implement `RegisterWalletRoutes()` with full wallet state |
| Version badge not updating | Update both `dashboard.html` AND `login.html` |
| Multiple dashboard copies | Consolidate to `C:\ParanoidX-data\dashboard.html` only |

## File Structure
```
C:\ParanoidX\
├── cmd\ParanoidX\main.go          # Root handler with auth flow
├── internal\api\wallet.go         # RegisterWalletRoutes()
├── internal\auth\auth.go          # AuthMiddleware, ValidateToken
└── internal\api\handlers.go       # LoginHandler, LogoutHandler, RegisterHandler

C:\ParanoidX-data\
├── dashboard.html                 # Dashboard with version badge
├── login.html                     # Login page with version badge
├── dashboard_token cookie         # Session cookie
└── users.json                     # User store
```

## Verification Checklist
- [ ] Unauthenticated GET `/` → login page (not 401)
- [ ] Login POST → cookie set → redirect to `/`
- [ ] Authenticated GET `/` → dashboard with version badge
- [ ] Version badge visible in sidebar (A04)
- [ ] Wallet state API returns 8 denominations
- [ ] Wallet exchange returns rate 1.0, fee 2.28%
- [ ] VPN APIs return 10 protocols
- [ ] All 16 tabs APIs functional

## Related Skills
- `windows-dev-environment` - Windows Go setup
- `software-development` - General Go patterns