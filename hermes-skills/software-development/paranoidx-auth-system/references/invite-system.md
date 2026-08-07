# Invite System in ParanoidX

## Overview
The invite system controls user registration. Only users with a valid invite token can register (except admin-created accounts via `/api/auth/register`).

## Data Structure (`invites.json`)

```json
{
  "UNIVERSAL-UNLIMITED": {
    "token": "UNIVERSAL-UNLIMITED",
    "created_by": "system",
    "created_at": "2026-08-06T12:00:00.000000000+02:00",
    "expires_at": "0001-01-01T00:00:00Z",
    "max_uses": 0,
    "uses": 0,
    "role": "user",
    "note": "Universal unlimited invite - no expiration, unlimited uses"
  },
  "abc123...": {
    "token": "abc123...",
    "created_by": "admin@domain.com",
    "created_at": "2026-08-05T10:34:11.548636833+02:00",
    "expires_at": "0001-01-01T00:00:00Z",
    "max_uses": 1,
    "uses": 0,
    "role": "user",
    "note": "test"
  }
}
```

## InviteInfo Fields

| Field | Type | Description |
|-------|------|-------------|
| `token` | string | Unique invite token (key in JSON map) |
| `created_by` | string | Username/email of creator |
| `created_at` | time.Time | Creation timestamp (RFC3339) |
| `expires_at` | time.Time | Expiration (zero time = no expiration) |
| `max_uses` | int | Maximum uses allowed (0 = unlimited) |
| `uses` | int | Current use count |
| `role` | string | Role assigned to invited user (default: "user") |
| `note` | string | Optional description |

## Validation Logic (`ValidateInvite`)

```go
func (am *AuthManager) ValidateInvite(token string) (string, error) {
    // Load invites.json from same directory as users.json
    invitesFile := filepath.Join(filepath.Dir(am.usersFile), "invites.json")
    // ... cross-platform path normalization ...
    
    b, err := os.ReadFile(invitesFileWSL)
    var invites map[string]InviteInfo
    json.Unmarshal(b, &invites)
    
    invite, ok := invites[token]
    if !ok {
        return "", ErrInviteInvalid
    }
    
    // Check expiration (zero time = no expiration)
    if !invite.ExpiresAt.IsZero() && time.Now().After(invite.ExpiresAt) {
        return "", ErrInviteInvalid
    }
    
    // Check uses (max_uses = 0 means unlimited)
    if invite.MaxUses > 0 && invite.Uses >= invite.MaxUses {
        return "", ErrInviteExhausted
    }
    
    return invite.Role, nil
}
```

## Consumption Logic (`ConsumeInvite`)

```go
func (am *AuthManager) ConsumeInvite(token string) error {
    // ... load invites ...
    invite.Uses++
    invites[token] = invite
    // ... save back to file ...
}
```

**Note**: For unlimited invites (`max_uses: 0`), the `uses` counter increments but validation always passes since `invite.MaxUses > 0` is false.

## Universal Unlimited Invite

The token `UNIVERSAL-UNLIMITED` is pre-configured with:
- `max_uses: 0` (unlimited)
- `expires_at`: zero time (no expiration)
- `role: "user"`
- Created by "system"

This allows anyone with the token to register without individual invite management.

## API Integration

### Register with Invite
```bash
POST /api/auth/register-with-invite
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword123",
  "invite": "UNIVERSAL-UNLIMITED",
  "mnemonic": "optional existing seed phrase"
}
```

Response on success:
```json
{
  "status": "created",
  "username": "newuser",
  "mnemonic": "generated or provided 24-word phrase",
  "pubkey": "ed25519-pubkey-hex",
  "token": "session-token"
}
```

### Error Responses
- `invalid or expired invite` — Token not found, expired, or exhausted
- `username, password, and invite required` — Missing fields
- `password must be at least 8 characters` — Weak password
- `invalid mnemonic` — Provided mnemonic fails BIP39 checksum
- `user already exists` — Username taken

## Frontend Integration

The register page (`register.html`) pre-fills the invite field with `UNIVERSAL-UNLIMITED` and makes it required. Users can optionally enter an existing mnemonic to link their account to a known seed phrase.

## Security Considerations

1. **Invite tokens** — Should be cryptographically random (use `crypto/rand` for generation)
2. **Unlimited invite** — `UNIVERSAL-UNLIMITED` is public knowledge; treat as "open registration"
3. **Expiration** — Set `expires_at` for time-limited campaigns
4. **Role assignment** — Invites can grant "admin" role; validate carefully
5. **Audit trail** — `created_by` and `uses` provide registration audit trail

## Generating New Invites

```bash
# Via API (requires auth)
curl -X POST http://localhost:8080/api/admin/create-invite \
  -H "Content-Type: application/json" \
  -d '{"max_uses": 1, "role": "user", "note": "VIP access"}'
```

Or manually add to `invites.json` with a random token:
```bash
TOKEN=$(openssl rand -hex 16)
```