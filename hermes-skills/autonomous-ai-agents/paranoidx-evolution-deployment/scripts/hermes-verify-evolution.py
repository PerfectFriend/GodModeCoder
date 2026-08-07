# Ad-hoc Verification Script for evolution_cycle.py Fixes

## Script: `hermes-verify-evolution.py`

### Purpose
Verify the fixes applied to `evolution_cycle.py` work correctly before running the full evolution cron.

### Usage
```bash
python C:\Users\tomas\AppData\Local\Temp\hermes-verify-evolution.py
```

### Tests Performed
1. **Version badge functions** — `get_version_badge()`, `increment_version()`, `set_version_badge()`
2. **Config paths** — Verify Windows paths are used (`C:\ParanoidX`, `D:\backups`, etc.)
3. **Backup creation** — Test `backup_to_usb()` with temp directories, verify `os.makedirs()` fix
4. **Config loading** — Test `load_config()` with temp simplex-node.json

### Expected Output
```
==================================================
VERIFICATION: evolution_cycle.py fixes
==================================================
Testing version badge functions...
  ✅ get_version_badge: A07
  ✅ increment_version: A07 → A08
  ✅ set_version_badge: verified A08

Testing config paths...
  ✅ PARANOIDX_SRC: C:\ParanoidX
  ✅ PARANOIDX_DATA: C:\ParanoidX-data
  ✅ BACKUP_DIR: D:\backups
  ✅ CONFIG_FILE: C:\ParanoidX-data\simplex-node.json

Testing backup creation...
  ✅ Backup created: paranoidx-evolution-A00-cycle01-<timestamp>.tar.gz
  ✅ Size: XXX bytes
  ✅ SHA256: <hash>...

Testing config loading...
  ✅ load_config: token=TEST_TOK..., chat_id=12345

==================================================
✅ ALL VERIFICATION TESTS PASSED
==================================================
```

### Key Assertions
- All config constants use Windows raw string paths (`r"C:\..."`)
- `backup_to_usb()` creates backup directory if missing
- Version badge increments correctly (A07 → A08, A09 → A10)
- `load_config()` parses JSON correctly

### When to Run
- After any changes to `evolution_cycle.py`
- Before deploying cron job changes
- After WSL2 IP changes (update `TEST_BASE_URL`)