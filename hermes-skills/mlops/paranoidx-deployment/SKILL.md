---
name: paranoidx-deployment
category: mlops
description: "Deploy ParanoidX on WSL2 with BIP39 auth and auto-TLS."
---

# ParanoidX Deployment Skill

Deploy and operate the ParanoidX sovereign network daemon (Go service) with BIP39-based authentication, automatic TLS, and versioned dashboard on Windows 11 WSL2.

## Triggers
- User wants to deploy/run ParanoidX on Windows WSL2
- Need BIP39 username/password auth with seed phrase recovery
- Need auto-TLS with self-signed certs for local/WSL2 interfaces
- Need dashboard with version badges (A00, A01...) and 16 tabs showing real API data

## Prerequisites
- Windows 11 with WSL2 Ubuntu 24.04+
- Go 1.22+ installed in WSL2
- Data directory at `/mnt/c/ParanoidX-data` (or custom `-data` flag)
- Binary built at `/home/tomas/bin/ParanoidX` (WSL2 path)

## Architecture

```
+-----------------------------------------------------+
|  ParanoidX Server (WSL2)                           |
|  /home/tomas/bin/ParanoidX                         |
|  -data /mnt/c/ParanoidX-data                       |
|  -listen 0.0.0.0:8080                              |
+-----------------------------------------------------+
         |           |           |
         v           v           v
    127.0.0.1   172.25.101.187  10.255.255.254
    (WSL2 lo)   (WSL2 eth0)     (WSL2 lo alias)
         |           |           |
         +-----------+-----------+
                     |
                     v
             HTTPS (TLS 1.2+)
             Self-signed cert
             SAN: localhost, 127.0.0.1,
                  172.25.101.187, 10.255.255.254
```

## Deployment Steps

### 1. Build Binary
```bash
cd /mnt/c/ParanoidX
go build -o ParanoidX ./cmd/ParanoidX
cp ParanoidX /home/tomas/bin/ParanoidX
```

### 2. Generate TLS Certificates (auto-detected)
```bash
mkdir -p /mnt/c/ParanoidX-data/certs
cd /mnt/c/ParanoidX-data/certs
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:172.25.101.187,IP:10.255.255.254"
```

### 3. Import Cert to Windows Trusted Root CA
```cmd
REM Run as Administrator in cmd.exe:
certutil -addstore -f ROOT C:\cert.pem
REM (Copy cert.pem to C:\cert.pem first)
```

### 4. Run Server
```bash
/home/tomas/bin/ParanoidX -data /mnt/c/ParanoidX-data -listen 0.0.0.0:8080
```

### 5. Access from Windows Browser
```
https://172.25.101.187:8080
```
(Use actual WSL2 eth0 IP from `wsl -- ip addr show eth0 | grep inet`)

## Auth System (BIP39)

### Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/auth/register-with-invite | POST | Register with invite, returns 24-word mnemonic + Ed25519 pubkey |
| /login | POST (form) | Username/password login, returns HttpOnly cookie token |
| /api/auth/me | GET | Verify auth, returns username/role |
| /api/auth/restore | POST | Recover account from seed phrase + new password |

### Invite System (REAL Cryptographic Tokens)
- Tokens generated via `secrets.token_hex(16)` = 32-char hex (128-bit entropy)
- NO fake strings like "GodModeToken" or "UNIVERSAL-UNLIMITED" — those were hallucinations, removed
- Stored in /mnt/c/ParanoidX-data/invites.json with RFC3339 timestamps
- Fields: token, created_by, created_at, expires_at, max_uses, uses, role, note
- max_uses=0 = unlimited, expires_at=zero = no expiry
- Registration UI = plain text input field (NO dropdowns)
- Invite creation API: POST /api/auth/create-invite (requires auth) with {expires_in_hours, max_uses, role, note}

### Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/auth/register-with-invite | POST | Register with real token, returns 24-word mnemonic + Ed25519 pubkey |
| /api/auth/create-invite | POST (auth) | Create new invite with custom properties |
| /login | POST (form) | Username/password login, returns HttpOnly cookie token |
| /api/auth/me | GET | Verify auth, returns username/role |
| /api/auth/restore | POST | Recover account from seed phrase + new password |
| /api/wallet/keys | GET (auth) | Export {mnemonic, pubkey, privkey} for sidechain apps |
| /api/wallet/verify-key | POST (auth) | Verify pubkey for TLR/ARGENTUM/NT API access |

### Registration Flow
1. User enters username (3-32 chars, alphanumeric/underscore/dash), password (min 8), invite token
2. Optional: provide existing 12/24-word BIP39 mnemonic to link existing wallet
3. Server generates new 24-word BIP39 mnemonic if not provided
4. Returns mnemonic (save securely!) + Ed25519 pubkey + JWT token

### Recovery Flow
1. User enters username + 12/24-word mnemonic + new password (twice)
2. Server validates mnemonic derives same pubkey
3. Password hash updated, old password invalidated
4. Returns new token

