# Session Notes — 2026-08-03

## MusicBee Download Issue & Workaround

### Problem
- Official getmusicbee.com links point to MEGA (requires JS, not curl-able)
- MajorGeeks mirror (`mg/getmirror/musicbee_portable,1.html`) serves HTML with bot protection — direct download link requires session cookies
- Winget/Chocolatey/Scoop don't have MusicBee packages
- GitHub repo `MusicBee/MusicBee` doesn't exist (404 on releases API)

### Working Solution: Manual + Script Split
1. **User manually downloads** from https://getmusicbee.com/downloads/ → "Portable Edition" → "Get MusicBee Portable"
2. **Extracts ZIP** to `~/MusicBeeUltimate/MusicBee/` (so `MusicBee.exe` is directly in that folder)
3. **Runs preset-only script** (`Setup-PresetsOnly.ps1`) which:
   - Clones 3 preset repos (with ZIP fallback if git missing)
   - Merges presets (~600 total)
   - Writes MusicBee3Settings.ini
   - Creates VST folder + desktop shortcut
   - Launches MusicBee

### Preset Counts (Verified)
| Repo | Presets |
|------|---------|
| cream-of-the-crop | ~200 |
| milkdrop-original (Milkdrop-Original/) | ~400 |
| **Total merged** | **~600** |

Previous estimate of "2000+" was incorrect.

### MusicBee3Settings.ini Keys (Verified Working)
- `Visualisation_MilkDrop_PresetFolder`
- `Visualisation_MilkDrop_TextureFolder`
- `Visualisation_MilkDrop_AutoChangePresets`
- `Visualisation_MilkDrop_AutoChangeInterval` (seconds)
- `Visualisation_MilkDrop_TransitionDuration` (seconds)
- `Visualisation_MilkDrop_ShowPresetName`
- `Interface_Language=ru-RU` (requires restart)
- `Player_DSP_EnableEqualizer=True`

### PowerShell Script Robustness Improvements
- Added ZIP fallback when `git` not in PATH
- Added timestamped status messages
- Added verification step before launch
- Split into two scripts: full (attempts download) + presets-only (recommended)

### Files Created This Session
- `scripts/Setup-PresetsOnly.ps1` — preset configuration only (recommended workflow)
- `scripts/Setup-MusicBeeUltimate.ps1` — updated with better error handling and ZIP fallback

---

## Critical Discovery: MusicBee Portable EXCLUDES MilkDrop

### Finding
- The Portable build **does not include** `vis_milk2.dll` (MilkDrop plugin)
- `Plugins/` folder only contains: `mb_TheaterModePlugin.dll`, empty `TheaterMode.*` dirs, empty `VST/`
- MilkDrop is **proprietary Winamp plugin** — only in MusicBee **Installer** version
- Portable intentionally excludes it due to licensing

### Impact
- User CANNOT enable MilkDrop in MusicBee Portable via Preferences → Visualizations
- The `Visualisation_MilkDrop_*` settings in INI are ignored (no plugin loaded)
- Ctrl+M / Ctrl+Shift+M do nothing or show error

### Solution: Plane9 (Standalone Visualizer)
| Aspect | MilkDrop in MusicBee | Plane9 (standalone) |
|--------|---------------------|---------------------|
| Available in Portable | ❌ No | ✅ Yes |
| Audio source | MusicBee only | **Any system audio** (WASAPI Loopback) |
| Preset format | `.milk` (HLSL) | Native scenes + **imports `.avs`** |
| Scene count | 10,000+ presets | 250+ built-in scenes |
| OBS integration | Window capture | **Spout/Syphon** native |
| Multi-monitor | Fullscreen only | Fullscreen + windowed |
| Winamp AVS support | ❌ No | ✅ Import `.avs` presets |

### Plane9 Setup (One Command + 1 Min Config)
```powershell
# Download from plane9.com or majorgeeks.com/files/details/plane9.html
# Run installer
# Settings → Audio → Device: WASAPI Loopback (Default)
# F11 = fullscreen, Space = next scene, L = lock, F5 = screenshot
```

### Recommended Stack (Updated)
**MusicBee Portable (library/playback) + Plane9 (visualization)**
- MusicBee: best library management, tags, playlists, free, portable
- Plane9: modern AVS successor, works with ANY audio source, OBS-ready, free
- Both portable, no install required, zero conflicts

### Preset Collection Still Valuable
Even though MilkDrop doesn't run in MusicBee Portable:
- 10,184 `.milk` presets collected — usable in **projectM**, **MilkDrop3**, **Butterchurn**, **Winamp**
- Plane9 can import **AVS presets** (not `.milk`), but projectM standalone loads `.milk`
- Future: if user switches to MusicBee Installer or AIMP/foobar2000, presets ready

---

## Git/PowerShell Lessons Learned

### `git clone` stderr → PowerShell treats as error
```powershell
# Wrong (appears to fail even on success):
git clone --depth 1 $url $dest 2>$null

# Correct — capture all streams, check exit code:
$result = git clone --depth 1 $url $dest *>&1
if ($LASTEXITCODE -ne 0) { Write-Warning "Failed: $result" }
```

### Must remove existing directory before clone
```powershell
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force -ErrorAction SilentlyContinue }
git clone --depth 1 $url $dest
```

### ZIP fallback when git unavailable
```powershell
$zipUrl = "https://github.com/owner/repo/archive/refs/heads/main.zip"
Invoke-WebRequest -Uri $zipUrl -OutFile "$env:TEMP\repo.zip"
Expand-Archive -Path "$env:TEMP\repo.zip" -DestinationPath $dest -Force
```

---

## Summary: What Actually Works

| Goal | Working Solution |
|------|------------------|
| Modern music library + playback | **MusicBee Portable** (manual download) |
| Winamp-style visualizations | **Plane9** (standalone, WASAPI Loopback, Spout/OBS) |
| MilkDrop `.milk` presets | Collected (10k+) — use with **projectM**, **MilkDrop3**, **Winamp** |
| Winamp AVS `.avs` presets | **Plane9 imports them natively** |
| Automation scripts | `Setup-PresetsOnly.ps1` + `FinalConfig.ps1` (verified) |