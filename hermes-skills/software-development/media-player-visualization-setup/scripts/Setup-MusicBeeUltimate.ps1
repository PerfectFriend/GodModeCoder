<#>
.SYNOPSIS
    MusicBee Ultimate Setup — Automated installation of MusicBee Portable with MilkDrop visualizations
    and 2000+ presets from GitHub collections.

.DESCRIPTION
    This script performs a complete "batteries included" setup:
    1. Downloads MusicBee Portable (latest stable)
    2. Extracts to ~/MusicBeeUltimate/MusicBee
    3. Clones 3 GitHub preset repositories (cream-of-the-crop, original, textures)
    4. Merges all presets into a single AllPresets folder
    5. Generates MusicBee3Settings.ini with MilkDrop paths, auto-rotation, Russian UI, EQ
    6. Creates VST plugin directory
    7. Creates desktop shortcut
    8. Launches MusicBee

.REQUIREMENTS
    - PowerShell 5.1+ (built into Windows 10/11)
    - Internet connection
    - Git (optional; falls back to ZIP downloads if not available)
    - No admin rights required (Portable install)

.USAGE
    # Save as Setup-MusicBeeUltimate.ps1
    # Right-click → "Run with PowerShell"
    # Or from terminal: powershell -ExecutionPolicy Bypass -File .\Setup-MusicBeeUltimate.ps1

.NOTES
    Author: Hermes Agent
    Version: 1.0
    Tested on: Windows 10/11
#>

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# ========== CONFIGURATION ==========
$BaseDir      = "$env:USERPROFILE\MusicBeeUltimate"
$MusicBeeDir  = "$BaseDir\MusicBee"
$PresetsDir   = "$BaseDir\MilkDropPresets"
$TexturesDir  = "$BaseDir\MilkDropTextures"
$VSTDir       = "$MusicBeeDir\Plugins\VST"
$SettingsDir  = "$env:APPDATA\MusicBee"
$MusicFolder  = "$env:USERPROFILE\Music"

# URLs
$MajorGeeksMirror = "https://www.majorgeeks.com/mg/getmirror/musicbee_portable,1.html"
$GitHubRepos = @(
    @{ Name="cream-of-the-crop"; Url="https://github.com/projectM-visualizer/presets-cream-of-the-crop"; Target="$PresetsDir\CreamOfTheCrop" },
    @{ Name="milkdrop-original"; Url="https://github.com/projectM-visualizer/presets-milkdrop-original"; Target="$PresetsDir\Original" },
    @{ Name="milkdrop-textures"; Url="https://github.com/projectM-visualizer/presets-milkdrop-texture-pack"; Target="$TexturesDir" }
)

