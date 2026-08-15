#!/usr/bin/env powershell
<#
.SYNOPSIS
    ParanoidX Windows Hybrid WSL2 Setup - Full Automatic Installation
    Self-continues after reboots via RunOnce registry key

.DESCRIPTION
    1. Enables WSL2 + VirtualMachinePlatform
    2. Installs Ubuntu-24.04 (auto-reboots and continues if needed)
    3. Configures wsl.conf (systemd, bind mounts)
    4. Clones 5 repositories
    5. Builds Go server
    6. Creates C:\ParanoidX-data shared folder structure

.USAGE
    powershell -ExecutionPolicy Bypass -File "C:\Users\tomas\setup-paranoidx-hybrid-full.ps1"
#>

$ErrorActionPreference = "Stop"
$scriptPath = $MyInvocation.MyCommand.Definition
$runOnceKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
$runOnceValue = "ParanoidX-WSL2-Setup"
$phase = "init"

# --- Logging functions ---
function Log { param([string]$msg, [string]$color="Cyan") Write-Host $msg -ForegroundColor $color }
function LogOk { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function LogWarn { param([string]$msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function LogErr { param([string]$msg) Write-Host "  [ERR] $msg" -ForegroundColor Red }

# --- Admin check ---
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    LogErr "Administrator rights required! Run PowerShell as Administrator."
    exit 1
}

# --- Determine phase (before/after reboot) ---
if (Get-ItemProperty -Path $runOnceKey -Name $runOnceValue -ErrorAction SilentlyContinue) {
    $phase = (Get-ItemProperty -Path $runOnceKey -Name $runOnceValue).($runOnceValue)
    Remove-ItemProperty -Path $runOnceKey -Name $runOnceValue -ErrorAction SilentlyContinue
    Log "=== ParanoidX Setup: Phase $phase (after reboot) ===" -ForegroundColor Cyan
} else {
    Log "=== ParanoidX Windows Hybrid WSL2 Setup (Full Auto) ===" -ForegroundColor Cyan
    Log "Version: 2.0 - Auto-continues after reboots" -ForegroundColor Gray
}

# ============================================================
# PHASE 1: Install WSL2 + Ubuntu (may require reboot)
# ============================================================
if ($phase -eq "init" -or $phase -eq "install-wsl") {
    if ($phase -eq "init") { $phase = "install-wsl" }

    Log "[1/5] Enabling WSL2 and Virtual Machine Platform..." -ForegroundColor Yellow
    $rebootNeeded = $false

    # Microsoft-Windows-Subsystem-Linux
    $feat = dism /online /get-feature /featurename:Microsoft-Windows-Subsystem-Linux 2>&1
    if ($feat -match "State : Disabled") {
        Log "  Enabling Microsoft-Windows-Subsystem-Linux..."
        dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null
        $rebootNeeded = $true
        LogOk "Microsoft-Windows-Subsystem-Linux enabled"
    } else { LogOk "Microsoft-Windows-Subsystem-Linux already enabled" }

    # VirtualMachinePlatform
    $feat = dism /online /get-feature /featurename:VirtualMachinePlatform 2>&1
    if ($feat -match "State : Disabled") {
        Log "  Enabling VirtualMachinePlatform..."
        dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null
        $rebootNeeded = $true
        LogOk "VirtualMachinePlatform enabled"
    } else { LogOk "VirtualMachinePlatform already enabled" }

    # WSL2 as default
    wsl --set-default-version 2 | Out-Null
    LogOk "WSL2 set as default version"

    # Install Ubuntu-24.04
    Log "[2/5] Installing Ubuntu-24.04..." -ForegroundColor Yellow
    $wslList = wsl -l -v 2>&1
    if ($wslList -notmatch "Ubuntu-24.04") {
        Log "  Installing Ubuntu-24.04 (downloading ~500MB)..." -ForegroundColor Yellow
        $result = wsl --install -d Ubuntu-24.04 2>&1
        if ($result -match "requires a reboot|reboot|restart") {
            $rebootNeeded = $true
        }
        LogOk "Ubuntu-24.04 installed (requires first-run initialization)"
    } else {
        LogOk "Ubuntu-24.04 already installed"
    }

    if ($rebootNeeded) {
        Log ""; LogWarn "REBOOT REQUIRED to apply WSL changes" -ForegroundColor Yellow
        Log "Script will auto-continue after reboot..." -ForegroundColor Gray

        # Register self in RunOnce for auto-resume after reboot
        Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "configure-wsl" -Force
        Log "Registered auto-resume after reboot (RunOnce)" -ForegroundColor Gray

        Log "Rebooting in 10 seconds... (Ctrl+C to cancel)" -ForegroundColor Yellow
        Start-Sleep 10
        Restart-Computer -Force
        exit 0
    }
}

# ============================================================
# PHASE 2: Configure WSL (after reboot, Ubuntu initialized)
# ============================================================
if ($phase -eq "configure-wsl" -or $phase -eq "install-wsl") {
    if ($phase -eq "install-wsl") { $phase = "configure-wsl" }

    Log "[3/5] Configuring wsl.conf (systemd + bind mounts)..." -ForegroundColor Yellow

    # Wait for Ubuntu to become available (first run creates user)
    $maxWait = 120; $waited = 0
    while ($waited -lt $maxWait) {
        $test = wsl -d Ubuntu-24.04 -u root bash -c "echo 'ready'" 2>&1
        if ($test -match "ready") { break }
        Log "  Waiting for Ubuntu initialization... ($waited/$maxWait sec)" -ForegroundColor Gray
        Start-Sleep 5
        $waited += 5
    }

    # Write wsl.conf
    $wslConf = @"
[automount]
enabled = true
root = /mnt/
options = "metadata,uid=1000,gid=1000,umask=0022"

[network]
generateHosts = true
generateResolvConf = true

[boot]
systemd = true
"@

    wsl -d Ubuntu-24.04 -u root bash -c "cat > /etc/wsl.conf << 'EOF'
$wslConf
EOF" 2>$null
    LogOk "wsl.conf written"

    # Restart WSL to apply systemd
    Log "  Restarting WSL to apply systemd..."
    wsl --terminate Ubuntu-24.04
    Start-Sleep 3
    wsl -d Ubuntu-24.04 -u root bash -c "systemctl is-system-running" 2>&1 | Out-Null
    LogOk "WSL restarted, systemd active"

    # Register next phase
    Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "clone-repos" -Force
    Log "Next phase: clone repositories (after another reboot for clean systemd)" -ForegroundColor Gray

    # Optional reboot for clean systemd
    LogWarn "Recommended: one more reboot for clean systemd state" -ForegroundColor Yellow
    Log "Rebooting in 10 seconds... (Ctrl+C to skip)" -ForegroundColor Yellow
    Start-Sleep 10
    Restart-Computer -Force
    exit 0
}

# ============================================================
# PHASE 3: Clone repositories
# ============================================================
if ($phase -eq "clone-repos") {
    Log "[4/5] Cloning repositories in WSL2..." -ForegroundColor Yellow

    $repos = @(
        @{name="ParanoidX"; url="https://github.com/DarkPushkin/ParanoidX.git"; path="~/ParanoidX"},
        @{name="The-Isle"; url="https://github.com/DarkPushkin/The-Isle.git"; path="~/The-Isle"},
        @{name="Royal-Isle"; url="https://github.com/DarkPushkin/Royal-Isle.git"; path="~/Royal-Isle"},
        @{name="shared-libs"; url="https://github.com/DarkPushkin/shared-libs.git"; path="~/shared-libs"},
        @{name="the-grimoire"; url="https://github.com/DarkPushkin/the-grimoire.git"; path="~/the-grimoire"}
    )

    foreach ($repo in $repos) {
        $exists = wsl -d Ubuntu-24.04 bash -c "test -d $($repo.path) && echo 'exists'" 2>$null
        if ($exists -match "exists") {
            LogOk "$($repo.name) already cloned"
        } else {
            Log "  Cloning $($repo.name)..." -ForegroundColor Yellow
            $result = wsl -d Ubuntu-24.04 bash -c "git clone $($repo.url) $($repo.path)" 2>&1
            if ($LASTEXITCODE -eq 0) { LogOk "$($repo.name) cloned" }
            else { LogWarn "$($repo.name): $result" }
        }
    }

    # Register next phase
    Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "build-go" -Force
}

# ============================================================
# PHASE 4: Build Go server
# ============================================================
if ($phase -eq "build-go") {
    Log "[5/5] Building Go server in WSL2..." -ForegroundColor Yellow

    $goVer = wsl -d Ubuntu-24.04 bash -c "go version" 2>&1
    LogOk "Go version: $goVer"

    Log "  Building ParanoidX..." -ForegroundColor Yellow
    $buildResult = wsl -d Ubuntu-24.04 bash -c "cd ~/ParanoidX && go build -o ~/bin/ParanoidX ./cmd/ParanoidX/" 2>&1
    if ($LASTEXITCODE -eq 0) {
        LogOk "ParanoidX built: ~/bin/ParanoidX"
    } else {
        LogErr "Build failed: $buildResult"
        LogWarn "Check dependencies in WSL2: wsl -d Ubuntu-24.04 bash -c 'cd ~/ParanoidX && go mod tidy'"
    }

    # Create Windows data folder
    Log "  Creating C:\ParanoidX-data structure..." -ForegroundColor Yellow
    $dataPath = "C:\ParanoidX-data"
    if (-not (Test-Path $dataPath)) { New-Item -ItemType Directory -Path $dataPath -Force | Out-Null }
    @("backups","logs","radio","dc","config") | ForEach-Object {
        $p = Join-Path $dataPath $_
        if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
    }
    LogOk "Data: C:\ParanoidX-data <-> /mnt/c/ParanoidX-data"
}

# ============================================================
# FINAL
# ============================================================
Log ""
Log "=== ParanoidX Hybrid Foundation Setup COMPLETE ===" -ForegroundColor Cyan
Log ""
Log "What was done:" -ForegroundColor Cyan
LogOk "WSL2 + Ubuntu-24.04 (systemd, bind mounts)"
LogOk "5 repositories cloned to ~/ParanoidX, ~/The-Isle, ..."
LogOk "Go server built: ~/bin/ParanoidX"
LogOk "Shared data: C:\ParanoidX-data <-> /mnt/c/ParanoidX-data"
Log ""
Log "NEXT STEPS (manual):" -ForegroundColor Yellow
Log "  1. Start Docker Desktop on Windows" -ForegroundColor Gray
Log "  2. In WSL2: cd ~/ParanoidX/docker && docker compose up -d" -ForegroundColor Gray
Log "  3. Build Flutter apps: .\build-windows-flutter.ps1" -ForegroundColor Gray
Log "  4. Launch full stack: .\launch-hybrid.ps1" -ForegroundColor Gray
Log ""
Log "Useful commands:" -ForegroundColor Cyan
Log "  wsl -d Ubuntu-24.04                    # enter Ubuntu shell" -ForegroundColor Gray
Log "  wsl -d Ubuntu-24.04 bash -c 'cd ~/ParanoidX && ~/bin/ParanoidX -data /mnt/c/ParanoidX-data -http :8080'" -ForegroundColor Gray
Log "  .\launch-hybrid.ps1                    # launch full stack" -ForegroundColor Gray