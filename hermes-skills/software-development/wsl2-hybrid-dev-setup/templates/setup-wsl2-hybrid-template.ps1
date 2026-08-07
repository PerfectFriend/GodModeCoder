#!/usr/bin/env powershell
<#
.SYNOPSIS
    Template: Hybrid WSL2 + Windows Setup Script
    Customize PROJECT_NAME, REPOS, BUILD_CMD for your project
#>

$ErrorActionPreference = "Stop"

# ========== CONFIGURATION ==========
$PROJECT_NAME = "MyProject"
$UBUNTU_VERSION = "Ubuntu-24.04"
$REPOS = @(
    @{name="Backend"; url="https://github.com/user/backend.git"; path="backend"},
    @{name="Frontend"; url="https://github.com/user/frontend.git"; path="frontend"},
    @{name="Shared"; url="https://github.com/user/shared.git"; path="shared"}
)
$BUILD_CMD = "cd \$HOME/backend && go build -o ~/bin/$PROJECT_NAME ./cmd/main/"
$DATA_SUBDIRS = @("logs", "data", "config", "backups")
# ===================================

$runOnceKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
$runOnceValue = "$PROJECT_NAME-WSL2-Setup"
$phase = "init"

function Log { param([string]$msg, [string]$color="Cyan") Write-Host $msg -ForegroundColor $color }
function LogOk { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function LogWarn { param([string]$msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function LogErr { param([string]$msg) Write-Host "  [ERR] $msg" -ForegroundColor Red }

# Admin check
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    LogErr "Run as Administrator!"
    exit 1
}

# Determine phase
if (Get-ItemProperty -Path $runOnceKey -Name $runOnceValue -ErrorAction SilentlyContinue) {
    $phase = (Get-ItemProperty -Path $runOnceKey -Name $runOnceValue).($runOnceValue)
    Remove-ItemProperty -Path $runOnceKey -Name $runOnceValue -ErrorAction SilentlyContinue
    Log "=== $PROJECT_NAME Setup: Phase $phase ===" -ForegroundColor Cyan
} else {
    Log "=== $PROJECT_NAME Hybrid WSL2 Setup ===" -ForegroundColor Cyan
}

# ---- PHASE: install-wsl ----
if ($phase -eq "init" -or $phase -eq "install-wsl") {
    if ($phase -eq "init") { $phase = "install-wsl" }
    Log "[1/4] Enabling WSL2..." -ForegroundColor Yellow
    
    $reboot = $false
    foreach ($feat in @("Microsoft-Windows-Subsystem-Linux", "VirtualMachinePlatform")) {
        $state = dism /online /get-feature /featurename:$feat 2>&1
        if ($state -match "State : Disabled") {
            dism /online /enable-feature /featurename:$feat /all /norestart | Out-Null
            $reboot = $true
            LogOk "$feat enabled"
        } else { LogOk "$feat already enabled" }
    }
    wsl --set-default-version 2 | Out-Null
    
    $wslList = wsl -l -v 2>&1
    if ($wslList -notmatch $UBUNTU_VERSION) {
        Log "Installing $UBUNTU_VERSION..." -ForegroundColor Yellow
        $result = wsl --install -d $UBUNTU_VERSION 2>&1
        if ($result -match "reboot|restart") { $reboot = $true }
        LogOk "$UBUNTU_VERSION installed"
    } else { LogOk "$UBUNTU_VERSION already installed" }
    
    if ($reboot) {
        LogWarn "REBOOT REQUIRED"; Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "configure-wsl" -Force
        Log "Rebooting in 10s..."; Start-Sleep 10; Restart-Computer -Force; exit 0
    }
}

# ---- PHASE: configure-wsl ----
if ($phase -eq "configure-wsl" -or $phase -eq "install-wsl") {
    if ($phase -eq "install-wsl") { $phase = "configure-wsl" }
    Log "[2/4] Configuring $UBUNTU_VERSION..." -ForegroundColor Yellow
    
    # Wait for Ubuntu ready
    $waited = 0
    while ($waited -lt 120) {
        $test = wsl -d $UBUNTU_VERSION -u root bash -c "echo 'ready'" 2>&1
        if ($test -match "ready") { break }
        Log "Waiting for Ubuntu... ($waited/120s)"; Start-Sleep 5; $waited += 5
    }
    
    # Create user if needed
    $username = "devuser"
    $userExists = wsl -d $UBUNTU_VERSION -u root bash -c "id -u $username 2>/dev/null && echo 'exists'" 2>&1
    if ($userExists -notmatch "exists") {
        wsl -d $UBUNTU_VERSION -u root bash -c "useradd -m -s /bin/bash -G sudo $username && echo '$username:$username' | chpasswd && echo '$username ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/$username && chmod 440 /etc/sudoers.d/$username"
        LogOk "User $username created"
    }
    
    # Write wsl.conf
    $wslConf = @"
[user]
default=$username

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
    wsl -d $UBUNTU_VERSION -u root bash -c "cat > /etc/wsl.conf << 'EOF'
$wslConf
EOF"
    LogOk "wsl.conf written"
    
    wsl --terminate $UBUNTU_VERSION; Start-Sleep 3
    Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "clone-repos" -Force
    LogWarn "Reboot for clean systemd"; Start-Sleep 10; Restart-Computer -Force; exit 0
}

# ---- PHASE: clone-repos ----
if ($phase -eq "clone-repos") {
    Log "[3/4] Cloning repositories..." -ForegroundColor Yellow
    foreach ($repo in $REPOS) {
        $exists = wsl -d $UBUNTU_VERSION bash -c "test -d /home/$username/$($repo.path) && echo 'exists'" 2>$null
        if ($exists -match "exists") { LogOk "$($repo.name) already cloned" }
        else {
            Log "Cloning $($repo.name)..." -ForegroundColor Yellow
            $result = wsl -d $UBUNTU_VERSION bash -c "git clone $($repo.url) /home/$username/$($repo.path)" 2>&1
            if ($LASTEXITCODE -eq 0) { LogOk "$($repo.name) cloned" }
            else { LogWarn "$($repo.name): $result" }
        }
    }
    Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "build-go" -Force
}

# ---- PHASE: build-go ----
if ($phase -eq "build-go") {
    Log "[4/4] Building project..." -ForegroundColor Yellow
    
    # Install Go if needed
    $goVer = wsl -d $UBUNTU_VERSION bash -c "go version 2>&1"
    if ($goVer -notmatch "go version") {
        Log "Installing Go..." -ForegroundColor Yellow
        wsl -d $UBUNTU_VERSION bash -c "sudo apt update && sudo apt install -y golang-go" 2>&1 | Out-Null
        LogOk "Go installed"
    }
    LogOk "Go: $goVer"
    
    # Build
    Log "Building $PROJECT_NAME..." -ForegroundColor Yellow
    $result = wsl -d $UBUNTU_VERSION bash -c $BUILD_CMD 2>&1
    if ($LASTEXITCODE -eq 0) { LogOk "$PROJECT_NAME built" }
    else { LogErr "Build failed: $result"; exit 1 }
    
    # Shared data folder
    $dataPath = "C:\$PROJECT_NAME-data"
    if (-not (Test-Path $dataPath)) { New-Item -ItemType Directory -Path $dataPath -Force | Out-Null }
    foreach ($sub in $DATA_SUBDIRS) { $p = Join-Path $dataPath $sub; if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null } }
    LogOk "Shared data: $dataPath <-> /mnt/c/$PROJECT_NAME-data"
    
    # Verify bind mount
    $mount = wsl -d $UBUNTU_VERSION bash -c "ls /mnt/c/$PROJECT_NAME-data" 2>&1
    if ($LASTEXITCODE -eq 0) { LogOk "Bind mount verified" }
    else { LogWarn "Bind mount may need: wsl --terminate $UBUNTU_VERSION" }
}

Log ""
Log "=== $PROJECT_NAME Setup COMPLETE ===" -ForegroundColor Green