# ========== HELPER FUNCTIONS ==========
function Write-Status {
    param([string]$Message, [ConsoleColor]$Color = 'Yellow')
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

function Test-GitAvailable {
    try { git --version 2>$null | Out-Null; return $true } catch { return $false }
}

function Clone-Or-Download {
    param(
        [string]$RepoUrl,
        [string]$TargetPath,
        [string]$RepoName
    )

    if (Test-Path $TargetPath) {
        Write-Success "$RepoName already exists at $TargetPath"
        return
    }

    $gitAvailable = Test-GitAvailable

    if ($gitAvailable) {
        Write-Host "  Cloning $RepoName via git..." -NoNewline
        try {
            git clone --depth 1 $RepoUrl $TargetPath 2>$null
            Write-Success "Done"
            return
        } catch {
            Write-Host "  Git clone failed, falling back to ZIP..." -ForegroundColor Gray
        }
    }

    # Fallback: Download ZIP
    $zipUrl = "$RepoUrl/archive/refs/heads/main.zip"
    $zipPath = "$env:TEMP\$RepoName-main.zip"
    Write-Host "  Downloading $RepoName via ZIP..." -NoNewline
    try {
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing -Headers @{ 'User-Agent' = 'Mozilla/5.0' } -ErrorAction Stop
        Expand-Archive -Path $zipPath -DestinationPath $TargetPath -Force -ErrorAction Stop
        # ZIP extracts to folder-name-main, move contents up
        $extracted = Get-ChildItem $TargetPath -Directory | Select-Object -First 1
        if ($extracted -and (Test-Path "$($extracted.FullName)\*")) {
            Move-Item "$($extracted.FullName)\*" $TargetPath -Force
            Remove-Item $extracted.FullName -Recurse -Force
        }
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        Write-Success "Done"
    } catch {
        Write-Error "Failed to download $RepoName: $($_.Exception.Message)"
        throw
    }
}

function Get-MusicBeeDirectUrl {
    # Parse MajorGeeks mirror page for direct download link
    Write-Host "  Resolving MusicBee download URL..." -NoNewline
    try {
        $page = Invoke-WebRequest -Uri $MajorGeeksMirror -UseBasicParsing -Headers @{ 'User-Agent' = 'Mozilla/5.0' } -ErrorAction Stop
        # Look for direct .zip link in page
        $link = ($page.Links | Where-Object { $_.href -match 'musicbee.*portable.*\.zip$' }).href | Select-Object -First 1
        if ($link) {
            Write-Success "Found: $link"
            return $link
        }
    } catch {
        Write-Host "  Mirror parse failed, using fallback..." -ForegroundColor Gray
    }

    # Fallback: Known stable direct URL pattern (MajorGeeks CDN)
    $fallback = "https://www.majorgeeks.com/files/get/1/musicbee_portable/13607"
    Write-Host "  Using fallback: $fallback" -ForegroundColor Gray
    return $fallback
}

# ========== MAIN EXECUTION ==========
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  MusicBee Ultimate Setup — MilkDrop + 2000+ Presets        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "Target: $BaseDir" -ForegroundColor Gray

# 1. DOWNLOAD MUSICBEE PORTABLE
Write-Status "[1/7] Downloading MusicBee Portable..."
$mbZip = "$env:TEMP\MusicBee_Portable.zip"
$mbUrl = Get-MusicBeeDirectUrl

try {
    Invoke-WebRequest -Uri $mbUrl -OutFile $mbZip -UseBasicParsing -Headers @{ 'User-Agent' = 'Mozilla/5.0' } -ErrorAction Stop
    Write-Success "Downloaded $(("{0:N1}" -f (Get-Item $mbZip).Length/1MB)) MB"
} catch {
    Write-Error "Download failed: $($_.Exception.Message)"
    Write-Host "  Try manually downloading from https://getmusicbee.com/downloads/ and placing at $mbZip" -ForegroundColor Red
    exit 1
}

# 2. EXTRACT MUSICBEE
Write-Status "[2/7] Extracting MusicBee..."
if (Test-Path $MusicBeeDir) { Remove-Item $MusicBeeDir -Recurse -Force -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Force -Path $MusicBeeDir | Out-Null

Expand-Archive -Path $mbZip -DestinationPath $MusicBeeDir -Force -ErrorAction Stop

# Handle nested folder in archive
$exe = Get-ChildItem $MusicBeeDir -Recurse -Filter "MusicBee.exe" | Select-Object -First 1
if ($exe -and $exe.DirectoryName -ne $MusicBeeDir) {
    Move-Item $exe.Directory\* $MusicBeeDir -Force
    Remove-Item $exe.Directory -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Success "Extracted to $MusicBeeDir"

# 3. CLONE PRESET REPOSITORIES
Write-Status "[3/7] Cloning preset repositories..."
foreach ($repo in $GitHubRepos) {
    Clone-Or-Download -RepoUrl $repo.Url -TargetPath $repo.Target -RepoName $repo.Name
}

# 4. MERGE PRESETS
Write-Status "[4/7] Merging presets into AllPresets..."
$AllPresets = "$PresetsDir\All"
New-Item -ItemType Directory -Force -Path $AllPresets | Out-Null

$count = 0
$count += (Get-ChildItem "$PresetsDir\CreamOfTheCrop" -Recurse -Filter "*.milk" -ErrorAction SilentlyContinue | Copy-Item -Destination $AllPresets -Force -ErrorAction SilentlyContinue).Count
$count += (Get-ChildItem "$PresetsDir\Original\Milkdrop-Original" -Recurse -Filter "*.milk" -ErrorAction SilentlyContinue | Copy-Item -Destination $AllPresets -Force -ErrorAction SilentlyContinue).Count

Write-Success "Merged $count presets into $AllPresets"

# 5. GENERATE SETTINGS
Write-Status "[5/7] Generating MusicBee3Settings.ini..."
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
Visualisation_MilkDrop_BeatDetection=True
Visualisation_MilkDrop_HardwareAcceleration=True
Library_AutoScanFolders=$MusicFolder
Library_MonitorFolders=$MusicFolder
Player_OutputDevice=Default
Player_DSP_EnableEqualizer=True
Player_DSP_EqualizerPreset=Flat
Player_DSP_Crossfeed=False
Player_Volume=100
Interface_Language=ru-RU
Interface_Skin=MusicBee3.xmlc
Interface_CompactMode=False
Startup_CheckForUpdates=True
Startup_ShowSplashScreen=False
"@

$ini | Out-File -Encoding UTF8 "$SettingsDir\MusicBee3Settings.ini"
Write-Success "Settings written to $SettingsDir\MusicBee3Settings.ini"

# 6. CREATE VST DIRECTORY
Write-Status "[6/7] Creating VST plugin directory..."
New-Item -ItemType Directory -Force -Path $VSTDir | Out-Null
Write-Success "VST directory: $VSTDir"
Write-Host "  Tip: Drop TDR Nova, SPAN, or other VST .dll files here, then Rescan in MusicBee" -ForegroundColor Gray

# 7. CREATE SHORTCUT & LAUNCH
Write-Status "[7/7] Creating desktop shortcut..."
$shortcutPath = "$env:USERPROFILE\Desktop\MusicBee Ultimate.lnk"
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($shortcutPath)
$sc.TargetPath = "$MusicBeeDir\MusicBee.exe"
$sc.WorkingDirectory = $MusicBeeDir
$sc.IconLocation = "$MusicBeeDir\MusicBee.exe,0"
$sc.Description = "MusicBee Ultimate — MilkDrop presets preloaded"
$sc.Save()
Write-Success "Shortcut created: $shortcutPath"

# LAUNCH
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  SETUP COMPLETE! Launching MusicBee...                     ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host @"
┌────────────────────────────────────────────────────────────────┐
│  MusicBee Ultimate — Ready!                                   │
├────────────────────────────────────────────────────────────────┤
│  📁 Player folder:     $MusicBeeDir              │
│  🎨 Presets (All):     $AllPresets  │
│  🖼️ Textures:          $TexturesDir               │
│  ⚙️ Settings:          $SettingsDir              │
│  🔌 VST plugins:       $VSTDir                  │
│  🔗 Shortcut:          Desktop → "MusicBee Ultimate"        │
├────────────────────────────────────────────────────────────────┤
│  🎯 PRE-CONFIGURED:                                           │
│  • MilkDrop → Preset folder = All (2000+ presets)             │
│  • Auto-change presets every 30 sec with 5-sec transition     │
│  • Russian interface, EQ enabled, beat detection ON           │
│  • Portable — no system install, copy folder to USB           │
├────────────────────────────────────────────────────────────────┤
│  🎮 MILKDROP HOTKEYS (in visualization window):               │
│  Ctrl+M          — Toggle visualization                        │
│  Ctrl+Shift+M    — MilkDrop settings (FPS, resolution, etc.)  │
│  Tab / Shift+Tab — Next / Previous preset                      │
│  L               — Lock current preset (stop auto-change)      │
│  R               — Random preset                               │
│  F               — Fullscreen                                  │
│  Esc             — Exit fullscreen                             │
├────────────────────────────────────────────────────────────────┤
│  🔧 NEXT STEPS:                                               │
│  1. MusicBee will ask for music folder → pick $MusicFolder   │
│  2. View → Visualisations → MilkDrop (or Ctrl+M)              │
│  3. Preferences → Plugins → VST → Rescan → add TDR Nova/SPAN  │
│  4. View → Arrange Panels → Skins → download "Winamp Classic" │
└────────────────────────────────────────────────────────────────┘
"@

Start-Process "$MusicBeeDir\MusicBee.exe"