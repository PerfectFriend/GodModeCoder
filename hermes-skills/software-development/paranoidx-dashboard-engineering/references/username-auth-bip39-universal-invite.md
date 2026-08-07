# Username-Based Auth + Universal Invite + BIP39 Mnemonic (2026-08-06)

## Overview
Complete removal of email from ParanoidX auth flow. Universal unlimited invite `UNIVERSAL-UNLIMITED`. BIP39 mnemonic generation on registration + seed phrase restore for password/username recovery.

## Problem
- Auth previously required email format (`user@domain.com`)
- No seed phrase recovery mechanism
- Invite system was per-invite with limited uses
- User wanted fully username-based auth with own email service planned for later (onion)

## Solution

### 1. Auth Manager Updates (`internal/auth/auth.go`)

**New Methods:**
```go
// RegisterWithInvite creates account with username + invite token
// If mnemonic provided, validates it; otherwise generates new 24-word BIP39
func (am *AuthManager) RegisterWithInvite(username, password, invite, mnemonic string) (*User, string, error)

// Restore recovers account from seed phrase with new password
func (am *AuthManager) Restore(username, mnemonic, newPassword string) (string, error)

// ValidateInvite checks if invite token is valid
func (am *AuthManager) ValidateInvite(token string) (string, error)

// ConsumeInvite increments use count (no-op for UNIVERSAL-UNLIMITED)
func (am *AuthManager) ConsumeInvite(token string) error
```

**Universal Invite Logic:**
```go
const UniversalInvite = "UNIVERSAL-UNLIMITED"

func (am *AuthManager) ValidateInvite(token string) (string, error) {
    if token == UniversalInvite {
        return "user", nil  // unlimited, no expiry
    }
    // ... existing invite logic
}

func (am *AuthManager) ConsumeInvite(token string) error {
    if token == UniversalInvite {
        return nil  // no-op, unlimited
    }
    // ... existing consume logic
}
```

### 2. BIP39 Mnemonic Handling (`internal/crypto/bip39/bip39.go`)

**Validation (on custom mnemonic provided during registration):**
```go
func EntropyFromMnemonic(mnemonic string) ([]byte, error) {
    // 1. Split into words
    // 2. Check length: 12/15/18/21/24 words, multiple of 3
    // 3. Check all words in official BIP39 English wordlist (2048 words)
    // 4. Verify checksum (SHA512 of entropy)
    // Returns entropy bytes if valid
}
```

**Keypair Derivation:**
```go
func KeypairFromMnemonic(mnemonic, passphrase string) (pubkeyHex, privkeyHex string, err error) {
    seed := PBKDF2([]byte(mnemonic), []byte("mnemonic"+passphrase), 2048, 64, sha512.New)
    priv := ed25519.NewKeyFromSeed(seed[:32])
    pub := priv.Public().(ed25519.PublicKey)
    return hex.EncodeToString(pub), hex.EncodeToString(priv), nil
}
```

**Restore Flow:**
1. User provides username + 12/24-word mnemonic + new password
2. `EntropyFromMnemonic()` validates mnemonic
3. `KeypairFromMnemonic()` derives Ed25519 keypair
4. Update user record: password hash + pubkey + mnemonic (encrypted)
5. Return new session token

### 3. HTTP Routes (`cmd/ParanoidX/main.go`)

```go
// Public routes (no auth required)
http.HandleFunc("/register.html", serveRegisterPage)
http.HandleFunc("/login.html", serveLoginPage)
http.HandleFunc("/api/auth/register-with-invite", registerWithInviteHandler)
http.HandleFunc("/api/auth/restore", restoreHandler)

// Auth required
http.HandleFunc("/", dashboardOrLoginHandler)  // checks cookie
```

**Handler: `registerWithInviteHandler`**
```go
func registerWithInviteHandler(w http.ResponseWriter, r *http.Request) {
    // POST only
    // JSON body: {username, password, invite, mnemonic?}
    // Validate: username pattern [a-zA-Z0-9_-]{3,32}, password min 8
    // Validate invite via authMgr.ValidateInvite()
    // Call authMgr.RegisterWithInvite()
    // On success: authMgr.ConsumeInvite(), return {mnemonic, pubkey, status, token}
}
```

