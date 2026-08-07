# BIP39 Integration in ParanoidX

## Overview
ParanoidX uses BIP39 (Bitcoin Improvement Proposal 39) for deterministic wallet seed phrase generation and recovery. Each user account gets a 24-word mnemonic that maps to an Ed25519 keypair for cryptographic operations.

## Components

### 1. Mnemonic Generation (`internal/crypto/bip39/bip39.go`)
```go
func GenerateMnemonic() (string, error) {
    entropy := make([]byte, 32)  // 256 bits = 24 words
    if _, err := rand.Read(entropy); err != nil {
        return "", err
    }
    return MnemonicFromEntropy(entropy)
}
```

### 2. Mnemonic Validation (Checksum)
```go
func EntropyFromMnemonic(mnemonic string) ([]byte, error) {
    words := strings.Fields(mnemonic)
    if len(words) < 12 || len(words) > 24 || len(words)%3 != 0 {
        return nil, fmt.Errorf("invalid mnemonic length: %d", len(words))
    }
    // ... word lookup + checksum verification
    // Checksum: first (entropy_bits/32) bits of SHA512(entropy)
}
```

### 3. Ed25519 Keypair Derivation
```go
func KeypairFromMnemonic(mnemonic, passphrase string) (pubkeyHex, privkeyHex string, err error) {
    seed := PBKDF2([]byte(mnemonic), []byte("mnemonic"+passphrase), 2048, 64, sha512.New)
    priv := ed25519.NewKeyFromSeed(seed[:32])
    pub := priv.Public().(ed25519.PublicKey)
    return hex.EncodeToString(pub), hex.EncodeToString(priv), nil
}
```

## User Account Fields
```go
type User struct {
    Username             string    `json:"username"`
    PasswordHash         string    `json:"password_hash"`
    Role                 string    `json:"role"`
    ForcePasswordChange  bool      `json:"force_password_change"`
    CreatedAt            time.Time `json:"created_at"`
    LastLogin            *time.Time `json:"last_login,omitempty"`
    Mnemonic             string    `json:"mnemonic,omitempty"`      // BIP39 seed phrase
    Pubkey               string    `json:"pubkey,omitempty"`        // Ed25519 pubkey (hex)
}
```

## Registration Flow
1. User submits username, password, invite, optional mnemonic
2. If mnemonic provided: validate via `EntropyFromMnemonic()`, derive pubkey via `KeypairFromMnemonic()`
3. If mnemonic omitted: generate new via `GenerateMnemonic()`, derive pubkey
4. Store mnemonic + pubkey in user record

## Restore Flow (Password/Username Recovery)
1. User submits username, mnemonic, new password
2. Lookup existing user, get stored pubkey
3. Validate mnemonic checksum via `EntropyFromMnemonic()`
4. Derive pubkey from mnemonic via `KeypairFromMnemonic()`
5. Compare derived pubkey with stored pubkey — must match exactly
6. If match: update password, auto-login

## Security Notes
- Mnemonic stored in plaintext in users.json (for recovery) — ensure file permissions 0600
- Passphrase is empty string by default (standard BIP39)
- PBKDF2: 2048 iterations, SHA-512, 64-byte output
- Ed25519 seed: first 32 bytes of PBKDF2 output
- Pubkey stored as hex (64 chars = 32 bytes)

## Test Vectors
Valid BIP39 test mnemonic (12 words):
```
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
```
This has a valid checksum and is commonly used for testing.

Invalid example (fails checksum):
```
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon
```