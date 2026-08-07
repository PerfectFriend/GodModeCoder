# Auth RW-Mutex Deadlock — Recognition & Fix

## When it happens
First login attempt hangs forever; server becomes unresponsive on `/login` and `/api/auth/*`.

## Goroutine dump signature
`go test` hangs → `kill -QUIT <pid>` or test timeout prints:

```
goroutine 8 [sync.RWMutex.RLock]:
sync.(*RWMutex).RLock(...)
ParanoidX/internal/auth.(*AuthManager).saveUsers(0x...)
    auth.go:93
ParanoidX/internal/auth.(*AuthManager).ensureAdminUser(0x...)
    auth.go:118
ParanoidX/internal/auth.NewAuthManager({...})
    auth.go:64
```

Key tell: `saveUsers` (which does `RLock`) is called from `ensureAdminUser` / `Authenticate` /
`ChangePassword` / `CreateUser` — all of which already hold `mu.Lock()`. `sync.RWMutex` is
NOT reentrant: a second lock acquisition on the same goroutine blocks forever.

## Root cause (as found 2026-08-05)
```go
func (am *AuthManager) saveUsers() error {
    am.mu.RLock()          // <-- blocks: caller already holds Lock()
    defer am.mu.RUnlock()
    ...
}
func (am *AuthManager) ensureAdminUser() {
    am.mu.Lock()
    defer am.mu.Unlock()
    ...
    am.saveUsers()         // <-- deadlock
}
```

## Fix
Rename to `saveUsersLocked()` with NO locking inside; every caller already holds `Lock()`:
```go
// saveUsersLocked writes users to file. Caller must hold am.mu.Lock().
func (am *AuthManager) saveUsersLocked() error {
    data, err := json.MarshalIndent(am.users, "", "  ")
    ...
}
```
Update all 4 call sites (ensureAdminUser, Authenticate, ChangePassword, CreateUser).

## Related data race found in same pass
`ListUsers()` mutated `u.PasswordHash = ""` on the stored pointer under `RLock()` → race with
writers. Fix: clone struct before clearing the hash.

## Verification
`scripts/verify-auth.sh` — build + vet + temp `_test.go` (admin login with forced change,
force-change clears flag, old password rejected). A test that hangs >100s = deadlock regression.