## Dashboard Versioning
- Version badge in header/sidebar: A00, A01, A02...
- Increment on every dashboard code change
- Located in C:\ParanoidX-data\dashboard.html and login.html
- Search for version-badge dashVersion A06

## Key Files
| File | Purpose |
|------|---------|
| C:\ParanoidX-data\dashboard.html | Main dashboard (16 tabs) |
| C:\ParanoidX-data\login.html | Login page (username, not email) |
| C:\ParanoidX-data\register.html | Register/Restore page |
| C:\ParanoidX-data\certs\cert.pem | TLS cert (auto-detected) |
| C:\ParanoidX-data\certs\key.pem | TLS key (auto-detected) |
| C:\ParanoidX-data\invites.json | Invite tokens |
| C:\ParanoidX-data\users.json | User accounts (BIP39 mnemonics) |

## API Endpoints (All Require Auth Cookie)
| Tab | Endpoint | Description |
|-----|----------|-------------|
| Wallet | /api/wallet/state | 8 denominations, 8 NFTs, 16GB vault |
| VPN | /api/vpn/configs | 10 protocols (vmess, vless, trojan, etc.) |
| Treasury | /api/treasury/state | Silver reserve, NFT banknotes |
| Exchanger | /api/wallet/exchange/quote | TL<->NT rates, 2.28% fee |
| Radio | /api/radio | 5 stations (EN/RU/ES) |
| Marketplace | /api/marketplace | Listings |
| Bridge | /api/bridge/status | SimpleX relay |
| Citizens | /api/citizens | Heraldry/coat of arms |
| Vault | /api/vault/list | Encrypted file storage |
| Status | /api/status | System health, memory, disk |
| Subscription | /api/subscription?pubkey= | Tier colonist benefits |

## Common Issues & Fixes

### Address already in use on port 8080
```bash
# Kill systemd service if exists
sudo systemctl stop paranoidx.service 2>/dev/null
sudo systemctl disable paranoidx.service 2>/dev/null
# Kill all ParanoidX processes
pkill -9 -f ParanoidX
# Remove systemd unit
sudo rm /etc/systemd/system/paranoidx.service
sudo systemctl daemon-reload
```

### TLS wrong version number / cert not loading
- Verify certs exist: ls -la /mnt/c/ParanoidX-data/certs/
- Check logs for TLS enabled message
- Rebuild binary after cert changes

### Windows browser Not Secure
- Import cert.pem to Trusted Root CA (run as Admin):
  certutil -addstore -f ROOT C:\cert.pem
- Restart browser completely (Ctrl+Shift+W)

### WSL2 IP changes after reboot
```bash
# Get current IP
wsl -- ip addr show eth0 | grep "inet "
# Update cert SAN if needed, or use new IP directly
```

### Cookie Authentication Not Working (Session 2026-08-07)
**Problem**: Login was failing because `/login` expects `application/x-www-form-urlencoded` form data, not JSON
**Fix**: 
- Go handlers use `r.FormValue()` for form-encoded data
- Cookie set with `Secure: true` for HTTPS
- Cookie config: `SameSite=Lax`, `HttpOnly=true`, `Secure=true`, `Path=/`, `MaxAge=86400`
- Dashboard checks cookie via `r.Cookie("dashboard_token")` → validates via `AuthMiddleware`

### PowerShell Backup Verification in WSL
**Problem**: PowerShell `-Command` with inline scripts fails due to variable expansion and quoting issues when called from WSL
**Working pattern**:
```python
# Write verification script to /tmp/verify.ps1
with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8', dir='/tmp') as f:
    f.write(ps_verify_script)
    ps_verify_path = f.name

# Convert /tmp/... to \\wsl$\Ubuntu-24.04\tmp\... for Windows PowerShell
ps_verify_win = ps_verify_path.replace('/tmp/', '\\\\wsl$\\Ubuntu-24.04\\tmp\\').replace('/', '\\\\')
ok, out, err = run_cmd(f'powershell.exe -NoProfile -NoLogo -ExecutionPolicy Bypass -File "{ps_verify_win}"', timeout=60)

# Filter out PowerShell banner lines
out_lines = [line for line in out.strip().split('\n') if line.strip() and not line.strip().startswith('Windows PowerShell') and not line.strip().startswith('Copyright')]
out = '\n'.join(out_lines)
```

