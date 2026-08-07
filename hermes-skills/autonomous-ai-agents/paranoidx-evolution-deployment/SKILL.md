---
name: paranoidx-evolution-deployment
description: Deploy/verify ParanoidX evolution cycles w/ version badges.
trigger: Use when deploying/verifying ParanoidX evolution cycles with version badges.
category: autonomous-ai-agents
---
# ParanoidX Autonomous Evolution Deployment & Verification

## Version Badge System
- Dashboard header gold badge: A00, A01, A02... (CSS: `.version-badge #dashVersion`)
- Increment on each cycle in `C:\ParanoidX-data\dashboard.html`

## Single Source of Truth
```
C:\ParanoidX\          # Go source (cmd/, internal/)
C:\ParanoidX-data\     # Dashboard HTML, SQLite DBs, static assets
D:\backups\            # Timestamped backups
```
Delete duplicates: `C:\Users\tomas\ParanoidX*`, `C:\C\`

## Evolution Cycle
1. Backup → `tar -czf D:\backups\paranoidx-<ts>.tar.gz C:\ParanoidX C:\ParanoidX-data`
2. Edit in `C:\ParanoidX\` only
3. Build → `wsl -d Ubuntu-24.04 -- bash -c 'cd /mnt/c/ParanoidX && go build -o /home/tomas/bin/ParanoidX ./cmd/ParanoidX'`
4. Deploy → restart with `-data /mnt/c/ParanoidX-data`
5. Verify → run full API test suite
6. Increment version badge in `dashboard.html`
7. Backup again

## Required Components (All Must Work)
| Component | Verification |
|-----------|--------------|
| Dashboard | Version badge visible, 16 tabs render real API data |
| Auth | POST /login → cookie → /api/auth/me → change pwd → invite register |
| VPN | 10 protocols, configs CRUD, 5+ subs, 27+ servers |
| Treasury | Supply, silver deposit (70/30), dividends |
| Wallet | AI Exchanger quote/execute (2.28% fee, TL↔USDT) |
| Heraldry | Coat of arms (citizen gate), flag watermark (0.08) |
| Tor HS | `.onion` via SOCKS5 9050 |
| Health | 18+ checks pass, all Docker UP |

## Verification Protocol
```bash
# HTTPS (self-signed TLS, WSL2 IP)
curl -k -c /tmp/cookies.txt -X POST https://172.25.101.187:8080/login -d 'username=...&password=...'
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/auth/me
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/vpn/configs
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/treasury/state
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/wallet/exchange/quote?from=TL&to=NT
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/radio
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/marketplace
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/bridge/status
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/citizens
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/vault/list
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/status
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/subscription?pubkey=...
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/wallet/keys       # Sidechain keys
curl -k -b /tmp/cookies.txt -X POST https://172.25.101.187:8080/api/wallet/verify-key -H 'Content-Type: application/json' -d '{"pubkey":"..."}'
curl -s https://172.25.101.187:8080/static/coat_of_arms.gif | wc -c
curl -s https://172.25.101.187:8080/static/flag.png | wc -c
curl --socks5-hostname 127.0.0.1:9050 http://<onion>.onion/api/version
```

## Invite System: This tool was invoked after update with this session's learnings:
- **GodMode invites** are now cryptographically secure 32-char hex tokens generated via `secrets.token_hex(16)` (128-bit entropy), not human-readable strings
- **Real GodMode tokens**: `90dbad2056aeee01978ed62a553d7485`, `f4d96322178b6e6367be64ca2ef7cc6d` — admin, unlimited, no expiry
- **Token storage**: `invites.json` with RFC3339 timestamps, `max_uses: 0` = unlimited
- **Registration UI**: Plain text input for invite token (no dropdown with fake labels)
- **Invite Creation API**: `POST /api/auth/create-invite` (auth required) — returns new cryptographic token

## Sidechain Wallet API (for TLR/ARGENTUM/NT)
- `GET /api/wallet/keys` — exports `{mnemonic, pubkey, privkey, username, note}` for sidechain apps
- `POST /api/wallet/verify-key` — validates API key for sidechain access (`{ "ok": true, "pubkey": "...", "user": "..." }`)
- `POST /api/auth/create-invite` — authenticated users create new tokens with custom expiry/uses/role
- Keys derived from user's BIP39 mnemonic (Ed25519 via `bip39.KeypairFromMnemonic`)

## Login/Register/Restore UI (Production-Ready)
All forms in `C:\ParanoidX-data\` are **functional products** — not simulations:

### `/login.html`
- Eye toggle (👁️/🙈) on password field via `.pw-wrap` + delegated click handler
- Toggle at **far right** of input (`position:absolute; right:10px`), `tabindex="-1"` prevents focus stealing
- Tab navigation only between username/password fields
- Submit button disables during request, shows "Signing in..."
- Enter key support on both fields
- Links to Register + Restore from seed
- POST `/login` → sets `dashboard_token` cookie → redirects to `/`

### `/register.html`
- Two working tabs: "Register with Invite" + "Restore from Seed" — keyboard accessible (ArrowLeft/Right, Enter, Space), ARIA roles
- Eye toggles on **all 4** password fields (far right, `tabindex="-1"`)
- **No form clearing on error** — user input preserved, only error message shown
- Password mismatch → inline error, form stays filled
- Submit buttons disable during request: "Creating..." / "Restoring..."
- Real API calls to `/api/auth/register-with-invite` and `/api/auth/restore`
- Success: shows generated mnemonic with numbered words + warning banner, redirects to dashboard
- Restore tab: complete form with username, mnemonic (required), new password, confirm

## Autonomous Evolution Cron
- **Cron job**: `paranoidx-evolution-cycle` (every 2h via `cronjob` tool)
- **Script**: `C:\ParanoidX\scripts\evolution_cycle.py` — runs cycle N, increments version badge, reports to Telegram
- **Cycle actions**: Backup to `D:\backups` → Build Go binary → Restart server → Run tests → Increment version badge → Report to Telegram
- **Version badge**: Visible in `dashboard.html` header (`<span class="version-badge" id="dashVersion">A{NN}</span>`)
- **Dashboard version**: **A18** (auto-incremented by evolution cron, currently running 20-cycle evolution)

## Evolution Cycle Script Fixes (This Session)
The `evolution_cycle.py` script was fixed to run reliably on Windows Python (not WSL Python):

1. **Windows paths** — All config constants use raw Windows paths (`r"C:\ParanoidX"`, `r"D:\backups"`), not WSL paths. The script runs on Windows Python (`C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`).

2. **Backup directory creation** — Added `os.makedirs(BACKUP_DIR, exist_ok=True)` before creating tarballs to handle missing `D:\backups` directory.

3. **Build command** — Uses `wsl -- bash -c "cd /mnt/c/ParanoidX && go build ..."` to build inside WSL.

4. **Server restart pattern** — Critical fix: keep WSL shell alive long enough for server to daemonize:
   ```python
   cmd = f'wsl -- bash -c "nohup {WSL_BINARY} -data {WSL_DATA} -listen 0.0.0.0:8080 > /tmp/paranoidx.log 2>&1 & sleep 5"'
   ok, out, err = run_cmd(cmd, timeout=15)
   time.sleep(3)
   ```
   The `& sleep 5` inside the bash command ensures the shell doesn't exit before the Go server fully detaches.

5. **Test endpoint URL** — Changed from `https://127.0.0.1:8080` to `https://172.25.101.187:8080` (WSL2 eth0 IP accessible from Windows host). Windows cannot reach WSL2 `127.0.0.1` directly.

