# BIP39 Authentication Flow for ParanoidX

## Overview
ParanoidX uses BIP39 mnemonic phrases for account registration and recovery, eliminating email/password dependencies entirely. No external email services needed.

## Flow

### 1. Registration with Invite
```
POST /api/auth/register-with-invite
{
  "username": "user123",
  "password": "securepass",
  "invite": "UNIVERSAL-UNLIMITED",
  "mnemonic": "optional existing 12/24-word seed phrase"  // Optional
}
```

**Response:**
```json
{
  "status": "created",
  "username": "user123",
  "mnemonic": "word1 word2 ... word24",  // 24-word BIP39 phrase
  "pubkey": "ed25519_public_key_hex",
  "token": "session_token"
}
```

### 2. Login (Username + Password)
```
POST /login
Content-Type: application/x-www-form-urlencoded

username=user123&password=securepass
```

**Response:**
```json
{
  "status": "ok",
  "token": "session_token"
}
```

### 3. Authenticated Endpoints
All dashboard APIs require `Cookie: dashboard_token=<token>` header.

### 4. Account Recovery (Restore from Seed)
```
POST /api/auth/restore
{
  "username": "user123",
  "mnemonic": "word1 word2 ... word24",
  "password": "new_secure_password"
}
```

**Response:**
```json
{
  "status": "restored",
  "token": "new_session_token"
}
```

**Key property:** Old password is **permanently invalidated** after restore.

### 5. Verify Old Password Rejected
```
POST /login
username=user123&password=old_password
```
**Response:** `"invalid credentials"`

## Universal Invite Token
- Token: `UNIVERSAL-UNLIMITED`
- Created by system at startup
- MaxUses: 0 (unlimited)
- No expiration
- Pre-filled in register.html

## BIP39 Implementation Details

### Mnemonic Generation
- 256-bit entropy → 24 words (English wordlist)
- Uses `golang.org/x/crypto/bip39` compatible implementation
- Ed25519 keypair derived via PBKDF2(mnemonic + "mnemonic", 2048 rounds)

### Seed Phrase Validation
- Must be 12 or 24 words
- All words must exist in BIP39 English wordlist
- Checksum must validate

## UI Pages

### `/login.html`
- Username field (type=text, not email)
- Password field
- Link to `/register.html`
- Version badge (A06)

### `/register.html`
- Invite token (pre-filled: UNIVERSAL-UNLIMITED)
- Username field (pattern: `[a-zA-Z0-9_-]{3,32}`)
- Password + confirm password
- Optional mnemonic textarea (for existing seed linking)
- Tabs: "Register with Invite" | "Restore from Seed"

## Security Properties
1. **No email ever stored** - Username only
2. **Seed phrase = master key** - Can recover account without password
3. **Password change via restore** - Old password permanently invalidated
4. **HttpOnly cookie session** - `dashboard_token` cookie
5. **Ed25519 identity** - Pubkey derived from seed, used for subscriptions

## Testing Commands
```bash
# Register
curl -X POST http://127.0.0.1:8080/api/auth/register-with-invite \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"TestPass123!","invite":"UNIVERSAL-UNLIMITED"}'

# Login
curl -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=TestPass123!"

# Restore
curl -X POST http://127.0.0.1:8080/api/auth/restore \
  -H "Content-Type: application/json" \
  -d '{"username":"test","mnemonic":"<24-words>","password":"NewPass456!"}'

# Verify old password rejected
curl -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=TestPass123!"
```