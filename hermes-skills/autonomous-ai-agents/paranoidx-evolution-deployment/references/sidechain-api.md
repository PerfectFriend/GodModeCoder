# ParanoidX Sidechain Wallet API Reference

## Overview
Sidechain applications (TLR on TRON, ARGENTUM on TON, NT/NanoTaler native) authenticate via Ed25519 keypair derived from user's BIP39 mnemonic. All endpoints require authenticated session (`dashboard_token` cookie).

## Endpoints

### GET /api/wallet/keys
Export wallet keys for sidechain API access.

**Response:**
```json
{
  "username": "sidechain_user",
  "mnemonic": "volume original insane primary input bike assume silent able collect isolate question team staff step smile diary boost arctic cruise unveil patrol divorce demand",
  "pubkey": "1d8b5fa9c9033c463ee709cd955f80c1e0a9dd861e350add120c8f5deceeadd0",
  "privkey": "1d8b5fa9c9033c463ee709cd955f80c1e0a9dd861e350add120c8f5deceeadd0",
  "note": "Keep these keys secure. Used for TLR/ARGENTUM/NT sidechain API access."
}
```

**Usage:**
```bash
curl -k -b cookies.txt https://172.25.101.187:8080/api/wallet/keys
```

### POST /api/wallet/verify-key
Verify an API public key belongs to the authenticated user.

**Request:**
```json
{ "pubkey": "1d8b5fa9c9033c463ee709cd955f80c1e0a9dd861e350add120c8f5deceeadd0" }
```

**Response:**
```json
{ "ok": true, "pubkey": "1d8b5fa9c9033c463ee709cd955f80c1e0a9dd861e350add120c8f5deceeadd0", "user": "sidechain_user" }
```

## Integration Patterns

### Sidechain App Flow
1. User registers via `register.html` with `GodModeToken` (admin) or `UNIVERSAL-UNLIMITED` (user)
2. App calls `/api/wallet/keys` to get user's Ed25519 keypair
3. Sidechain app signs transactions with `privkey`
4. Sidechain service verifies signatures using `pubkey` via `/api/wallet/verify-key`

### Supported Networks
| Network | Token | Transport | Use Case |
|---------|-------|-----------|----------|
| TRON | TLR | TRC20 | Fast payments, energy rental |
| TON | ARGENTUM | Jetton | High-throughput, low-fee |
| Native | NT | NanoTaler (ParanoidX) | Silver-backed, dividends, NFT banknotes |

## Invite Tokens Reference

### GodModeToken
- **Role**: admin
- **Max Uses**: 0 (unlimited)
- **Expires**: never
- **Created By**: system
- **Pre-seeded**: Yes in `invites.json`

### UNIVERSAL-UNLIMITED
- **Role**: user
- **Max Uses**: 0 (unlimited)
- **Expires**: never
- **Created By**: system
- **Pre-seeded**: Yes in `invites.json`

### Custom Invites (via API)
```bash
curl -k -b cookies.txt -X POST https://172.25.101.187:8080/api/auth/create-invite \
  -H "Content-Type: application/json" \
  -d '{"expires_in_hours": 24, "max_uses": 5, "role": "user", "note": "Beta access"}'
```

Response:
```json
{ "ok": true, "token": "a1b2c3d4...", "expires": 24, "max_uses": 5, "role": "user", "note": "Beta access" }
```

## Registration UI
`register.html` dropdown now includes:
- `GodModeToken (admin, unlimited, no expiry)` — admin role
- `UNIVERSAL-UNLIMITED (user, unlimited, no expiry)` — user role (default)

## Security Notes
- Keys exported via `/api/wallet/keys` are **raw Ed25519 private keys** — treat as high-value secrets
- Sidechain apps should store keys in secure enclaves / hardware wallets
- ParanoidX does not log exported keys
- Mnemonic never leaves server in plaintext except on this endpoint
- All endpoints require valid session cookie (24h TTL)