---
name: paranoidx-auth-system
description: ParanoidX username auth with BIP39 mnemonic + invite.
---

# ParanoidX Auth System

## Trigger
Use when implementing or modifying the ParanoidX authentication system — username-based auth (no email), BIP39 seed phrase generation/recovery, universal unlimited invite, and HttpOnly cookie sessions.

## Architecture

### Core Components
1. **AuthManager** (`internal/auth/auth.go`) — User storage, password hashing, token management, invite validation
2. **API Handlers** (`internal/api/handlers.go`) — `/api/auth/register-with-invite`, `/api/auth/restore`, `/login`, `/api/auth/me`
3. **Frontend** (`ParanoidX-data/register.html`, `login.html`) — Two-tab registration (invite + seed restore), login form
4. **Data Files** (`ParanoidX-data/users.json`, `invites.json`) — JSON storage with mnemonic/pubkey fields

### Key Features
- **Username-only auth** — No email required, usernames 3-32 chars alphanumeric + `_-`
- **Universal unlimited invite** — Token `UNIVERSAL-UNLIMITED` with `max_uses: 0`, no expiration
- **BIP39 mnemonic** — 24-word seed generated on registration, stored with Ed25519 pubkey for recovery verification
- **Seed phrase recovery** — `/api/auth/restore` verifies mnemonic matches stored pubkey, allows password reset
- **HttpOnly cookie sessions** — 24h expiry, `SameSite=Lax`, auto-login after register/restore

## Cross-Platform Path Resolution (Critical)

The `-data` flag accepts both Windows (`C:\ParanoidX-data`) and WSL (`/mnt/c/ParanoidX-data`) paths. Invite file lookup must handle both:

```go
// Convert Windows C:\... to WSL /mnt/c/... and /c/... to /mnt/c/...
invitesFileWSL := invitesFile
if len(invitesFile) >= 3 && invitesFile[1] == ':' && invitesFile[2] == '\\' {
    drive := strings.ToLower(invitesFile[0:1])
    rest := strings.ReplaceAll(invitesFile[3:], "\\", "/")
    invitesFileWSL = "/mnt/" + drive + "/" + rest
} else if len(invitesFile) >= 3 && (invitesFile[0] == '/' || invitesFile[0] == '\\') &&
    (invitesFile[1] == 'c' || invitesFile[1] == 'C') &&
    (invitesFile[2] == '/' || invitesFile[2] == '\\') {
    rest := strings.ReplaceAll(invitesFile[3:], "\\", "/")
    invitesFileWSL = "/mnt/c/" + rest
}
// Try native path first, then WSL path
b, err := os.ReadFile(invitesFile)
if err != nil {
    b, err = os.ReadFile(invitesFileWSL)
}
```

