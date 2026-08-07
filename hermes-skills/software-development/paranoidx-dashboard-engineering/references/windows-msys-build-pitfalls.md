# Windows/MSYS Build Pitfalls — Reference for ParanoidX Development

**Discovered:** 2026-08-05 (ParanoidX autonomous evolution session)

## Critical Path Mismatch

| Path | Status | Contains |
|------|--------|----------|
| `/mnt/c/Users/tomas/ParanoidX-backup/codebase` | ✅ **Real Go module** | `main.go`, all `internal/*` packages |
| `/home/tomas/ParanoidX/` | ❌ **Partial copy** | configs only, missing `main.go` |

**Always build from:**
```bash
cd /mnt/c/Users/tomas/ParanoidX-backup/codebase && go build -o /home/tomas/bin/ParanoidX ./cmd/ParanoidX
```

## write_file Path Trap on Windows Host

- Linux-style paths (`/home/tomas/...`) silently land in WRONG place (`\home\tomas\...` on Windows FS)
- Use `C:\Users\...` or `/mnt/c/Users\...` for write_file/patch
- bash heredoc in `wsl -c` destroys Go string quotes (`\"` → empty) → use `write_file` instead

## Binary Copy & Restart Workflow

```bash
cp /tmp/ParanoidX /home/tomas/bin/ParanoidX  # NOT C:\Users\...
pkill -9 -f "ParanoidX"
/home/tomas/bin/ParanoidX -data /mnt/c/ParanoidX-data -listen 0.0.0.0:8080 &
```

## Dashboard File Trap (TWO files exist)

| File | Served by Server? | Notes |
|------|-------------------|-------|
| `C:\ParanoidX-data\dashboard.html` (= `/mnt/c/ParanoidX-data/dashboard.html`) | ✅ YES | This is what the server actually serves (`-data /mnt/c/ParanoidX-data`) |
| `C:\Users\tomas\ParanoidX-data\dashboard.html` | ❌ NO | Editing this does NOTHING visible |

**Always verify before editing:**
```bash
curl localhost:8080/ | md5sum        # what the server returns
md5sum /mnt/c/ParanoidX-data/dashboard.html  # candidate file
# After editing: copy to served path + re-verify md5 matches
```

**Browser caches aggressively** → hard-refresh (Ctrl+F5) or `?v=` cache-buster

## Go Shim Pattern for Missing Handlers (2026-08-05)

**Problem:** Large legacy codebase references handlers that don't exist yet — blocks `go build`.

**Solution:** Create `internal/api/main_shim.go` with minimal valid handlers:

```go
func ClaimDividendsHandler(dataDir string) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        writeJSON(w, map[string]any{"ok": false, "error": "not implemented"})
    }
}
```

**Wire in `feature_routes.go`:** `api.RegisterTreasuryRoutes(dataDir, authMgr)` + wallet exchange routes.

**Iterative fill:** Replace shim with real logic one-by-one; binary stays buildable throughout.

**Key imports:** `math/big` for amounts, `time` for tx hashes, `fmt` for Sscanf.