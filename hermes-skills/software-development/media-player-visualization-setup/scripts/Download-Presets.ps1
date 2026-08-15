<#>
.SYNOPSIS
    Standalone MilkDrop preset downloader/merger for MusicBee, AIMP, foobar2000, or projectM.

.DESCRIPTION
    Downloads and merges the three essential preset collections from GitHub:
    - presets-cream-of-the-crop (curated best)
    - presets-milkdrop-original (official MilkDrop 2.x presets)
    - presets-milkdrop-texture-pack (required textures)

    Outputs a merged AllPresets folder ready to point any MilkDrop-compatible player at.

.USAGE
    powershell -ExecutionPolicy Bypass -File .\Download-Presets.ps1
    powershell -ExecutionPolicy Bypass -File .\Download-Presets.ps1 -TargetDir "D:\MyPresets"
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$TargetDir = "$env:USERPROFILE\MusicBeeUltimate\MilkDropPresets",
    
    [Parameter()]
    [string]$TextureDir = "$env:USERPROFILE\MusicBeeUltimate\MilkDropTextures",
    
    [switch]$NoGit
)

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = 'Stop'

$gitAvailable = -not $NoGit -and (try { git --version 2>$null; $true } catch { $false })

$repos = @(
    @{ Name="cream-of-the-crop"; Url="https://github.com/projectM-visualizer/presets-cream-of-the-crop"; SubPath=""; Target="$TargetDir\CreamOfTheCrop" },
    @{ Name="milkdrop-original"; Url="https://github.com/projectM-visualizer/presets-milkdrop-original"; SubPath="Milkdrop-Original"; Target="$TargetDir\Original" },
    @{ Name="milkdrop-textures"; Url="https://github.com/projectM-visualizer/presets-milkdrop-texture-pack"; SubPath=""; Target="$TextureDir" }
)

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  MilkDrop Preset Downloader                                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "Target: $TargetDir" -ForegroundColor Gray
Write-Host "Textures: $TextureDir" -ForegroundColor Gray
Write-Host "Git: $(if ($gitAvailable) { 'Available' } else { 'Disabled (using ZIP)' })" -ForegroundColor Gray

function Clone-Or-Download {
    param($RepoUrl, $TargetPath, $RepoName, $SubPath = "")
    
    if (Test-Path $TargetPath) {
        Write-Host "  ✓ $RepoName already exists" -ForegroundColor Green
        return
    }
    
    New-Item -ItemType Directory -Force -Path (Split-Path $TargetPath) | Out-Null
    
    if ($gitAvailable) {
        Write-Host "  Cloning $RepoName..." -NoNewline
        try {
            git clone --depth 1 $RepoUrl $TargetPath 2>$null
            Write-Host " ✓" -ForegroundColor Green
            return
        } catch {
            Write-Host " ✗ (falling back to ZIP)" -ForegroundColor Yellow
        }
    }
    
    $zipUrl = "$RepoUrl/archive/refs/heads/main.zip"
    $zipPath = "$env:TEMP\$RepoName-main.zip"
    Write-Host "  Downloading $RepoName..." -NoNewline
    try {
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing -Headers @{ 'User-Agent' = 'Mozilla/5.0' }
        Expand-Archive -Path $zipPath -DestinationPath $TargetPath -Force
        # Move contents from repo-main subfolder
        $sub = Get-ChildItem $TargetPath -Directory | Where-Object { $_.Name -like "*-main" } | Select-Object -First 1
        if ($sub) {
            if ($SubPath) { $source = "$($sub.FullName)\$SubPath" } else { $source = $sub.FullName }
            if (Test-Path $source) {
                Move-Item "$source\*" $TargetPath -Force
            }
            Remove-Item $sub.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        Write-Host " ✓" -ForegroundColor Green
    } catch {
        Write-Host " ✗ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        throw
    }
}

# Download all repos
foreach ($repo in $repos) {
    Clone-Or-Download -RepoUrl $repo.Url -TargetPath $repo.Target -RepoName $repo.Name -SubPath $repo.SubPath
}

# Merge presets
Write-Host "`nMerging presets into AllPresets..." -ForegroundColor Yellow
$AllPresets = "$TargetDir\All"
New-Item -ItemType Directory -Force -Path $AllPresets | Out-Null

$files1 = Get-ChildItem "$TargetDir\CreamOfTheCrop" -Recurse -Filter "*.milk" -ErrorAction SilentlyContinue
$files2 = Get-ChildItem "$TargetDir\Original\Milkdrop-Original" -Recurse -Filter "*.milk" -ErrorAction SilentlyContinue

$files1 | Copy-Item -Destination $AllPresets -Force -ErrorAction SilentlyContinue
$files2 | Copy-Item -Destination $AllPresets -Force -ErrorAction SilentlyContinue

$total = (Get-ChildItem $AllPresets -Filter "*.milk").Count
Write-Host "  ✓ Merged $total presets into $AllPresets" -ForegroundColor Green

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║  DONE!                                                       ║
╠══════════════════════════════════════════════════════════════╣
║  Presets:   $AllPresets
║  Textures:  $TextureDir
║  Total:     $total .milk files
╚══════════════════════════════════════════════════════════════╝

Configure your player:
  MusicBee:   Preferences → Visualizations → MilkDrop → Preset folder = AllPresets
  AIMP:       Options → Visualizations → MilkDrop → Presets directory
  foobar2000: Preferences → Visualizations → Shpeck/ProjectM → Preset path
  projectM:   Config → Preset directory = AllPresets
"@