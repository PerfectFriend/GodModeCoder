# WSL2 Persistent Daemon + Windows Boot Autostart — Working Recipe

Validated 2026-08-05 on ParanoidX (Go server in Ubuntu-24.04, Windows 11 host).

## Why nohup/setsid fail

`wsl -d Ubuntu-24.04 -- bash -lc "nohup app & ..."` — when the outer `wsl` process
exits, the entire Linux session is torn down; the process group gets SIGTERM.
Log shows: `"msg":"shutdown","signal":15`. `nohup`, `setsid`, `disown` do NOT help.
Only systemd (WSL2 `systemd=true` in `/etc/wsl.conf`) keeps the process alive.

## Step 1 — systemd unit

```ini
[Unit]
Description=App Daemon
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=simple
User=tomas
WorkingDirectory=/home/tomas/app
Environment=SIMPLEX_SRC=/mnt/c/Users/tomas/app-backup/codebase
ExecStart=/home/tomas/bin/app -data /mnt/c/Shared-data -listen :8080
Restart=always
RestartSec=5
StandardOutput=append:/home/tomas/app.log
StandardError=append:/home/tomas/app.log

[Install]
WantedBy=multi-user.target
```

```bash
sudo cp deploy/app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable app        # symlink -> multi-user.target.wants/
sudo systemctl start app
systemctl is-active app          # active
systemctl is-enabled app         # enabled
```

Survival test (critical): exit the terminal entirely, reopen, then
`systemctl is-active app` must still be `active` and HTTP endpoint answering.

## Step 2 — Boot task before login (Task Scheduler, SYSTEM)

A task that fires at Windows boot (before any user logs in) needs a SYSTEM
principal, which requires admin rights. From a non-admin terminal use the
RunAs + cmd-wrapper pattern:

1. Write task XML to a temp file:

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-08-05T00:00:00</Date>
    <Author>tomas</Author>
    <Description>Start WSL2 at boot so systemd daemon comes up automatically.</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>5</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\Windows\System32\wsl.exe</Command>
      <Arguments>-d Ubuntu-24.04 -- /bin/true</Arguments>
    </Exec>
  </Actions>
</Task>
```

2. Create a `.cmd` wrapper that records the result to a file:

```cmd
@echo off
schtasks /Create /TN "App-WSL2-Boot-System" /XML "C:\path\task.xml" /F > C:\path\result.txt 2>&1
```

3. Elevate via PowerShell (UAC prompt appears — user must click Yes):

```powershell
powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/c','C:\path\create-task.cmd' -Verb RunAs -Wait"
```

4. Read result (Russian locale output is cp866):

```bash
cat result.txt | iconv -f cp866 -t utf-8    # "УСПЕХ. ... успешно создана."
```

5. Verify with another elevated cmd wrapper:

```cmd
schtasks /Query /TN "App-WSL2-Boot-System" /V /FO LIST > C:\path\query.txt 2>&1
```
Check: `Запуск от имени: СИСТЕМА` (Run As User: SYSTEM), `Тип расписания: При запуске компьютера` (Schedule: At startup).

6. Test-run it:
```cmd
schtasks /Run /TN "App-WSL2-Boot-System"
```
Then verify `systemctl is-active <app>` in WSL.

## Pitfalls

- **`Start-Process -Verb RunAs` CANNOT combine with `-RedirectStandardOutput`**
  → ParameterBindingException (AmbiguousParameterSet). Always use the `.cmd`
  wrapper writing to a file instead of redirect flags.
- **Plain `schtasks /Create ... /SC ONLOGON` from a non-admin shell** → "Отказано
  в доступе" (Access denied). ONLOGON with `-RL LIMITED` still needs elevation
  for the /RU SYSTEM style principal; ONSTART always does.
- **First `schtasks /Create` attempt via `Start-Process schtasks ... -Verb RunAs`**
  silently loses schtasks' own error output (UAC window result is swallowed).
  The cmd-wrapper-to-file pattern is the reliable way to see the error.
- `Last Result: -1` right after `/Run` = still running (wsl.exe keeps WSL alive) — expected, not an error.
- Boot task fires at boot; if WSL is also started at login by Run-key, the boot
  instance is reused (systemd already running) — no conflict.

## Step 3 — On-login fallback (no admin required)

```bash
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "App-WSL2-Boot" /t REG_SZ /d "wsl.exe -d Ubuntu-24.04 -- /bin/true" /f
```
```powershell
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\App-WSL2-Boot.lnk")
$lnk.TargetPath = "C:\Windows\System32\wsl.exe"
$lnk.Arguments = "-d Ubuntu-24.04 -- /bin/true"
$lnk.Save()
```

## WSL path mangling (Windows temp file -> WSL)

Passing `C:\Users\tomas\AppData\Local\Temp\file.go` into `wsl bash -lc "cp <path> ..."`
mangles to `C:Userstomas...` (backslashes eaten). Convert to
`/mnt/c/Users/tomas/AppData/Local/Temp/file.go` first:
```python
wsl_path = "/mnt/c/" + win_path.replace("C:\\", "").replace("\\", "/")
```
Bash heredocs also drop `\"` inside double-quoted content — for Go test files,
write via `write_file` to the Windows path (same file through bind mount)
instead of heredoc.
