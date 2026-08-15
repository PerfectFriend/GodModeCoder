# Zombie Killer Pattern — Detailed Reproduction & Fix

## Problem
On Windows with MSYS/bash, `process.kill()` or shell `kill` only terminates the **bash wrapper process**. The actual `python.exe` survives and continues long-polling Telegram.

**Result**: Two (or more) bots on the same token → Telegram distributes updates round-robin → commands answered with **stale in-memory state**.

## Reproduction
1. Start bot via MSYS: `python panic_mode.py` (PID 1234 = bash, PID 5678 = python.exe)
2. `kill 1234` (or Hermes `process.kill`)
3. Bash dies, `python.exe` 5678 survives, keeps polling
4. Restart bot → new python.exe 9012 starts
5. Both 5678 and 9012 poll same token → 50/50 chance each command hits zombie
6. Zombie has old `TARGET_DESC`, `ZONE`, `LANG` in memory → `save_settings()` overwrites file with stale values

## Root Cause
- `os.getpid()` in MSYS returns **bash PID**, not python.exe PID
- PowerShell `Get-CimInstance Win32_Process` sees only python.exe processes
- `$_` variable mangled by MSYS in inline PowerShell commands

## Solution
```python
def kill_other_instances():
    import psutil, subprocess
    mypid = psutil.Process().pid  # REAL python.exe PID
    ps_script = f"""$mypid = {mypid}
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object {{ $_.CommandLine -match 'panic_mode' -and $_.ProcessId -ne $mypid }} |
    ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}
    """
    with open("kill_zombies.ps1", "w", encoding="utf-8") as f:
        f.write(ps_script)
    subprocess.run(["powershell", "-NoProfile", "-File", "kill_zombies.ps1"],
                   capture_output=True, text=True, timeout=20, encoding="utf-8", errors="ignore")
```

## Key Points
1. **Use `psutil.Process().pid`** — returns actual python.exe PID on Windows
2. **Write PS script to file** — avoids MSYS mangling of `$_`, quotes, `$PID`
3. **`encoding="utf-8", errors="ignore"`** — Windows RU locale stderr is cp866
4. **Call at `__main__` entry** — before `load_settings()` or any Telegram calls
5. **Match by script name** — `CommandLine -match 'panic_mode'` (or your bot name)

## Verification
```powershell
# Before fix: kill leaves python.exe alive
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'panic_mode' }

# After fix: new process kills old ones at startup
# Log shows: "killed stale instance(s): 5678"
```