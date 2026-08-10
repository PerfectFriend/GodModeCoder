#!/usr/bin/env powershell
<#
.SYNOPSIS
    Build Flutter apps (The-Isle + Royal-Isle) for Windows

.USAGE
    powershell -ExecutionPolicy Bypass -File "C:\Users\tomas\build-windows-flutter.ps1"
#>

$ErrorActionPreference = "Stop"

function Log { param([string]$msg, [string]$color="Cyan") Write-Host $msg -ForegroundColor $color }
function LogOk { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function LogWarn { param([string]$msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function LogErr { param([string]$msg) Write-Host "  [ERR] $msg" -ForegroundColor Red }

Log "=== ParanoidX Flutter Windows Build ===" -ForegroundColor Cyan
Log ""

# Check Flutter
Log "[1/5] Checking Flutter..." -ForegroundColor Yellow
$flutterVersion = flutter --version 2>&1
if ($LASTEXITCODE -ne 0) {
    LogErr "Flutter not found in PATH!"
    Log "  Install Flutter: https://docs.flutter.dev/get-started/install/windows" -ForegroundColor Yellow
    exit 1
}
LogOk "Flutter: $flutterVersion"

# Enable Windows desktop
Log "[2/5] Enabling Windows desktop support..." -ForegroundColor Yellow
flutter config --enable-windows-desktop | Out-Null
LogOk "Windows desktop enabled"

# Build function
function Build-FlutterApp {
    param([string]$ProjectPath, [string]$ProjectName)
    Log "  Building $ProjectName..." -ForegroundColor Yellow
    
    if (-not (Test-Path $ProjectPath)) {
        LogErr "Folder not found: $ProjectPath"
        return $false
    }
    
    Push-Location $ProjectPath
    
    Log "    flutter pub get..." -ForegroundColor Gray
    $result = flutter pub get 2>&1
    if ($LASTEXITCODE -ne 0) {
        LogErr "pub get failed: $result"
        Pop-Location
        return $false
    }
    
    Log "    flutter build windows --release..." -ForegroundColor Gray
    $result = flutter build windows --release 2>&1
    if ($LASTEXITCODE -ne 0) {
        LogErr "Build failed: $result"
        Pop-Location
        return $false
    }
    
    Pop-Location
    LogOk "$ProjectName built: $ProjectPath\build\windows\x64\runner\Release\"
    return $true
}

# 3. shared-libs
Log "[3/5] Checking shared-libs..." -ForegroundColor Yellow
$sharedLibsPath = "C:\Users\tomas\the-grimoire\shared-libs"
if (Test-Path "$sharedLibsPath\pubspec.yaml") {
    Build-FlutterApp -ProjectPath $sharedLibsPath -ProjectName "shared-libs"
} else {
    Log "  [SKIP] shared-libs not found or not a Flutter project" -ForegroundColor Gray
}

# 4. The-Isle
Log "[4/5] Building The-Isle (Civilian App)..." -ForegroundColor Yellow
$theIslePath = "C:\Users\tomas\The-Isle"
if (Test-Path "$theIslePath\pubspec.yaml") {
    Build-FlutterApp -ProjectPath $theIslePath -ProjectName "The-Isle"
} else {
    LogWarn "The-Isle not found in $theIslePath"
    Log "  Checking WSL2..." -ForegroundColor Yellow
    $wslPath = wsl -d Ubuntu-24.04 bash -c "ls ~/The-Isle/pubspec.yaml 2>/dev/null && echo 'found'" 2>&1
    if ($wslPath -match "found") {
        Log "  Found in WSL2, copying to Windows..." -ForegroundColor Yellow
        wsl -d Ubuntu-24.04 bash -c "cp -r ~/The-Isle /mnt/c/Users/tomas/The-Isle-WSL" 2>&1 | Out-Null
        Build-FlutterApp -ProjectPath "C:\Users\tomas\The-Isle-WSL" -ProjectName "The-Isle (from WSL)"
    }
}

# 5. Royal-Isle
Log "[5/5] Building Royal-Isle (Admin App)..." -ForegroundColor Yellow
$royalIslePath = "C:\Users\tomas\Royal-Isle"
if (Test-Path "$royalIslePath\pubspec.yaml") {
    Build-FlutterApp -ProjectPath $royalIslePath -ProjectName "Royal-Isle"
} else {
    LogWarn "Royal-Isle not found in $royalIslePath"
    Log "  Checking WSL2..." -ForegroundColor Yellow
    $wslPath = wsl -d Ubuntu-24.04 bash -c "ls ~/Royal-Isle/pubspec.yaml 2>/dev/null && echo 'found'" 2>&1
    if ($wslPath -match "found") {
        Log "  Found in WSL2, copying to Windows..." -ForegroundColor Yellow
        wsl -d Ubuntu-24.04 bash -c "cp -r ~/Royal-Isle /mnt/c/Users/tomas/Royal-Isle-WSL" 2>&1 | Out-Null
        Build-FlutterApp -ProjectPath "C:\Users\tomas\Royal-Isle-WSL" -ProjectName "Royal-Isle (from WSL)"
    }
}

Log ""
Log "=== Flutter Windows Build Complete ===" -ForegroundColor Cyan
Log ""
Log "Executables:" -ForegroundColor Cyan
Log "  The-Isle:   C:\Users\tomas\The-Isle\build\windows\x64\runner\Release\The-Isle.exe" -ForegroundColor Gray
Log "  Royal-Isle: C:\Users\tomas\Royal-Isle\build\windows\x64\runner\Release\Royal-Isle.exe" -ForegroundColor Gray
Log ""
Log "Copy .exe and data folder next to executable to run" -ForegroundColor Yellow