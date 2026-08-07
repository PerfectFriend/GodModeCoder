# Sidechain API Reference (TLR/ARGENTUM/NT)

## Overview
These endpoints provide cryptographic key material for sidechain applications (TLR, ARGENTUM, NT). All endpoints require authenticated session via HttpOnly cookie.

---

## GET /api/wallet/keys

Returns the user's BIP39 mnemonic, Ed25519 public key, and private key.

### Request
```http
GET /api/wallet/keys
Cookie: dashboard_token=<token>
```

### Response (200 OK)
```json
{
  "mnemonic": "word1 word2 ... word24",
  "pubkey": "64_hex_char_ed25519_pubkey",
  "privkey": "64_hex_char_ed25519_privkey",
  "note": "Keep these keys secure. Used for TLR/ARGENTUM/NT sidechain API access."
}
```

### Example
```bash
curl -k -b cookies.txt https://172.25.101.187:8080/api/wallet/keys
```

---

## POST /api/wallet/verify-key

Validates that a public key belongs to the authenticated user.

### Request
```http
POST /api/wallet/verify-key
Content-Type: application/json
Cookie: dashboard_token=<token>

{
  "pubkey": "64_hex_char_ed25519_pubkey"
}
```

### Response (200 OK)
```json
{
  "ok": true,
  "pubkey": "64_hex_char_ed25519_pubkey",
  "user": "username"
}
```

### Error Response (400/401)
```json
{
  "ok": false,
  "error": "Invalid pubkey"
}
```

### Example
```bash
curl -k -b cookies.txt -X POST https://172.25.101.187:8080/api/wallet/verify-key \
  -H "Content-Type: application/json" \
  -d '{"pubkey":"69165cfe7d8b54d8934d2f5e9fcdc8ca19cba32de15d0fee61d87fe279f3a773"}'
```

---

## POST /api/auth/create-invite

Allows authenticated users to create new invite tokens with custom parameters.

### Request
```http
POST /api/auth/create-invite
Content-Type: application/json
Cookie: dashboard_token=<token>

{
  "expires_in_hours": 0,
  "max_uses": 0,
  "role": "admin",
  "note": "Description of this invite"
}
```

### Parameters
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `expires_in_hours` | integer | 0 | Token expiration in hours (0 = no expiration) |
| `max_uses` | integer | 0 | Maximum uses (0 = unlimited) |
| `role` | string | "user" | Role for invited user: "user" or "admin" |
| `note` | string | "" | Description/notes for this invite |

### Response (200 OK)
```json
{
  "invite": "32_char_hex_token",
  "expires_at": "2026-08-06T18:43:36Z",
  "max_uses": 0,
  "uses": 0,
  "role": "admin",
  "note": "Description of this invite"
}
```

### Example
```bash
curl -k -b cookies.txt -X POST https://172.25.101.187:8080/api/auth/create-invite \
  -H "Content-Type: application/json" \
  -d '{"expires_in_hours":0,"max_uses":0,"role":"admin","note":"GodMode unlimited invite for sidechain apps"}'
```

---

## Invite Token Format

Tokens are **cryptographically secure random hex** generated via `secrets.token_hex(16)`:
- **Length**: 32 hex characters (16 bytes = 128 bits entropy)
- **Validation**: JSON lookup in `invites.json` with RFC3339 timestamp parsing
- **No more**: Human-readable fake strings like "UNIVERSAL-UNLIMITED" or "GodModeToken"

### Example Valid Tokens (GodMode)
```
90dbad2056aeee01978ed62a553d7485
f4d96322178b6e6367be64ca2ef7cc6d
```

---

## Integration with Sidechain Apps

### TLR (Thaler)
```python
import requests

session = requests.Session()
session.verify = False  # self-signed cert
session.cookies.set('dashboard_token', token)

# Get keys
keys = session.get('https://172.25.101.187:8080/api/wallet/keys').json()
mnemonic = keys['mnemonic']
pubkey = keys['pubkey']
privkey = keys['privkey']

# Use mnemonic to derive TLR wallet
# Use pubkey for API authentication
```

### ARGENTUM
```python
# Verify key before API calls
verify = session.post(
    'https://172.25.101.187:8080/api/wallet/verify-key',
    json={'pubkey': pubkey}
).json()

if verify['ok']:
    # Key is valid, proceed with ARGENTUM operations
    pass
```

### NT (Gas Token)
```python
# Create invite for new NT wallet user
invite = session.post(
    'https://172.25.101.187:8080/api/auth/create-invite',
    json={
        'expires_in_hours': 24,
        'max_uses': 1,
        'role': 'user',
        'note': 'NT gas wallet access'
    }
).json()

invite_token = invite['invite']
# Share invite_token with user for registration
```

---

## Verification Checklist (from verify-auth.py)

- [ ] `GET /api/wallet/keys` returns `{mnemonic, pubkey, privkey, note}`
- [ ] `POST /api/wallet/verify-key` with valid pubkey returns `{"ok":true, "pubkey":"...", "user":"..."}`
- [ ] `POST /api/wallet/verify-key` with invalid pubkey returns `{"ok":false, "error":"..."}`
- [ ] `POST /api/auth/create-invite` creates token with custom expiry/uses/role
- [ ] Generated invite works with `POST /api/auth/register-with-invite`
- [ ] All endpoints require authenticated cookie
- [ ] Tokens are 32-char hex (not human-readable strings)
- [ ] RFC3339 timestamps in invite JSON