### Evolution Cycle Backup Strategy
**Problem**: PowerShell `Compress-Archive` was unreliable for large (48GB) backups
**Solution**: Use Python `tarfile` with `w:gz` compression — deterministic, SHA256 verified, ~111MB compressed
```python
exclude_patterns = [
    "vault/", "backups/", "island-bot/",
    "*.db-journal", "*.db-shm", "*.db-wal",
    "*.tmp", "*.swp", "*.log", "__pycache__", "*.pyc", "*.db.bak",
]
def filter_func(tarinfo):
    name = tarinfo.name
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(os.path.basename(name), pattern) or fnmatch.fnmatch(name, f"*/{pattern}"):
            return None
    return tarinfo

with tarfile.open(backup_path, "w:gz") as tar:
    tar.add(PARANOIDX_SRC, arcname=os.path.join(backup_name, "ParanoidX"), filter=filter_func)
    tar.add(PARANOIDX_DATA, arcname=os.path.join(backup_name, "ParanoidX-data"), filter=filter_func)
```

### Systemd Service Configuration for Node Monitor
- **Unit file**: `/etc/systemd/system/paranoidx-node-monitor.service` with `Type=notify`, `Restart=always`, `RestartSec=10`
- **Security**: `NoNewPrivileges=yes`, `PrivateTmp=yes`, `ProtectSystem=strict`, `ReadWritePaths` for ParanoidX dirs
- **Enabled**: `systemctl enable paranoidx-node-monitor.service` + `daemon-reload`

### Verification Script (7/7 tests passing)
Created ad-hoc verification testing:
- Version badge (A81)
- Login flow (form-encoded POST)
- `/api/auth/me` — returns user info
- `/api/onboarding/status` — wallet, citizen, silver balance
- `/api/superguard/alarm` — alarm state with zone/target/auto-resolve
- `/api/treasury/state` — reserve, banknotes, RWA
- Dashboard access with cookie auth

### Files Modified This Session
- `/c/ParanoidX/internal/api/handlers.go` — cookie Secure flag, login/register/restore handlers
- `/c/ParanoidX/internal/api/onboarding_status.go` — new onboarding status endpoint
- `/c/ParanoidX/cmd/ParanoidX/main.go` — register `/api/onboarding/status` route
- `/c/ParanoidX/scripts/evolution_cycle.py` — Python tarfile backup, fixed PowerShell verification
- `/c/ParanoidX/scripts/node_monitor.py` — systemd-ready node monitor with Telegram reporting
- `/c/ParanoidX/scripts/paranoidx-node-monitor.service` — systemd unit
- `/c/ParanoidX/internal/superguard/handlers.go` — full alarm REST API
- `/c/ParanoidX-data/dashboard.html` — version badge A81, SuperGuard tab
- `/c/ParanoidX-data/login.html` — form-encoded login, cookie handling
- `/c/ParanoidX-data/register.html` — invite registration, mnemonic display

## Verification Checklist
Run after deployment:
```bash
python3 -c "
import json, subprocess
def c(url, ck=None, m=GET, d=None, f=None):
    cmd=[curl,-k,-s]
    if ck: cmd+=[-H,Cookie: dashboard_token={ck}]
    cmd+=[-X,m,url]
    if f: cmd+=[--data,&.join([f{k}={v} for k,v in f.items()]),-H,Content-Type: application/x-www-form-urlencoded]
    elif d: cmd+=[-H,Content-Type: application/json,-d,json.dumps(d)]
    return subprocess.run(cmd,capture_output=True,text=True,timeout=10).stdout

b=https://127.0.0.1:8080
r=json.loads(c(f{b}/api/auth/register-with-invite,m=POST,d={username:v,password:TestPass123!,invite:UNIVERSAL-UNLIMITED}))
t=json.loads(c(f{b}/login,m=POST,f={username:v,password:TestPass123!})).get(token)
print(Auth:,json.loads(c(f{b}/api/auth/me,cookie=t)).get(username))
print(Dash A06:, A06 in c(f{b}/,cookie=t))
w=json.loads(c(f{b}/api/wallet/state,cookie=t))
print(Wallet:, len(w.get(denominations,[]))==8, len(w.get(nfts,[]))==8)
print(ALL OK if all([len(w.get(denominations,[]))==8, len(w.get(nfts,[]))==8]) else FAIL)
"
```

## References
- references/bip39-auth.md - BIP39 mnemonic generation/validation details
- references/tls-auto-detect.md - Auto-TLS implementation in main.go
- references/wsli2-networking.md - WSL2 networking quirks (127.0.0.1 vs eth0 IP)
- references/dashboard-versioning.md - Version badge increment procedure
- references/real-token-system.md - Real cryptographic token system (NO fake strings)
- references/evolution-backup.md - 20-cycle autonomous evolution with D:\backups

## Templates
- templates/register.html - Register/Restore page with tabs (plain text invite input)
- templates/login.html - Login page with version badge
- templates/dashboard.html - 16-tab dashboard skeleton

## Scripts
- scripts/gen-certs.sh - Generate self-signed cert with SAN
- scripts/import-cert.ps1 - PowerShell script to import cert to Windows Root CA
- scripts/verify-deploy.py - Full deployment verification (29 checks)
- scripts/evolution_cycle.py - Autonomous evolution cycle (20 cycles, D:\backups)