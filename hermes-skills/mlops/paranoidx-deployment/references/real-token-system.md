# Real Cryptographic Token System

## Token Generation
```python
import secrets
token = secrets.token_hex(16)  # 32-char hex, 128-bit entropy
```

## Token Storage (invites.json)
```json
{
  "token": "a1b2c3d4e5f6...",
  "created_by": "system|username",
  "created_at": "2026-08-06T18:45:10Z",
  "expires_at": "0001-01-01T00:00:00Z",
  "max_uses": 0,
  "uses": 0,
  "role": "user|admin",
  "note": "description"
}
```

- `max_uses=0` = unlimited
- `expires_at=zero` = no expiry
- RFC3339 timestamps (UTC, Z suffix)

## Registration UI
Plain text input: `<input type="text" id="invite" placeholder="Enter your invite token" required>`

## API Endpoints
| Endpoint | Auth | Purpose |
|----------|------|---------|
| `/api/auth/register-with-invite` | No | Register with token → returns mnemonic, pubkey, token |
| `/api/auth/create-invite` | Yes | Create new token with custom properties |
| `/api/wallet/keys` | Yes | Export {mnemonic, pubkey, privkey} for sidechain |
| `/api/wallet/verify-key` | Yes | Verify pubkey for API access |

## Sidechain Integration
TLR (TRON), ARGENTUM (TON), NT (NanoTaler) apps use:
1. `GET /api/wallet/keys` → `{mnemonic, pubkey, privkey}`
2. Use `privkey` to sign requests
3. `POST /api/wallet/verify-key` with `pubkey` → validates ownership

## Key Lesson
User explicitly rejected fake strings like "GodModeToken" and dropdowns. Real tokens = cryptographically secure random hex, validated via JSON lookup.