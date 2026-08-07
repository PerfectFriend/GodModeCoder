# ParanoidX Autonomous Evolution Cycle Script

## Script: `scripts/evolution_cycle.py`

### Purpose
Runs one complete evolution cycle:
1. **Pre-backup** → D:\backups (tar.gz)
2. **Build** → Go binary in WSL2 (`/home/tomas/bin/ParanoidX`)
3. **Deploy** → Restart server with new binary
4. **Tests** → Full API test suite (11 endpoints)
5. **Version Increment** → dashboard.html badge A{NN} → A{NN+1}
6. **Post-backup** → D:\backups
7. **Telegram Report** → Cycle summary

### Usage
```bash
# Single cycle
python3 scripts/evolution_cycle.py 1

# Full 20-cycle run (with 2h delays)
python3 scripts/evolution_cycle.py 20
```

### Config (Top of Script) — **WSL paths** (runs on WSL Python)
```python
# Config - WSL paths since this runs inside WSL (cron job)
# In WSL, C: is mounted at /mnt/c/ and D: at /mnt/d/
PARANOIDX_SRC = "/mnt/c/ParanoidX"
PARANOIDX_DATA = "/mnt/c/ParanoidX-data"
BACKUP_DIR = "/mnt/d/backups"           # CRITICAL: USB drive D:\ only! (WSL: /mnt/d/backups)
WSL_BINARY = "/home/tomas/bin/ParanoidX"
WSL_DATA = "/mnt/c/ParanoidX-data"
DASHBOARD_HTML = os.path.join(PARANOIDX_DATA, "dashboard.html")
LOGIN_HTML = os.path.join(PARANOIDX_DATA, "login.html")
REGISTER_HTML = os.path.join(PARANOIDX_DATA, "register.html")
CONFIG_FILE = os.path.join(PARANOIDX_DATA, "simplex-node.json")
CYCLES = 20
TEST_BASE_URL = "https://172.25.101.187:8080"  # WSL2 eth0 IP accessible from Windows
```

### Cron Job
- **Job ID**: `cca91e6c1ae2`
- **Schedule**: `every 120m` (every 2 hours)
- **Workdir**: `/mnt/c/ParanoidX` (WSL path)
- **Script**: `evolution_cycle.py 1`
- **Delivery**: `telegram`
- **Skills**: `paranoidx-evolution-deployment`

### Backup Naming
```
pre:  paranoidx-evolution-A{NN}-cycle{NN}-{timestamp}.tar.gz
post: paranoidx-evolution-A{NN}-cycle{NN}-{timestamp}.tar.gz
```

### Version Badge Logic
```python
def increment_version(current: str) -> str:
    # A07 -> A08, A09 -> A10, etc.
    num = int(current[1:]) + 1
    return f"A{num:02d}"
```

### Telegram Report Format
```
🧬 ParanoidX Evolution Cycle {N}/{20}
✅ Backup: {size} MB
✅ Build: success
✅ Deploy: pid={pid}
✅ Tests: 11/11 passed
✅ Version: A{NN} → A{NN+1}
✅ Post-backup: {size} MB
⏱ Duration: {duration}s
```

### Critical Fixes (This Session)

1. **WSL mount paths** — C: is mounted at `/mnt/c/` in WSL, NOT `/c/`. This was the root cause of "No such file or directory" errors when the script tried to access `/c/ParanoidX/`. Use `/mnt/c/ParanoidX` and `/mnt/c/ParanoidX-data`.

2. **Python execution environment** — The cron job runs on WSL Python (`/usr/bin/python3`), NOT Windows Python. The script must use WSL paths throughout.

3. **Backup directory creation** — Added `os.makedirs(BACKUP_DIR, exist_ok=True)` before creating tarballs to handle missing `/mnt/d/backups` directory.

4. **Build command** — Uses `cd /mnt/c/ParanoidX && go build -o /home/tomas/bin/ParanoidX ./cmd/ParanoidX` (direct WSL command, no `wsl -- bash` wrapper).

5. **Server restart pattern** — Keep WSL shell alive long enough for server to daemonize:
   ```python
   cmd = f'nohup {WSL_BINARY} -data {WSL_DATA} -listen 0.0.0.0:8080 > /tmp/paranoidx.log 2>&1 & sleep 5'
   ok, out, err = run_cmd(cmd, timeout=15)
   time.sleep(3)
   ```
   The `& sleep 5` inside the bash command ensures the shell doesn't exit before the Go server fully detaches.

6. **Test endpoint URL** — Use `https://172.25.101.187:8080` (WSL2 eth0 IP accessible from Windows host). Windows cannot reach WSL2 `127.0.0.1` directly.

7. **Debug cycle WSL commands** — All `ss`, `tail`, `pkill` commands run directly in WSL (no `wsl -- bash` wrapper needed since script runs in WSL).

8. **Error handling** — `err` can be `None`; use `err_msg = err[:200] if err else "Unknown error"` before slicing.

9. **Version badge extraction** — Supports both patterns: `id="dashVersion"` and `class="version-badge"`.

10. **Dashboard version confirmed A38** — 20+ cycles completed successfully, proving the cron job works end-to-end.

### Pitfalls
- **BACKUP DIR MUST BE D:\** — never C:\ or WSL paths (user mandate). In WSL: `/mnt/d/backups`
- WSL2 IP changes on restart — update `TEST_BASE_URL` or use portproxy
- GodModeToken must exist in `invites.json` for admin registrations
- TLS certs must exist for HTTPS verification (`/mnt/c/ParanoidX-data/certs/`)
- All 11 API endpoints must return 200 OK with auth cookie
- **WSL mount point is `/mnt/c/` not `/c/`** — this was a recurring source of path errors
- The evolution script MUST use WSL paths since it runs on WSL Python via cron