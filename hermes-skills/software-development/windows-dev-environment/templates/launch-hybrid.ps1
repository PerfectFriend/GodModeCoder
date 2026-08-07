#!/usr/bin/env powershell
<#
.SYNOPSIS
    Launch full ParanoidX stack (Hybrid WSL2 + Native Flutter)

.USAGE
    powershell -ExecutionPolicy Bypass -File "C:\Users\tomas\launch-hybrid.ps1"
#>

$ErrorActionPreference = "Stop"

function Log { param([string]$msg, [string]$color="Cyan") Write-Host $msg -ForegroundColor $color }
function LogOk { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function LogWarn { param([string]$msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function LogErr { param([string]$msg) Write-Host "  [ERR] $msg" -ForegroundColor Red }

Log "=== ParanoidX Hybrid Launch ===" -ForegroundColor Cyan
Log ""

# 1. Check WSL2 and Ubuntu
Log "[1/5] Checking WSL2..." -ForegroundColor Yellow
$wslStatus = wsl -l -v 2>&1
if ($wslStatus -match "Ubuntu-24.04") {
    LogOk "Ubuntu-24.04 found"
} else {
    LogErr "Ubuntu-24.04 not installed!"
    Log "  Run first: .\setup-paranoidx-hybrid-full.ps1" -ForegroundColor Yellow
    exit 1
}

# 2. Check Docker in WSL2
Log "[2/5] Checking Docker..." -ForegroundColor Yellow
$dockerCheck = wsl -d Ubuntu-24.04 bash -c "docker ps" 2>&1
if ($LASTEXITCODE -eq 0) {
    LogOk "Docker running"
} else {
    LogWarn "Docker not responding. Start Docker Desktop on Windows."
    Log "  Attempting to start containers..." -ForegroundColor Yellow
    wsl -d Ubuntu-24.04 bash -c "cd ~/ParanoidX/docker && docker compose up -d" 2>&1
}

# 3. Start Go server in WSL2 (background)
Log "[3/5] Starting Go server in WSL2..." -ForegroundColor Yellow
$serverCmd = "cd ~/ParanoidX && nohup ./bin/ParanoidX -data /mnt/c/ParanoidX-data -http :8080 > ~/paranoidx.log 2>&1 & echo \$!"
$serverPid = wsl -d Ubuntu-24.04 bash -c "$serverCmd" 2>&1
if ($LASTEXITCODE -eq 0 -and $serverPid -match "^\d+$") {
    LogOk "Go server started (PID: $serverPid)"
    Log "  Logs: wsl -d Ubuntu-24.04 bash -c 'tail -f ~/paranoidx.log'" -ForegroundColor Gray
} else {
    LogErr "Server start failed: $serverPid"
}

# Wait for server to start
Start-Sleep -Seconds 3

# 4. Check API server
Log "[4/5] Checking API server..." -ForegroundColor Yellow
try {
    $apiCheck = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 -ErrorAction Stop
    if ($apiCheck.StatusCode -eq 200) {
        LogOk "API responding at http://localhost:8080"
    }
} catch {
    LogWarn "API not responding yet (may still be starting)"
}

# 5. Launch Flutter apps (if built)
Log "[5/5] Checking Flutter apps..." -ForegroundColor Yellow

$theIsleExe = "C:\Users\tomas\The-Isle\build\windows\x64\runner\Release\The-Isle.exe"
$royalIsleExe = "C:\Users\tomas\Royal-Isle\build\windows\x64\runner\Release\Royal-Isle.exe"

if (Test-Path $theIsleExe) {
    Log "  The-Isle found. Launching..." -ForegroundColor Yellow
    Start-Process $theIsleExe -WorkingDirectory (Split-Path $theIsleExe)
    LogOk "The-Isle launched"
} else {
    LogWarn "The-Isle not built. Run: .\build-windows-flutter.ps1"
}

if (Test-Path $royalIsleExe) {
    Log "  Royal-Isle found. Launching..." -ForegroundColor Yellow
    Start-Process $royalIsleExe -WorkingDirectory (Split-Path $royalIsleExe)
    LogOk "Royal-Isle launched"
} else {
    LogWarn "Royal-Isle not built. Run: .\build-windows-flutter.ps1"
}

Log ""
Log "=== ParanoidX Hybrid Stack Running ===" -ForegroundColor Cyan
Log ""
Log "Services:" -ForegroundColor Cyan
Log "  Go API:      http://localhost:8080" -ForegroundColor Gray
Log "  The-Isle:    Native Windows app" -ForegroundColor Gray
Log "  Royal-Isle:  Native Windows app" -ForegroundColor Gray
Log ""
Log "Management:" -ForegroundColor Cyan
Log "  Server logs:  wsl -d Ubuntu-24.04 bash -c 'tail -f ~/paranoidx.log'" -ForegroundColor Gray
Log "  Stop server:  wsl -d Ubuntu-24.04 bash -c 'pkill ParanoidX'" -ForegroundColor Gray
Log "  Docker logs:  wsl -d Ubuntu-24.04 bash -c 'cd ~/ParanoidX/docker && docker compose logs -f'" -ForegroundColor Gray
Log ""
Log "Shared data:" -ForegroundColor Cyan
Log "  Windows: C:\ParanoidX-data" -ForegroundColor Gray
Log "  WSL2:    /mnt/c/ParanoidX-data" -ForegroundColor Gray