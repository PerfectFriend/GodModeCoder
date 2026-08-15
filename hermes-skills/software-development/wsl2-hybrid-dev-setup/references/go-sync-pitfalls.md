# Go Concurrency Pitfalls — RW-Mutex Reentrancy Deadlock & Data Race

Two real bugs caught by ad-hoc unit tests in a Go backend (ParanoidX auth package, 2026-08-05).

## Pitfall 1: RWMutex is NOT reentrant — lock-then-call-helper deadlock

**Symptom**: `go test` hangs forever (300s timeout hits). Goroutine dump shows:
```
goroutine 8 [sync.RWMutex.RLock]:
sync.runtime_SemacquireRWMutexR
sync.(*RWMutex).RLock
ParanoidX/internal/auth.(*AuthManager).saveUsers(0xc0000dc690)
ParanoidX/internal/auth.(*AuthManager).ensureAdminUser
ParanoidX/internal/auth.NewAuthManager
ParanoidX/internal/auth_test.TestAdminCreatedWithForcedChange
```

**Root cause**: helper `saveUsers()` took `am.mu.RLock()`, but every caller
(`ensureAdminUser`, `Authenticate`, `ChangePassword`, `CreateUser`) already held
`am.mu.Lock()`. Go's `sync.RWMutex` is not reentrant — an `RLock` from a
goroutine that already holds `Lock` blocks forever (a second `Lock` would
deadlock the same way).

**Fix pattern**: split into a locked helper — the helper does NO locking, the
caller (which holds the lock) invokes it:

```go
// saveUsersLocked writes users to file. Caller must hold am.mu.Lock().
func (am *AuthManager) saveUsersLocked() error {
    data, err := json.MarshalIndent(am.users, "", "  ")
    if err != nil { return err }
    return os.WriteFile(am.usersFile, data, 0600)
}
```
Replace ALL `am.saveUsers()` calls inside lock-holding methods with `am.saveUsersLocked()`.
Greppable: `grep -n "saveUsers()"` should return zero after the rename.

## Pitfall 2: Mutating map values under RLock — data race

**Symptom**: `go test -race` reports race on `u.PasswordHash`.

**Root cause**:
```go
for _, u := range am.users {
    u.PasswordHash = ""   // writes through the map's pointer while other goroutines may read
    users = append(users, u)
}
```

**Fix**: copy the struct before mutating:
```go
for _, u := range am.users {
    clone := *u
    clone.PasswordHash = ""
    users = append(users, &clone)
}
```

## Ad-hoc verification recipe (temp test file, run, delete)

To prove a fix without committing test files to the repo:

1. Write a temp `*_test.go` in the package dir (via `write_file` to the Windows
   path if working through WSL bind mounts — heredocs strip `\"` quotes).
2. `go test ./internal/auth/ -v -run 'TestAdmin|TestForce' -timeout 120s`
3. Read the failing API from the compiler: the test compiles against the REAL
   package — method names/arity in your test must match actual code
   (`Authenticate` not `Login`, `GetUser` returns 2 values, field is
   `ForcePasswordChange` not `MustChangePassword`). Iterate until green.
4. `rm` the temp test file; re-`go build ./internal/auth/` to confirm clean.

The deadlock only manifests at runtime, not compile time — the unit test with a
short timeout is what surfaces it. Keep `-timeout` short (120s) so a hang fails
fast instead of blocking the terminal for the default 10m.
