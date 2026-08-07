@echo off
REM Elevated batch to write administrators_authorized_keys correctly
REM Usage: Run as Administrator
REM   fix_administrators_keys.bat "ssh-ed25519 AAAAC3... user@host"

setlocal
if "%~1"=="" (
    echo Usage: %~nx0 "ssh-ed25519 AAAAC3... user@host"
    exit /b 1
)

set "KEY=%~1"
echo %KEY% > C:\ProgramData\ssh\administrators_authorized_keys

REM Verify
echo Written:
type C:\ProgramData\ssh\administrators_authorized_keys