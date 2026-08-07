---
name: media-player-visualization-setup
description: Set up players with MilkDrop visualizations and presets.
category: software-development
tags:
  - musicbee
  - aimp
  - foobar2000
  - milkdrop
  - projectm
  - visualization
  - presets
  - powershell
  - automation
---

# Media Player Visualization Setup

**Trigger**: User wants a modern Winamp-like media player with programmable visualizations (MilkDrop/projectM) and ready-to-use preset collections.

## Player Selection Guide

| Player | Best For | MilkDrop Support | Complexity |
|--------|----------|------------------|------------|
| **MusicBee** | Best balance — modern UI, portable, free, great library mgmt | **NOT in Portable build** — installer version has it in Preferences → Visualizations; Portable requires external visualizer (Plane9/projectM) | Low |
| **AIMP** | Closest to Winamp feel, Russian, skin engine compatible | Via Winamp DSP/vis plugins (copy `vis_milk2.dll` + textures) | Low |
| **foobar2000** | Maximum customization, component architecture | Via `foo_vis_shpeck` (loads real MilkDrop.dll) or `foo_vis_projectm` | High |

**Default recommendation**: **MusicBee Portable + Plane9** — MusicBee handles library/playback, Plane9 handles visualization (works with any audio source, 250+ scenes, WASAPI Loopback, Spout for OBS).

---

## Preset Collections (GitHub)

Clone these three repos for a complete "best of" preset library (**~600 `.milk` files**):

```bash
# Curated best presets (default in projectM)
git clone https://github.com/projectM-visualizer/presets-cream-of-the-crop

# Original MilkDrop 2.x presets (Geiss, Flexi, Rovastar, Unchained, Phat, Eo.S., Martin, ORB, Zylot, Stahlregen...)
git clone https://github.com/projectM-visualizer/presets-milkdrop-original

# Required textures for many presets
git clone https://github.com/projectM-visualizer/presets-milkdrop-texture-pack
```

**Merge for convenience**:
```bash
mkdir AllPresets
cp presets-cream-of-the-crop/**/*.milk AllPresets/
cp presets-milkdrop-original/Milkdrop-Original/*.milk AllPresets/
```

Point MusicBee MilkDrop settings → Preset folder: `AllPresets`, Texture folder: `presets-milkdrop-texture-pack`.

---

## Automated Setup Script (PowerShell)

See `scripts/Setup-PresetsOnly.ps1` — **recommended workflow** (MusicBee must be manually downloaded first):
1. **User manually downloads** MusicBee Portable from getmusicbee.com/downloads/ → extracts to `~/MusicBeeUltimate/MusicBee/`
2. Script clones all 3 preset repos (**with ZIP fallback if git unavailable**)
3. Merges presets into `AllPresets` (**~600 `.milk` files**, **10,184 total with all subdirs**)
4. Writes `MusicBee3Settings.ini` with preset/texture paths, auto-rotation (30s), Russian UI, EQ enabled
5. Creates VST plugin directory (`Plugins/VST`)
6. Creates desktop shortcut
7. Launches MusicBee

**Usage**: Save as `.ps1`, right-click → "Run with PowerShell". No admin required.

**Full script** `scripts/Setup-MusicBeeUltimate.ps1` attempts automated download but **MajorGeeks blocks bots** — falls back to manual download prompt.

**Critical**: MusicBee Portable **does NOT include MilkDrop plugin** (`vis_milk2.dll` missing). The INI settings for MilkDrop are ignored. For visualization, use **Plane9** (see below).

---

## MusicBee MilkDrop Hotkeys

| Key | Action |
|-----|--------|
| `Ctrl+M` | Toggle visualization |
| `Ctrl+Shift+M` | MilkDrop settings (FPS, resolution, beat detection) |
| `Tab` / `Shift+Tab` | Next / previous preset |
| `L` | Lock current preset (disable auto-change) |
| `R` | Random preset |
| `F` | Fullscreen |
| `Esc` | Exit fullscreen |

---

## Plane9 — Modern AVS Successor (Recommended for MusicBee Portable)

Since **MusicBee Portable excludes MilkDrop**, use **Plane9** as the visualization engine:

