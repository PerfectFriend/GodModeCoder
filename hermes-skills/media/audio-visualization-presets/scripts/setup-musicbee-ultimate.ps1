<# 
.SYNOPSIS
MusicBee Ultimate Setup — clones MilkDrop presets, configures MusicBee, creates shortcut

.DESCRIPTION
Run AFTER manually extracting MusicBee Portable to ~/MusicBeeUltimate/MusicBee/
This script handles everything else: preset cloning, config, VST folder, shortcut.

.PREREQUISITES
1. MusicBee Portable extracted to C:\Users\<user>\MusicBeeUltimate\MusicBee\ (MusicBee.exe directly there)
2. Git in PATH
3. PowerShell execution policy allows scripts (RemoteSigned or Bypass)

.USAGE
powershell -ExecutionPolicy Bypass -File .\setup-musicbee-ultimate.ps1
#>

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = 'Stop'

# === PATHS ===
$BaseDir     = "$env:USERPROFILE\MusicBeeUltimate"
$MusicBeeDir = "$BaseDir\MusicBee"
$PresetsDir  = "$BaseDir\MilkDropPresets"
$TexturesDir = "$BaseDir\MilkDropTextures"
$VSTDir      = "$MusicBeeDir\Plugins\VST"

Write-Host "`n============================" -ForegroundColor Cyan
Write-Host "  MusicBee Presets & Config" -ForegroundColor Cyan
Write-Host "============================`n" -ForegroundColor Cyan

# Verify MusicBee exists
$exe = Get-ChildItem $MusicBeeDir -Filter "MusicBee.exe" -ErrorAction SilentlyContinue
if (-not $exe) {
    Write-Error "MusicBee.exe not found in $MusicBeeDir"
    Write-Host "Extract MusicBee Portable ZIP there first." -ForegroundColor Yellow
    exit 1
}
Write-Host "OK: $($exe.FullName)" -ForegroundColor Green

# === 1. CLONE PRESETS ===
Write-Host "`n[1/4] Cloning MilkDrop presets..." -ForegroundColor Yellow
$repos = @(
    @{ Url="https://github.com/projectM-visualizer/presets-cream-of-the-crop.git"; Dest="$PresetsDir\CreamOfTheCrop" },
    @{ Url="https://github.com/projectM-visualizer/presets-milkdrop-original.git"; Dest="$PresetsDir\Original" },
    @{ Url="https://github.com/projectM-visualizer/presets-milkdrop-texture-pack.git"; Dest="$TexturesDir" }
)

$gitOk = $true
foreach ($repo in $repos) {
    Write-Host "  Cloning $($repo.Url)..." -ForegroundColor Gray
    # Remove existing directory first for idempotency
    if (Test-Path $repo.Dest) { Remove-Item $repo.Dest -Recurse -Force -ErrorAction SilentlyContinue }
    $result = git clone --depth 1 $repo.Url $repo.Dest *>&1
    if ($LASTEXITCODE -ne 0) { 
        Write-Warning "  Failed (git not in PATH or network issue)"
        $gitOk = $false 
    } else {
        Write-Host "  Done" -ForegroundColor Green
    }
}

if (-not $gitOk) {
    Write-Host "`n  Git unavailable. Opening repos in browser..." -ForegroundColor Yellow
    foreach ($repo in $repos) { try { Start-Process $repo.Url } catch { } }
    Write-Host "  Download each as ZIP, extract to:" -ForegroundColor White
    Write-Host "    $PresetsDir\CreamOfTheCrop" -ForegroundColor Gray
    Write-Host "    $PresetsDir\Original" -ForegroundColor Gray
    Write-Host "    $TexturesDir" -ForegroundColor Gray
    Read-Host "  Press ENTER when done"
}

# Merge all .milk into single folder
$AllPresets = "$PresetsDir\All"
New-Item -ItemType Directory -Force -Path $AllPresets | Out-Null
Get-ChildItem "$PresetsDir\CreamOfTheCrop" -Recurse -Filter "*.milk" -EA SilentlyContinue | Copy-Item -Destination $AllPresets -Force -EA SilentlyContinue
Get-ChildItem "$PresetsDir\Original\Milkdrop-Original" -Recurse -Filter "*.milk" -EA SilentlyContinue | Copy-Item -Destination $AllPresets -Force -EA SilentlyContinue
$count = (Get-ChildItem $AllPresets -Filter "*.milk" -EA SilentlyContinue).Count
Write-Host "  Merged $count presets" -ForegroundColor Green

# === 2. CONFIG ===
Write-Host "`n[2/4] Writing MusicBee config..." -ForegroundColor Yellow
$SettingsDir = "$env:APPDATA\MusicBee"
New-Item -ItemType Directory -Force -Path $SettingsDir | Out-Null

$ini = @"
[MusicBee3Settings]
Visualisation_MilkDrop_PresetFolder=$AllPresets
Visualisation_MilkDrop_TextureFolder=$TexturesDir
Visualisation_MilkDrop_AutoChangePresets=True
Visualisation_MilkDrop_AutoChangeInterval=30
Visualisation_MilkDrop_TransitionDuration=5
Visualisation_MilkDrop_ShowFPS=False
Visualisation_MilkDrop_ShowPresetName=True
Library_AutoScanFolders=$env:USERPROFILE\Music
Library_MonitorFolders=$env:USERPROFILE\Music
Player_DSP_EnableEqualizer=True
Interface_Language=ru-RU
Startup_ShowSplashScreen=False
"@
$ini | Out-File -Encoding UTF8 "$SettingsDir\MusicBee3Settings.ini"
Write-Host "  Done: $SettingsDir\MusicBee3Settings.ini" -ForegroundColor Green

# === 3. VST FOLDER ===
Write-Host "`n[3/4] Creating VST folder..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $VSTDir | Out-Null

# === 4. SHORTCUT ===
Write-Host "`n[4/4] Creating desktop shortcut..." -ForegroundColor Yellow
$shortcutPath = "$env:USERPROFILE\Desktop\MusicBee Ultimate.lnk"
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($shortcutPath)
$sc.TargetPath = "$MusicBeeDir\MusicBee.exe"
$sc.WorkingDirectory = $MusicBeeDir
$sc.IconLocation = "$MusicBeeDir\MusicBee.exe,0"
$sc.Description = "MusicBee Ultimate - 10000+ MilkDrop presets"
$sc.Save()
Write-Host "  Shortcut: $shortcutPath" -ForegroundColor Green

# === DONE ===
Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  READY! Launch from Desktop shortcut." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host @"
MusicBee folder:  $MusicBeeDir
Presets (All):    $AllPresets  ($count files)
Textures:         $TexturesDir
Settings:         $SettingsDir
VST plugins:      $VSTDir

Hotkeys in MilkDrop:
  Ctrl+M          = Toggle visualisation
  Ctrl+Shift+M    = MilkDrop settings
  Tab / Shift+Tab = Next / Prev preset
  L               = Lock current preset
  R               = Random preset
  F1              = Help
"@

Start-Process "$MusicBeeDir\MusicBee.exe"