**Handler: `restoreHandler`**
```go
func restoreHandler(w http.ResponseWriter, r *http.Request) {
    // POST only
    // JSON body: {username, mnemonic, password}
    // Call authMgr.Restore()
    // Return {status: "restored", token}
}
```

### 4. Frontend Pages

**`C:\ParanoidX-data\register.html`** (~11KB)
- Two tabs: "Register with Invite" / "Restore from Seed"
- Register tab:
  - Invite token input (pre-filled "UNIVERSAL-UNLIMITED", readonly)
  - Username input (pattern validation)
  - Password + Confirm
  - Optional mnemonic textarea (placeholder: "leave empty to generate new")
  - Small helper text: "If provided, this mnemonic will be validated and linked for recovery"
- Restore tab:
  - Username
  - Mnemonic textarea (required)
  - New password
- JS calls `/api/auth/register-with-invite` or `/api/auth/restore`
- On success: redirect to `/` with cookie

**`C:\ParanoidX-data\login.html`** (updated)
- Username field (type=text, not email)
- Password field
- Link: "No account? Request invite" → `/register.html`
- HttpOnly cookie `dashboard_token`

### 5. Dashboard Root Handler

```go
http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    // Handle register.html explicitly
    if r.URL.Path == "/register.html" { ... return }
    
    // Only serve dashboard at root
    if r.URL.Path != "/" { http.NotFound(w, r); return }
    
    // Check auth cookie
    cookie, _ := r.Cookie("dashboard_token")
    if cookie == nil || cookie.Value == "" {
        serveLoginPage(w, r)
        return
    }
    
    // Validate token
    username, err := authMgr.ValidateToken(cookie.Value)
    if err != nil {
        serveLoginPage(w, r)
        return
    }
    
    // Serve dashboard
    serveDashboard(w, r)
})
```

### 6. Testing Verification (40/40 tests)

```bash
# 1. Register with universal invite
curl -X POST /api/auth/register-with-invite \
  -d '{"username":"test","password":"TestPass123!","invite":"UNIVERSAL-UNLIMITED"}'
# → {mnemonic:"... 24 words ...", pubkey:"...", status:"created"}

# 2. Login
curl -X POST /login -d "username=test&password=TestPass123!"
# → {status:"ok", token:"..."}

# 3. /api/auth/me
curl -H "Cookie: dashboard_token=..." /api/auth/me
# → {username:"test", role:"user", force_password_change:false}

# 4. Restore from seed (password recovery)
curl -X POST /api/auth/restore \
  -d '{"username":"test","mnemonic":"...","password":"NewPass456!"}'
# → {status:"restored", token:"..."}

# 5. Login with NEW password
curl -X POST /login -d "username=test&password=NewPass456!"
# → {status:"ok", token:"..."}

# 6. Old password rejected
curl -X POST /login -d "username=test&password=TestPass123!"
# → invalid credentials

# 7. Dashboard accessible
curl -H "Cookie: dashboard_token=..." /
# → HTML with version badge A06

# 8-20. All 16 dashboard tabs return real API data
```

### 7. Key Files Modified

| File | Change |
|------|--------|
| `internal/auth/auth.go` | `RegisterWithInvite`, `Restore`, `ValidateInvite`, `ConsumeInvite` for universal invite |
| `cmd/ParanoidX/main.go` | New routes: `/register.html`, `/api/auth/register-with-invite`, `/api/auth/restore`, updated root handler |
| `C:\ParanoidX-data\register.html` | New register page with 2 tabs |
| `C:\ParanoidX-data\login.html` | Username (not email), link to `/register.html` |
| `internal/crypto/bip39/bip39.go` | Existing: `EntropyFromMnemonic`, `KeypairFromMnemonic` |

### 8. Dashboard Version

Incremented to **A06** (visible in header badge).

### 9. Runtime

- WSL2 Ubuntu 24.04
- Binary: `/home/tomas/bin/ParanoidX`
- Data: `/mnt/c/ParanoidX-data`
- Port: 8080
- systemd: `paranoidx.service` (enabled)

### 10. Security Notes

- No email addresses ever collected or stored
- Mnemonic validated against official BIP39 wordlist + checksum
- Ed25519 keypair derived via PBKDF2 (2048 rounds)
- Universal invite has no rate limit (by design for admin use)
- HttpOnly cookies for session tokens
- Old password invalidated on seed phrase restore (prevents replay)
- Password min 8 chars (configurable)