| Feature | Details |
|---------|---------|
| **Download** | https://plane9.com/ or https://www.majorgeeks.com/files/details/plane9.html |
| **Audio input** | WASAPI Loopback (captures **any system audio** — MusicBee, Spotify, browser, games) |
| **Scenes** | 250+ built-in, **imports Winamp `.avs` presets** |
| **OBS/Streaming** | Native **Spout/Syphon** output — add as "Video Capture Device" → "Spout Capture" in OBS |
| **Hotkeys** | `F11`=fullscreen, `Space`=next scene, `Shift+Space`=prev, `L`=lock, `P`=pause, `F5`=screenshot |
| **Multi-monitor** | Fullscreen on any monitor, windowed mode supported |
| **Portability** | Installer-based but portable-friendly (settings in `%APPDATA%\Plane9`) |

**Setup (1 minute):**
1. Install Plane9
2. Tray icon → Settings → Audio → Device: **WASAPI Loopback (Default)**
3. `F11` for fullscreen, `Space` to cycle scenes

**Stack**: **MusicBee Portable (library/playback) + Plane9 (visualization)** — zero conflicts, both free, works with any audio source.

---

## VST Plugin Enhancement (Optional — for MusicBee)

Add professional DSP to MusicBee's chain (`Preferences → Plugins → VST → Rescan`):

- **TDR Nova** (free dynamic EQ) — `https://www.tokyodawn.net/tdr-nova/`
- **SPAN** (free spectrum analyzer) — `https://www.voxengo.com/product/span/`

Drop `.dll` files into `MusicBee/Plugins/VST/`.

---

## Pitfalls & Fixes

| Issue | Fix |
|-------|-----|
| MusicBee official site MEGA links require JS | Use MajorGeeks mirror or parse `mg/getmirror/musicbee_portable,1.html` for direct URL |
| **MajorGeeks mirror blocks automated downloads (bot protection)** | **Recommended: Manual download + script. User downloads Portable ZIP from getmusicbee.com/downloads/, extracts to `~/MusicBeeUltimate/MusicBee/`, then runs preset-only script** |
| MilkDrop presets not loading | Ensure `Visualisation_MilkDrop_TextureFolder` points to texture pack repo |
| Presets show errors (missing textures) | Clone `presets-milkdrop-texture-pack` and set texture folder |
| Portable MusicBee loses settings | Settings stored in `%APPDATA%\MusicBee\MusicBee3Settings.ini` — script writes there |
| **MilkDrop not showing in MusicBee Portable** | **Portable build excludes `vis_milk2.dll` (licensing)** — only Installer version has it. **Fix:** Use Plane9 standalone visualizer instead. The preset collection still works with projectM, MilkDrop3, Winamp, Butterchurn. |
| Git not available | Use GitHub ZIP downloads: `https://github.com/owner/repo/archive/refs/heads/main.zip` |
| **Preset count lower than expected** | **cream-of-the-crop ~200, milkdrop-original ~400, merged ~600 total** (not 2000). Full tree clone yields ~10,184 `.milk` files in AllPresets due to many subdirectories. |
| **Git clone stderr pollutes PowerShell** | `git clone` writes progress to stderr → PowerShell shows as error. Fix: `$result = git clone ... *>&1` and check `$LASTEXITCODE`. |
| **Existing clone directory blocks re-run** | Must remove before clone: `if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }` |
| **MajorGeeks bot protection blocks auto-download** | Manual download required: user gets ZIP from getmusicbee.com/downloads/, extracts to target folder. |

---

## References

- `references/preset-collections.md` — Detailed preset repo inventory with file counts
- `references/musicbee-config-keys.md` — Full MusicBee3Settings.ini key reference
- `references/vst-plugins.md` — Curated free VST list for audio enhancement

## Templates

- `templates/MusicBee3Settings.ini.template` — Base configuration with MilkDrop paths as variables

## Scripts

- `scripts/Setup-MusicBeeUltimate.ps1` — Full automated setup (download, extract, clone, configure, launch)
- `scripts/Download-Presets.ps1` — Standalone preset downloader/merger
- `scripts/Install-VST-Plugins.ps1` — Fetches TDR Nova + SPAN into VST folder