## API Endpoints

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/login` | POST | form: username, password | Returns token, sets HttpOnly cookie |
| `/logout` | GET | — | Clears cookie, redirects to `/login` |
| `/api/auth/me` | GET | — | Returns username, role, force_password_change (requires auth) |
| `/api/auth/change-password` | POST | JSON: new_password | Requires auth |
| `/api/auth/register` | POST | JSON: username, password | Admin/no-invite registration |
| `/api/auth/register-with-invite` | POST | JSON: username, password, invite, mnemonic? | Validates invite, generates mnemonic if omitted |
| `/api/auth/restore` | POST | JSON: username, mnemonic, password | Verifies mnemonic→pubkey match, updates password |

## Frontend Patterns

**register.html** — Two tabs:
- **Register with Invite**: username, password, confirm, invite (prefilled `UNIVERSAL-UNLIMITED`), optional mnemonic textarea
- **Restore from Seed**: username, mnemonic (required), new password, confirm

Shows generated mnemonic prominently with numbered words and warning banner.

**login.html** — Simple username/password form, posts to `/login` with form encoding, redirects to `/` on success.

## Verification Script

See `scripts/verify-auth.py` for full test suite covering:
1. Register with universal invite → returns mnemonic + pubkey
2. Login → returns token + sets cookie
3. `/api/auth/me` → returns user info
4. Restore from seed → password reset
5. Login with new password works
6. Old password rejected
7. Invalid invite rejected
8. Dashboard accessible with version badge
9. API status endpoint works
9-24: All 16 dashboard tabs return real API data
25-27: UI pages (register, login, restore tab)
28-30: WSL2 interfaces (127.0.0.1, eth0, lo alias) — HTTPS
31-33: Restore flow (seed phrase recovery)

Run inside WSL:
```bash
python3 scripts/verify-auth.py --base https://127.0.0.1:8080 --insecure
```

## 2026-08-06 Session Update — Full Verification Complete (v2)

**Fresh ad-hoc verification: All auth flows + 16 dashboard tabs + sidechain APIs working**

### Core Auth Features Verified
- **Username-only auth** (no email) — usernames 3-32 chars alphanumeric + `_-`
- **Cryptographic invite tokens** — `secrets.token_hex(16)` → 32-char hex (128-bit entropy), RFC3339 timestamps, JSON lookup validation
- **GodMode invites** — Two unlimited admin tokens: `90dbad2056aeee01978ed62a553d7485`, `f4d96322178b6e6367be64ca2ef7cc6d`
- **BIP39 mnemonic generation** (24 words) on registration via `bip39.GenerateMnemonic()`
- **Custom seed phrase linking** — optional mnemonic on register, validated for 12/24 words + BIP39 checksum
- **Seed phrase restore + password recovery** via `/api/auth/restore` — verifies mnemonic→pubkey match
- **Old password invalidated** after restore
- **HttpOnly cookie sessions** — 24h expiry, `SameSite=Lax`, `credentials: 'include'` on all fetch calls
- **Dashboard version badge** — **A13** (auto-incremented by evolution cron)

### New Sidechain API Endpoints (for TLR/ARGENTUM/NT)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/wallet/keys` | GET | Returns `{mnemonic, pubkey, privkey}` for sidechain apps |
| `/api/wallet/verify-key` | POST | Validates pubkey for API access (`{"ok":true,"pubkey":"...","user":"..."}`) |
| `/api/auth/create-invite` | POST | Authenticated users create new tokens with custom expiry/uses/role |

### All 16 Dashboard Tabs — Real API Data (Verified via `/api/status`, cookie auth)
| Tab | API Endpoint | Verified |
|-----|--------------|----------|
| Wallet | `/api/wallet/state` | ✅ 8 denominations, 8 NFT slots, vault |
| VPN | `/api/vpn/configs` | ✅ 10 protocols (VMess, VLESS, Trojan, Shadowsocks, WireGuard, OpenVPN, Tor, SOCKS5, SSH, VLESS+Reality) |
| Treasury | `/api/treasury/state` | ✅ silver reserve, banknotes |
| AI Exchanger | `/api/wallet/exchange/quote` | ✅ TL↔NT rates, 2.28% fee |
| Radio | `/api/radio` | ✅ 5 stations (EN/RU/ES) |
| Marketplace | `/api/marketplace` | ✅ listings |
| Bridge | `/api/bridge/status` | ✅ SimpleX relay |
| Citizens | `/api/citizens` | ✅ heraldry/coat of arms |
| Vault | `/api/vault/list` | ✅ 16GB encrypted storage |
| System Status | `/api/status` | ✅ memory, disk, uptime, version |
| Subscription | `/api/subscription` | ✅ colonist tier |
| P2P | `/api/p2p/explore` | ✅ peer discovery |
| Containers | `/api/admin/docker` | ✅ docker status |
| Metrics | `/api/admin/metrics/system` | ✅ system metrics |
| Logs | `/api/admin/logs` | ✅ system logs |
| Invites | `/api/invite/list` | ✅ invite management |

### Frontend — Production Grade (No Simulations)
**login.html:**
- Eye toggle (👁️/🙈) at **far right** of password input (`position:absolute; right:10px`)
- `tabindex="-1"` on toggle prevents focus stealing — Tab moves only between username/password
- Submit button disables during request, shows "Signing in..."
- Enter key support on both fields
- Delegated click handler (no inline `onclick`)

**register.html:**
- Two tabs: **Register with Invite** + **Restore from Seed** — keyboard accessible (ArrowLeft/Right, Enter, Space)
- Eye toggles on **all 4** password fields (far right, `tabindex="-1"`)
- **No form clearing on error** — user input preserved, only error message shown
- Password mismatch → inline error, form stays filled
- Submit buttons disable during request: "Creating..." / "Restoring..."
- Real API calls to `/api/auth/register-with-invite` and `/api/auth/restore`
- Success: shows generated mnemonic with numbered words + warning banner, redirects to dashboard
- Restore tab: complete form with username, mnemonic (required), new password, confirm

