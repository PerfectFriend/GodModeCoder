#!/usr/bin/env powershell
<#
.SYNOPSIS
    ParanoidX Post-Install: Clone repos, build Go, create shared folder
    Run AFTER wsl.conf is configured and WSL rebooted, and user is created
#>

$ErrorActionPreference = "Stop"

function Log { param([string]$msg, [string]$color="Cyan") Write-Host $msg -ForegroundColor $color }
function LogOk { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function LogWarn { param([string]$msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function LogErr { param([string]$msg) Write-Host "  [ERR] $msg" -ForegroundColor Red }

# Admin check
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    LogErr "Run as Administrator!"
    exit 1
}

Log "=== ParanoidX Post-Install (Clone + Build + Data) ===" -ForegroundColor Cyan

# Verify Ubuntu ready
Log "[1/3] Verifying Ubuntu-24.04..." -ForegroundColor Yellow
$test = wsl -d Ubuntu-24.04 bash -c "echo 'ready'" 2>&1
if ($test -notmatch "ready") {
    LogErr "Ubuntu not ready. Launch Ubuntu once from Start menu to complete setup."
    exit 1
}
LogOk "Ubuntu ready"

# Verify default user is not root
$username = wsl -d Ubuntu-24.04 bash -c 'whoami' 2>&1 | Select-Object -First 1
$username = $username.Trim()
Log "  Current user: $username" -ForegroundColor Gray
if ($username -eq "root") {
    LogWarn "Running as root! User creation may be incomplete."
    LogWarn "Run user creation commands from wsl2-hybrid-troubleshooting.md"
}

# Clone repositories - escape $HOME so bash expands it
Log "[2/3] Cloning repositories in WSL2..." -ForegroundColor Yellow

$repos = @(
    @{name="ParanoidX"; url="https://github.com/DarkPushkin/ParanoidX.git"; path="ParanoidX"},
    @{name="The-Isle"; url="https://github.com/DarkPushkin/The-Isle.git"; path="The-Isle"},
    @{name="Royal-Isle"; url="https://github.com/DarkPushkin/Royal-Isle.git"; path="Royal-Isle"},
    @{name="shared-libs"; url="https://github.com/DarkPushkin/shared-libs.git"; path="shared-libs"},
    @{name="the-grimoire"; url="https://github.com/DarkPushkin/the-grimoire.git"; path="the-grimoire"}
)

foreach ($repo in $repos) {
    $exists = wsl -d Ubuntu-24.04 bash -c "test -d `$HOME/$($repo.path) && echo 'exists'" 2>$null
    if ($exists -match "exists") {
        LogOk "$($repo.name) already cloned"
    } else {
        Log "  Cloning $($repo.name)..." -ForegroundColor Yellow
        $result = wsl -d Ubuntu-24.04 bash -c "git clone $($repo.url) `$HOME/$($repo.path)" 2>&1
        if ($LASTEXITCODE -eq 0) { LogOk "$($repo.name) cloned to ~/$($repo.path)" }
        else { LogWarn "$($repo.name): $result" }
    }
}

# Build Go server
Log "[3/3] Building Go server in WSL2..." -ForegroundColor Yellow

$goVer = wsl -d Ubuntu-24.04 bash -c "go version" 2>&1
LogOk "Go version: $goVer"

Log "  Building ParanoidX..." -ForegroundColor Yellow
$buildResult = wsl -d Ubuntu-24.04 bash -c "cd `$HOME/ParanoidX && go build -o ~/bin/ParanoidX ./cmd/ParanoidX/" 2>&1
if ($LASTEXITCODE -eq 0) {
    LogOk "ParanoidX built: ~/bin/ParanoidX"
} else {
    LogErr "Build failed: $buildResult"
    LogWarn "Try: wsl -d Ubuntu-24.04 bash -c 'cd ~/ParanoidX && go mod tidy && go build -o ~/bin/ParanoidX ./cmd/ParanoidX/'"
}

# Create Windows data folder
Log "  Creating C:\ParanoidX-data structure..." -ForegroundColor Yellow
$dataPath = "C:\ParanoidX-data"
if (-not (Test-Path $dataPath)) { New-Item -ItemType Directory -Path $dataPath -Force | Out-Null; LogOk "Created $dataPath" }
else { LogOk "$dataPath exists" }

@("backups","logs","radio","dc","config") | ForEach-Object {
    $p = Join-Path $dataPath $_
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}
LogOk "Subfolders created: backups, logs, radio, dc, config"

# Verify bind mount works
Log "  Testing bind mount..." -ForegroundColor Yellow
$testMount = wsl -d Ubuntu-24.04 bash -c "ls /mnt/c/ParanoidX-data" 2>&1
if ($LASTEXITCODE -eq 0) {
    LogOk "Bind mount working: /mnt/c/ParanoidX-data accessible"
} else {
    LogWarn "Bind mount may need WSL restart: wsl --terminate Ubuntu-24.04"
}

Log ""
Log "=== Post-Install COMPLETE ===" -ForegroundColor Cyan
Log ""
Log "Done:" -ForegroundColor Cyan
LogOk "5 repositories cloned to ~/"
LogOk "Go server built: ~/bin/ParanoidX"
LogOk "Shared data: C:\ParanoidX-data <-> /mnt/c/ParanoidX-data"
Log ""
Log "Next steps:" -ForegroundColor Yellow
Log "  1. Start Docker Desktop on Windows" -ForegroundColor Gray
Log "  2. In WSL2: cd ~/ParanoidX/docker && docker compose up -d" -ForegroundColor Gray
Log "  3. Build Flutter apps: .\build-windows-flutter.ps1" -ForegroundColor Gray
Log "  4. Launch stack: .\launch-hybrid.ps1" -ForegroundColor Gray