6. **Debug cycle WSL commands** — All `ss`, `tail`, `pkill` commands wrapped in `wsl -- bash -c "..."`.

7. **Error handling** — `err` can be `None`; use `err_msg = err[:200] if err else "Unknown error"` before slicing.

8. **Version badge extraction** — Supports both patterns: `id="dashVersion"` and `class="version-badge"`.

## HTTPS Verified on All WSL2 Interfaces
| Interface | URL | Verified |
|-----------|-----|----------|
| WSL2 lo | `https://127.0.0.1:8080` | ✅ |
| WSL2 eth0 | `https://172.25.101.187:8080` | ✅ (Windows browser access) |
| WSL2 lo alias | `https://10.255.255.254:8080` | ✅ |

## Verification Protocol (Updated)
```bash
# HTTPS (self-signed TLS, WSL2 IP)
curl -k -c /tmp/cookies.txt -X POST https://172.25.101.187:8080/login -d 'username=...&password=...'
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/auth/me
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/vpn/configs
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/treasury/state
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/wallet/exchange/quote?from=TL&to=NT
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/radio
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/marketplace
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/bridge/status
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/citizens
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/vault/list
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/status
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/subscription?pubkey=...
curl -k -b /tmp/cookies.txt https://172.25.101.187:8080/api/wallet/keys       # Sidechain keys
curl -k -b /tmp/cookies.txt -X POST https://172.25.101.187:8080/api/wallet/verify-key -H 'Content-Type: application/json' -d '{"pubkey":"..."}'
curl -s https://172.25.101.187:8080/static/coat_of_arms.gif | wc -c
curl -s https://172.25.101.187:8080/static/flag.png | wc -c
curl --socks5-hostname 127.0.0.1:9050 http://<onion>.onion/api/version
```

