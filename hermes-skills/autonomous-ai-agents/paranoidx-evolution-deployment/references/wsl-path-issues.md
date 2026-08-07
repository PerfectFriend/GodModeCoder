# WSL Path Resolution — Root Cause Analysis & Fixes

## The Problem

During this session, the agent repeatedly created and referenced paths like `/c/ParanoidX` and `/c/c/ParanoidX-data` which are **incorrect**. 

The root cause: **WSL mounts Windows C: drive at `/mnt/c/`, NOT `/c/`**.

This caused multiple failures:
- `evolution_cycle.py` failing with "No such file or directory" when accessing `/c/ParanoidX/`
- Duplicate `ParanoidX-data` folder created at `/c/c/ParanoidX-data/` 
- Scripts and commands failing because they used the wrong mount point

## Correct Mount Points (from `mount | grep -E "^C:"`)

```
C:\ on /mnt/c type 9p (rw,noatime,aname=drvfs;path=C:\;uid=1000;gid=1000;metadata;uid=1000;gid=1000;umask=0022;symlinkroot=/mnt/,cache=0x5,access=client,msize=65536,trans=fd,rfd=6,wfd=6)
C:\Program Files\Docker\Docker\resources on /Docker/host type 9p (rw,noatime,aname=drvfs;path=C:\Program)
D: on /mnt/d type 9p (rw,relatime,aname=drvfs;path=D:;symlinkroot=/mnt/,cache=0x5,access=client,msize=65536,trans=fd,rfd=3,wfd=3)
```

## Path Mapping Table

| Windows Path | Correct WSL Path | **INCORRECT** (what was used) |
|-------------|------------------|------------------------------|
| `C:\ParanoidX` | `/mnt/c/ParanoidX` | `/c/ParanoidX` |
| `C:\ParanoidX-data` | `/mnt/c/ParanoidX-data` | `/c/ParanoidX-data` or `/c/c/ParanoidX-data` |
| `D:\backups` | `/mnt/d/backups` | `/d/backups` |

## How the Error Propagated

1. **Initial confusion** — WSL also creates a symlink `/c` → `/mnt/c` in some configurations, but it's not reliable
2. **`/c/c/` artifact** — When the script used `/c/ParanoidX-data` and the Go server wrote to it via `-data /c/ParanoidX-data`, and then subsequent operations prepended another `/c/`, creating the nested `/c/c/ParanoidX-data/`
3. **Cron job failure** — The evolution script ran on WSL Python with hardcoded `/c/` paths, causing FileNotFoundError

## Fix Applied

**`evolution_cycle.py` config section corrected to use WSL mount paths:**

```python
# Config - WSL paths since this runs inside WSL (cron job)
# In WSL, C: is mounted at /mnt/c/ and D: at /mnt/d/
PARANOIDX_SRC = "/mnt/c/ParanoidX"
PARANOIDX_DATA = "/mnt/c/ParanoidX-data"
BACKUP_DIR = "/mnt/d/backups"           # CRITICAL: USB drive D:\ only! (WSL: /mnt/d/backups)
WSL_BINARY = "/home/tomas/bin/ParanoidX"
WSL_DATA = "/mnt/c/ParanoidX-data"
```

**All commands in the script now use direct WSL paths** (no `wsl -- bash` wrapper needed since the script runs inside WSL):
- `cd /mnt/c/ParanoidX && go build ...`
- `pkill -f ParanoidX`
- `nohup /home/tomas/bin/ParanoidX -data /mnt/c/ParanoidX-data ...`
- `ss -tlnp | grep :8080`
- `tail -50 /tmp/paranoidx.log`

## Verification

After the fix, ad-hoc verification confirmed:
- ✅ Config file accessible at `/mnt/c/ParanoidX-data/simplex-node.json`
- ✅ Dashboard version readable at `/mnt/c/ParanoidX-data/dashboard.html` → **A38**
- ✅ Backup directory writable at `/mnt/d/backups` — 78 backup files found
- ✅ Syntax check passes
- ✅ All 11 verification checks pass

## Pitfall Prevention

**Always verify WSL mount points before writing paths in scripts:**
```bash
# In WSL, check actual mount:
mount | grep -E "^C:|^/mnt/c"

# Or simply:
ls -la /mnt/c/ParanoidX/
```

**Never assume `/c/` works** — it's a legacy symlink that may not exist or may point to wrong location. The official, stable mount is `/mnt/c/`.

## Related Files Fixed

- `C:\ParanoidX\scripts\evolution_cycle.py` — Updated config to use `/mnt/c/` and `/mnt/d/`
- Deleted spurious `/c/c/ParanoidX-data/` and `/c/c/Users/` directories