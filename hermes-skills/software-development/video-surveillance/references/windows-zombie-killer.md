# Windows Zombie Process Killer for Long-Polling Bots

**Problem**: On Windows/MSYS, `process.kill()` or Ctrl-C kills the bash wrapper but often leaves `python.exe` alive and STILL LONG-POLLING the same Telegram token. Result: two bots on one token → 409 Conflict → silent callback/button failure.

**Root cause**: MSYS signal handling — the shell receives SIGTERM, forwards to the child group, but Python's signal handler may not exit cleanly from `requests.post(getUpdates)` blocking call. The orphan survives and continues polling.

**Solution**: At script startup, kill ALL other `python.exe` processes running the same script EXCEPT the current one. Use `psutil` to get the real python.exe PID (not the MSYS bash wrapper PID), then PowerShell to kill by PID.

## Code Pattern (from panic_mode.py)

```python
def kill_other_instances():
    """\"\"\"Kill every python.exe running panic_mode.py EXCEPT the current process.
    A zombie that survived a shell 'kill' keeps Telegram long-polling and
    answers commands with stale in-memory state - two bots on one token is
    exactly how an old target kept resurrecting. PowerShell is used (MSYS
    mangles $_ in bash); file-based so MSYS can't corrupt it.\"\"\"
    import subprocess
    try:
        # Get the ACTUAL python.exe PID (not bash wrapper PID in MSYS)
        import psutil
        mypid = psutil.Process().pid
        # Build PS command in a file to avoid MSYS mangling
        ps_script = f\"\"\"$mypid = {mypid}
Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" |
Where-Object {{ $_.CommandLine -match 'panic_mode' -and $_.ProcessId -ne \\$mypid }} |
ForEach-Object {{ Stop-Process -Id \\$_.ProcessId -Force; Write-Output ('killed ' + \\$_.ProcessId) }}
\"\"\"
        with open(\"kill_zombies.ps1\", \"w\", encoding=\"utf-8\") as f:
            f.write(ps_script)
        # Use errors=\"ignore\" for PowerShell stderr (Cyrillic on RU Windows)
        r = subprocess.run([\"powershell\", \"-NoProfile\", \"-File\", \"kill_zombies.ps1\"],
                          capture_output=True, text=True, timeout=20, encoding=\"utf-8\", errors=\"ignore\")
        if r.stdout.strip():
            print(f\"  killed stale instance(s): {r.stdout.strip()}\", flush=True)
    except Exception as e:
        print(f\"  zombie kill err: {e}\", flush=True)
```

### CRITICAL FIX (2026-08-06): Dynamic PID in kill_zombies.ps1

The standalone `kill_zombies.ps1` file MUST use `$PID` (PowerShell automatic variable), NOT a hardcoded PID:

```powershell
# CORRECT - uses $PID (current PowerShell process)
$mypid = $PID
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
Where-Object { $_.CommandLine -match 'panic_mode' -and $_.ProcessId -ne $mypid } |
ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Output ('killed ' + $_.ProcessId) }

# WRONG - hardcoded PID (breaks on every restart)
$mypid = 27100  # BROKEN - only works once
```

**Root cause of 2026-08-06 bug**: The standalone `kill_zombies.ps1` had a hardcoded PID (`$mypid = 27100`) from an earlier generation. When panic_mode.py generated a fresh file, it wrote the correct dynamic `$mypid = {mypid}`, but if the file was manually edited or cached, the hardcoded version would break PowerShell parsing with:
```
ОШИБКА: "ExpectedValueExpression" near "$mypid"
```

The Python code generates the correct dynamic version, but the standalone file must ALSO use `$PID` for manual runs.

## Key Details

- **Use `psutil.Process().pid`**, NOT `os.getpid()` — the latter returns the MSYS bash wrapper PID on Windows
- **Write PowerShell script to a file** — inline `-Command` strings get mangled by MSYS (`$_` substitution breaks)
- **Use `errors="ignore"`** on subprocess run — PowerShell stderr on RU Windows is cp866, not UTF-8
- **Call at the VERY START of `__main__`** — before `load_settings()`, before any threads start
- **`psutil` is a required dependency** — add to requirements.txt

## Diagnosing Zombies

```powershell
# PowerShell: list all python.exe with command line
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -match 'panic_mode' } |
  Select-Object ProcessId, CommandLine

# Kill by PID (if kill_zombies.ps1 didn't catch them)
Stop-Process -Id <PID> -Force
```

## When to Suspect Zombies

- User says "button works sometimes, sometimes not" (409 with self)
- Bot "stopped responding" but process shows `running`
- `getUpdates` returns 409 Conflict even after restarting Hermes gateway
- Multiple `python.exe panic_mode.py` in process list

**Always run `kill_zombies.ps1` manually before declaring a bot bug** — 90% of "ghost" issues are zombies.