## Critical Fixes & Patterns (This Session)
1. **Path mismatch** — Server `-data` flag accepts both Windows (`C:\ParanoidX-data`) and WSL (`/mnt/c/ParanoidX-data`). Invite/user file lookup must try both native and WSL-converted paths.
2. **Port conflicts** — Multiple ParanoidX instances on 8080. Kill existing: `pkill -f "ParanoidX.*8080"` (WSL) + `taskkill /F /IM ParanoidX.exe` (Windows)
3. **Cookie not sent** — Frontend **must** use `credentials: 'include'` on all fetch calls
4. **Mnemonic validation** — Uses BIP39 checksum; test mnemonic "abandon x11 + about" fails. Generate real mnemonics via `bip39.GenerateMnemonic()`
5. **Invite consumption** — `max_uses: 0` = unlimited (no consumption), `max_uses > 0` = limited, tracked via `uses` counter
6. **Eye toggle position** — **Far right** of input (`right:10px`), `tabindex="-1"` prevents focus stealing, delegated event handler
7. **Tab switching** — No focus stealing, keyboard accessible, ARIA roles
8. **No form clearing on error** — Preserve user input, only show error message
9. **Version badge** — Incremented by evolution cron (`scripts/evolution_cycle.py`), visible in dashboard header
10. **No simulations** — Forms make real API calls, handle loading states, display errors, redirect on success

## Auth Gate
- JS `initAuth()` calls `/api/auth/me` on load
- 401 → redirect to `/login`
- POST `/login` → `dashboard_token` cookie
- All fetch use `credentials: 'include'`
- Change password overlay if `force_password_change: true`
- Invite register: `POST /api/auth/register {username, password}`

## Tor HS Config (torrc)
```torrc
SocksPort 9050
HiddenServiceSingleHopMode 1
HiddenServiceNonAnonymousMode 1
HiddenServiceDir /var/lib/tor/dashboard
HiddenServicePort 80 172.25.101.187:8080  # WSL host IP
```
Restart: `docker-compose -f C:\ParanoidX\docker\docker-compose.yml restart tor`

## Key Files
- `C:\ParanoidX-data\dashboard.html` — version badge at line ~164
- `C:\ParanoidX\cmd\ParanoidX\main.go` — routes, auth middleware
- `C:\ParanoidX\internal\auth\auth.go` — AuthManager
- `C:\ParanoidX\internal\api\handlers.go` — Login/Logout/Me/ChangePwd/Register
- `C:\ParanoidX\internal\treasury\ledger.go` — SQLite TL Ledger
- `C:\ParanoidX\internal\vpn\vpn.go` — VPN Manager + SubscriptionManager
- `C:\ParanoidX\docker\tor\torrc` — Tor HS config
- `C:\ParanoidX\docker\docker-compose.yml` — Docker services

## Pitfalls
- Multiple dashboard copies → keep only `C:\ParanoidX-data\dashboard.html`
- Wrong Tor IP → use WSL host IP (`172.25.x.x`), not Docker gateway (`172.18.0.1`)
- SocksPort conflict → `SocksPort 0` for HS-only mode
- Auth cookie → JS fetch must use `credentials: 'include'`
- Version badge → edit `<span class="version-badge" id="dashVersion">A{NN}</span>`