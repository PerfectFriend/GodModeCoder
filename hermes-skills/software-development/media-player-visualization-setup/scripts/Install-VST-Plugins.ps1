<#>
.SYNOPSIS
    Installs free VST plugins (TDR Nova, SPAN) into MusicBee's VST folder.

.DESCRIPTION
    Downloads and extracts professional-grade free VST plugins for use in MusicBee's DSP chain.
    Requires MusicBee VST host (Preferences → Plugins → VST → Rescan after running).

.USAGE
    powershell -ExecutionPolicy Bypass -File .\Install-VST-Plugins.ps1
    powershell -ExecutionPolicy Bypass -File .\Install-VST-Plugins.ps1 -VstDir "C:\MusicBee\Plugins\VST"
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$VstDir = "$env:USERPROFILE\MusicBeeUltimate\MusicBee\Plugins\VST"
)

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = 'Stop'

$plugins = @(
    @{
        Name = "TDR Nova"
        Url = "https://www.tokyodawn.net/wp-content/uploads/2023/11/TDR_Nova_v1.15_Win.zip"
        Description = "Free dynamic EQ (4-band) with parallel compression, sidechain, mid/side"
        DllPattern = "*Nova*.dll"
    },
    @{
        Name = "SPAN"
        Url = "https://www.voxengo.com/download/SPAN/SPAN_v20231110_win64.zip"
        Description = "Real-time spectrum analyzer with correlation meter, multiple views"
        DllPattern = "*SPAN*.dll"
    }
    # Add more plugins here as needed:
    # @{
    #     Name = "TDR Kotelnikov"
    #     Url = "https://www.tokyodawn.net/wp-content/uploads/2023/11/TDR_Kotelnikov_v1.6.0_Win.zip"
    #     Description = "Wideband compressor"
    #     DllPattern = "*Kotelnikov*.dll"
    # }
)

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  VST Plugin Installer for MusicBee                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "VST Directory: $VstDir" -ForegroundColor Gray

New-Item -ItemType Directory -Force -Path $VstDir | Out-Null

$installed = 0

foreach ($plugin in $plugins) {
    Write-Host "`n[$($plugin.Name)]" -ForegroundColor Yellow
    Write-Host "  $($plugin.Description)" -ForegroundColor Gray
    
    $zipPath = "$env:TEMP\$($plugin.Name.Replace(' ', '_')).zip"
    
    Write-Host "  Downloading..." -NoNewline
    try {
        Invoke-WebRequest -Uri $plugin.Url -OutFile $zipPath -UseBasicParsing -Headers @{ 'User-Agent' = 'Mozilla/5.0' } -ErrorAction Stop
        Write-Host " ✓" -ForegroundColor Green
    } catch {
        Write-Host " ✗ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        continue
    }
    
    Write-Host "  Extracting..." -NoNewline
    try {
        $extractDir = "$env:TEMP\$($plugin.Name.Replace(' ', '_'))_extracted"
        if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
        Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
        
        # Find DLL(s)
        $dlls = Get-ChildItem $extractDir -Recurse -Filter $plugin.DllPattern -ErrorAction SilentlyContinue
        if (-not $dlls) {
            # Try broader search
            $dlls = Get-ChildItem $extractDir -Recurse -Filter "*.dll" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch '32' }
        }
        
        foreach ($dll in $dlls) {
            $dest = "$VstDir\$($dll.Name)"
            Copy-Item $dll.FullName -Destination $dest -Force
            Write-Host "  → Installed: $($dll.Name)" -ForegroundColor Green
            $installed++
        }
        
        if (-not $dlls) {
            Write-Host "  ✗ No matching DLL found" -ForegroundColor Red
        }
        
        Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host " ✗ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║  VST INSTALL COMPLETE                                       ║
╠══════════════════════════════════════════════════════════════╣
║  Installed: $installed plugin(s) to $VstDir
╚══════════════════════════════════════════════════════════════╝

NEXT STEPS:
1. Open MusicBee
2. Preferences → Plugins → VST
3. Click "Rescan" (or "Add" and point to $VstDir)
4. Enable plugins in the list
5. Preferences → Player → DSP → Add to chain:
   - TDR Nova (dynamic EQ)
   - SPAN (spectrum analyzer - keep window open for monitoring)

RECOMMENDED DSP CHAIN ORDER:
  Input → TDR Nova → SPAN → Output

TDR NOVA QUICK SETUP:
  - Band 1: High-pass 30 Hz, 12 dB/oct
  - Band 2: Dynamic cut ~200 Hz (mud reduction), ratio 2:1
  - Band 3: Gentle dynamic boost ~3-5 kHz (presence)
  - Band 4: Air shelf 10 kHz+, +1-2 dB
"@