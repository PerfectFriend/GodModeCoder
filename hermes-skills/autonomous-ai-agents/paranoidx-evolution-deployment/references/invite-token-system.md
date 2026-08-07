# Invite Token System — Reference Implementation

## Token Generation (Python/Go)

### Python (for scripts)
```python
import secrets
import json
from datetime import datetime, timezone

def generate_invite_token():
    """Generate cryptographically secure invite token."""
    return secrets.token_hex(16)  # 32 hex chars = 128 bits entropy

def create_invite(token, created_by, expires_in_hours=0, max_uses=0, role="user", note=""):
    """Create invite entry for invites.json."""
    expires_at = "0001-01-01T00:00:00Z"  # zero time = no expiration
    if expires_in_hours > 0:
        expires_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    
    return {
        "token": token,
        "created_by": created_by,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        "expires_at": expires_at,
        "max_uses": max_uses,
        "uses": 0,
        "role": role,
        "note": note
    }

# Usage
token = generate_invite_token()
invite = create_invite(token, "system", expires_in_hours=0, max_uses=0, role="admin", note="GodMode unlimited")
# Add to invites.json[token] = invite
```

### Go (in auth.go)
```go
import (
    "crypto/rand"
    "encoding/hex"
    "time"
)

func GenerateToken() (string, error) {
    b := make([]byte, 16)
    if _, err := rand.Read(b); err != nil {
        return "", err
    }
    return hex.EncodeToString(b), nil
}
```

## Token Format Requirements

| Field | Type | Format | Notes |
|-------|------|--------|-------|
| token | string | 32 hex chars | `secrets.token_hex(16)` |
| created_by | string | username | "system" for pre-seeded |
| created_at | string | RFC3339 UTC | `2026-08-06T18:43:36Z` (NO microseconds!) |
| expires_at | string | RFC3339 UTC | `0001-01-01T00:00:00Z` = no expiry |
| max_uses | int | 0 = unlimited | >0 = limited uses |
| uses | int | auto-incremented | |
| role | string | "user" \| "admin" | |
| note | string | free text | |

## Critical: RFC3339 Timestamp Format

**CORRECT**: `2026-08-06T18:43:36Z`
**WRONG**: `2026-08-06T18:43:36.748409` (Go's `time.Time.String()` includes microseconds which fails JSON unmarshal)

```go
// Correct Go formatting
createdAt := time.Now().UTC().Format(time.RFC3339)
// or
createdAt := time.Now().UTC().Truncate(time.Second).Format(time.RFC3339)
```

```python
# Correct Python formatting
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
```

## Validation Logic (Go)

```go
func (am *AuthManager) ValidateInvite(token string) (string, error) {
    // 1. Load invites.json from both Windows and WSL paths
    // 2. Find token in map
    // 3. Check expiration (zero time = no expiry)
    // 4. Check uses (max_uses=0 = unlimited)
    // 5. Return role
}

func (am *AuthManager) ConsumeInvite(token string) error {
    // Increment uses counter
    // Persist to both paths
}
```

## Pre-seeded Tokens (in invites.json)

```json
{
  "90dbad2056aeee01978ed62a553d7485": {
    "token": "90dbad2056aeee01978ed62a553d7485",
    "created_by": "system",
    "created_at": "2026-08-06T18:43:36Z",
    "expires_at": "0001-01-01T00:00:00Z",
    "max_uses": 0,
    "uses": 0,
    "role": "admin",
    "note": "GodMode unlimited invite - no expiration, unlimited uses, admin role"
  },
  "f4d96322178b6e6367be64ca2ef7cc6d": {
    "token": "f4d96322178b6e6367be64ca2ef7cc6d",
    "created_by": "system",
    "created_at": "2026-08-06T16:45:10Z",
    "expires_at": "0001-01-01T00:00:00Z",
    "max_uses": 0,
    "uses": 0,
    "role": "admin",
    "note": "GodMode unlimited invite - no expiration, unlimited uses, admin role"
  }
}
```

## API Endpoints

### Create Invite (auth required)
```
POST /api/auth/create-invite
Content-Type: application/json

{
  "expires_in_hours": 0,
  "max_uses": 0,
  "role": "user|admin",
  "note": "optional description"
}

Response:
{
  "ok": true,
  "token": "a1b2c3d4...",
  "expires": 0,
  "max_uses": 0,
  "role": "admin",
  "note": "optional description"
}
```

### Register with Invite
```
POST /api/auth/register-with-invite
Content-Type: application/json

{
  "username": "newuser",
  "password": "min8chars",
  "invite": "a1b2c3d4...",
  "mnemonic": "optional 12/24 word seed"
}

Response:
{
  "status": "created",
  "username": "newuser",
  "mnemonic": "generated or provided seed",
  "pubkey": "ed25519 pubkey",
  "token": "session_token"
}
```

## Pitfalls to Avoid

1. **Never use human-readable tokens** like "GodModeToken" — always `secrets.token_hex(16)`
2. **RFC3339 timestamps without microseconds** — Go's JSON parser rejects `2026-08-06T18:43:36.748409`
3. **Write to both paths** — Windows (`C:\ParanoidX-data\invites.json`) and WSL (`/mnt/c/ParanoidX-data/invites.json`)
4. **Token case-sensitivity** — tokens are case-sensitive, store and compare exactly
5. **max_uses=0 means unlimited** — don't use negative numbers or omit field