### HTTPS Verified on All WSL2 Interfaces
| Interface | URL | Verified |
|-----------|-----|----------|
| WSL2 lo | `https://127.0.0.1:8080` | ✅ |
| WSL2 eth0 | `https://172.25.101.187:8080` | ✅ (Windows browser access) |
| WSL2 lo alias | `https://10.255.255.254:8080` | ✅ |

### Runtime Status
- WSL2 Ubuntu 24.04
- Binary: `/home/tomas/bin/ParanoidX`
- Data: `/mnt/c/ParanoidX-data`
- Port: 8080 (HTTPS with self-signed cert)
- TLS: TLS 1.3, cert in `/mnt/c/ParanoidX-data/certs/`

### Critical Fixes & Patterns (2026-08-06)
1. **Path mismatch** — Server `-data` flag accepts both Windows (`C:\ParanoidX-data`) and WSL (`/mnt/c/ParanoidX-data`). Invite/user file lookup must try both native and WSL-converted paths.
2. **Port conflicts** — Multiple ParanoidX instances on 8080. Kill existing: `pkill -f "ParanoidX.*8080"` (WSL) + `taskkill /F /IM ParanoidX.exe` (Windows)
3. **Cookie not sent** — Frontend **must** use `credentials: 'include'` on all fetch calls
4. **Mnemonic validation** — Uses BIP39 checksum; test mnemonic "abandon x11 + about" fails. Generate real mnemonics via `bip39.GenerateMnemonic()`
5. **Invite consumption** — `max_uses: 0` = unlimited (no consumption), `max_uses > 0` = limited, tracked via `uses` counter
6. **Eye toggle position** — **Far right** of input (`right:10px`), `tabindex="-1"` prevents focus stealing, delegated event handler
7. **Tab switching** — No focus stealing, keyboard accessible, ARIA roles
8. **No form clearing on error** — Preserve user input, only show error message
9. **Version badge** — Incremented by evolution cron (`scripts/evolution_cycle.py`), visible in dashboard header

## Build & Deploy

```bash
# Windows (build)
cd C:\\ParanoidX && go build -o ./ParanoidX ./cmd/ParanoidX

# WSL (run)
wsl -- bash -c 'pkill -f "ParanoidX.*8080"; sleep 2; nohup /home/tomas/bin/ParanoidX -data /mnt/c/ParanoidX-data -listen 0.0.0.0:8080 > /tmp/paranoidx.log 2>&1 & sleep 6'

# Verify
python3 scripts/verify-auth.py --base https://172.25.101.187:8080 --insecure
```

## References
- `references/bip39-integration.md` — BIP39 entropy/checksum/keypair derivation details
- `references/cross-platform-paths.md` — Windows/WSL path normalization patterns
- `references/invite-system.md` — Invite JSON structure, validation logic, cryptographic token design
- `references/sidechain-api.md` — `/api/wallet/keys`, `/api/wallet/verify-key`, `/api/auth/create-invite` for TLR/ARGENTUM/NT

## Templates
- `templates/register.html` — Two-tab registration with seed phrase restore, eye toggles, real API calls
- `templates/login.html` — Username/password login with eye toggle, HttpOnly cookie, real API call

## Scripts
- `scripts/verify-auth.py` — Complete auth flow verification (core auth + all 16 dashboard tabs + sidechain APIs + frontend pages + HTTPS on WSL2 interfaces)

## References
- `references/bip39-integration.md` — BIP39 entropy/checksum/keypair derivation details
- `references/cross-platform-paths.md` — Windows/WSL path normalization patterns
- `references/invite-system.md` — Invite JSON structure, validation logic, unlimited invite design

## Templates
- `templates/register.html` — Two-tab registration with seed phrase restore
- `templates/login.html` — Username/password login with HttpOnly cookie

## Scripts
- `scripts/verify-auth.py` — Complete auth flow verification (40 tests: core auth + all 16 dashboard tabs + frontend pages)