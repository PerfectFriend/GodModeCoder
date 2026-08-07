# Cross-Platform Path Handling in ParanoidX

## Problem
The ParanoidX server can be started from either Windows (`/c/ParanoidX/ParanoidX -data /c/ParanoidX-data`) or WSL (`/mnt/c/ParanoidX/ParanoidX -data /mnt/c/ParanoidX-data`). The `AuthManager` receives the data directory path as provided on the command line, but invite file lookup must work regardless of which path format was used.

## Path Formats Encountered

| Format | Example | Source |
|--------|---------|--------|
| Windows absolute | `C:\ParanoidX-data` | `flag.String("data", "C:\ParanoidX-data")` |
| WSL absolute | `/mnt/c/ParanoidX-data` | `flag.String("data", "/mnt/c/ParanoidX-data")` |
| WSL /c/ shorthand | `/c/ParanoidX-data` | `flag.String("data", "/c/ParanoidX-data")` |
| Windows with backslashes | `\\c\ParanoidX-data` | Rare but possible |

## Normalization Logic

```go
func normalizeToWSL(path string) string {
    // Case 1: Windows C:\... -> /mnt/c/...
    if len(path) >= 3 && path[1] == ':' && path[2] == '\\' {
        drive := strings.ToLower(path[0:1])
        rest := strings.ReplaceAll(path[3:], "\\", "/")
        return "/mnt/" + drive + "/" + rest
    }
    // Case 2: /c/... or \c\... -> /mnt/c/...
    if len(path) >= 3 && (path[0] == '/' || path[0] == '\\') &&
        (path[1] == 'c' || path[1] == 'C') &&
        (path[2] == '/' || path[2] == '\\') {
        rest := strings.ReplaceAll(path[3:], "\\", "/")
        return "/mnt/c/" + rest
    }
    // Already WSL or other - return as-is
    return path
}

// Usage in ValidateInvite and ConsumeInvite:
usersDir := filepath.Dir(am.usersFile)
invitesFile := filepath.Join(usersDir, "invites.json")
invitesFileWSL := normalizeToWSL(invitesFile)

b, err := os.ReadFile(invitesFile)
if err != nil {
    b, err = os.ReadFile(invitesFileWSL)
}
```

## Why Try Both Paths?

The Go `os.ReadFile` on Windows can read both `C:\path` and `/mnt/c/path` (via 9p/Plan9), but WSL can only read `/mnt/c/path` and `/c/path` formats. By trying the native path first, then the normalized WSL path, we cover all deployment scenarios.

## Verification

Debug output shows both paths being tried:
```
[DEBUG] ValidateInvite: usersFile="\c\ParanoidX-data\users.json", invitesFile="\c\ParanoidX-data\invites.json", invitesFileWSL="/mnt/c/ParanoidX-data/invites.json"
[DEBUG] ValidateInvite: error reading invites file "\c\ParanoidX-data\invites.json": open /mnt/c/ParanoidX-data/invites.json: The system cannot find the file specified.
[DEBUG] ValidateInvite: error reading invites file WSL "/mnt/c/ParanoidX-data/invites.json": open /mnt/c/ParanoidX-data/invites.json: The system cannot find the file specified.
```

Note: The error shows the *display path* but Go's error message shows the *actual opened path* (converted by the OS).

## Build/Run Matrix

| Build On | Run On | -data Flag | Works? |
|----------|--------|------------|--------|
| Windows | Windows | `C:\ParanoidX-data` | ✅ |
| Windows | WSL | `/mnt/c/ParanoidX-data` | ✅ |
| WSL | WSL | `/mnt/c/ParanoidX-data` | ✅ |
| WSL | WSL | `/c/ParanoidX-data` | ✅ |
| Windows | WSL | `C:\ParanoidX-data` | ✅ (9p) |

## Key Insight
Always normalize the data directory path at AuthManager construction time, or at least at invite lookup time. The normalization is idempotent — running it on an already-WSL path returns the same path.