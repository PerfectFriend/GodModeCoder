@echo off
REM Full elevated install+config script for OpenSSH Server on Windows
REM Run as Administrator

setlocal enabledelayedexpansion

echo ============================================
echo OpenSSH Server Install & Config (Windows)
echo ============================================

echo [1/6] Installing OpenSSH Server via winget...
winget install --exact --source winget --id Microsoft.OpenSSH.Preview --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
if errorlevel 1 (
    echo ERROR: winget install failed. Try manually: winget install Microsoft.OpenSSH.Preview
    pause
    exit /b 1
)

echo [2/6] Generating host keys...
"C:\Program Files\OpenSSH\ssh-keygen.exe" -A
if errorlevel 1 (
    echo ERROR: ssh-keygen failed
    pause
    exit /b 1
)

echo [3/6] Fixing host key permissions...
icacls "C:\ProgramData\ssh\ssh_host_*" /reset
if errorlevel 1 (
    echo WARNING: icacls reset failed, trying TakeOwn...
    TakeOwn /F "C:\ProgramData\ssh\ssh_host_*" /A
    icacls "C:\ProgramData\ssh\ssh_host_*" /grant SYSTEM:F /grant Administrators:F
)

echo [4/6] Configuring sshd_config...
set "CONFIG=C:\ProgramData\ssh\sshd_config"
set "TMP=%TEMP%\sshd_config_new"

REM Backup original
copy "%CONFIG%" "%CONFIG%.bak" >nul

REM Enable PasswordAuthentication and PubkeyAuthentication
REM Comment out Match Group administrators block
(
    for /f "usebackq delims=" %%i in ("%CONFIG%") do (
        set "line=%%i"
        if "!line!"=="#PasswordAuthentication yes" (
            echo PasswordAuthentication yes
        ) else if "!line!"=="#PubkeyAuthentication yes" (
            echo PubkeyAuthentication yes
        ) else if "!line!"=="Match Group administrators" (
            echo #Match Group administrators
        ) else if "!line!"=="       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys" (
            echo #       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
        ) else (
            echo %%i
        )
    )
) > "%TMP%"

copy /Y "%TMP%" "%CONFIG%" >nul
del "%TMP%"

echo [5/6] Adding firewall rule...
netsh advfirewall firewall add rule name="OpenSSH Server" dir=in action=allow protocol=TCP localport=22

echo [6/6] Starting sshd service...
sc start sshd
timeout /t 3 >nul
sc query sshd | find "RUNNING" >nul
if errorlevel 1 (
    echo ERROR: sshd failed to start
    pause
    exit /b 1
)

echo ============================================
echo SUCCESS: OpenSSH Server installed and running
echo ============================================
echo.
echo Next steps:
echo 1. Create a local user for password auth:
echo    net user sshuser "StrongPass123!" /add
echo    net localgroup administrators sshuser /add
echo.
echo 2. Or set up key-based auth for existing user:
echo    mkdir C:\Users\^<username^>\.ssh
echo    echo "ssh-ed25519 ..." > C:\Users\^<username^>\.ssh\authorized_keys
echo.
echo 3. Test from client:
echo    ssh -o StrictHostKeyChecking=no user@localhost "echo OK"
echo.
pause