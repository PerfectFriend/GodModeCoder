# BIP39 Auth Reference

## Mnemonic Generation
- 24-word BIP39 English wordlist (2048 words)
- 256-bit entropy + 8-bit checksum = 264 bits = 24 words
- Generated via `crypto/bip39.GenerateMnemonic()`

## Mnemonic Validation
- 12 or 24 words only
- Each word must be in BIP39 wordlist
- Checksum verification via SHA512 of entropy
- Implementation in `internal/crypto/bip39/bip39.go`

## Key Derivation
- PBKDF2(mnemonic, "mnemonic"+passphrase, 2048, 64, SHA512)
- First 32 bytes = Ed25519 private key seed
- Ed25519 keypair via `ed25519.NewKeyFromSeed()`

## API Integration
- `/api/auth/register-with-invite` returns `mnemonic` + `pubkey` (64 hex chars)
- `/api/auth/restore` validates mnemonic derives same pubkey
- Old password invalidated after restore

## Wordlist
Official BIP39 English (2048 words) in `internal/crypto/bip39/wordlist.go`