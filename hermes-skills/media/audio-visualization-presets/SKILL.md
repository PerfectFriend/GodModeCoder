---
name: audio-visualization-presets
description: Use for MilkDrop/projectM presets on Winamp alternatives.
category: media
tags:
  - milkdrop
  - projectm
  - visualization
  - musicbee
  - aimp
  - foobar2000
  - winamp-alternative
  - presets
  - shaders
  - hlsl
---

# Audio Visualization Presets — MilkDrop / projectM

**Trigger:** User wants a modern Winamp-like player with programmable visualizations, or needs ready-made preset collections for MilkDrop/projectM engines.

## Modern Winamp Alternatives with Visualization Support

| Player | Engine | Preset Format | Notes |
|--------|--------|---------------|-------|
| **MusicBee** | MilkDrop (built-in) | `.milk` / `.milk2` | Best balance: modern UI, MilkDrop 2.x built-in, portable version available |
| **AIMP** | Winamp DSP/Vis (native) | `.milk` / `.dll` | Russian, lightweight, Winamp skin support (.wsz), 18-band EQ |
| **foobar2000** | Shpeck (loads real MilkDrop.dll) / projectM | `.milk` | Maximum customization, component architecture |

**Recommendation:** Start with **MusicBee** — enables MilkDrop with one checkbox, 200+ presets instantly, portable (no UAC issues).

## GitHub Preset Collections (Clone & Use)

### Best Curated Collections

| Repo | Stars | Contents | Clone Command |
|------|-------|----------|---------------|
| `projectM-visualizer/presets-cream-of-the-crop` | 149 | **Curated best-of** from all MilkDrop releases. Categories: Transition, Dancer, Fractal, Geometric, Hypnotic, Particles, Reaction, Sparkle, Supernova, Waveform | `git clone https://github.com/projectM-visualizer/presets-cream-of-the-crop` |
| `projectM-visualizer/presets-milkdrop-original` | 33 | **Original last official MilkDrop pack** (200+ presets, no textures). Authors: Geiss, Flexi, Rovastar, Unchained, Phat, Eo.S., Martin, ORB, Zylot, Stahlregen… | `git clone https://github.com/projectM-visualizer/presets-milkdrop-original` |
| `projectM-visualizer/presets-milkdrop-texture-pack` | 43 | **Textures** required by many presets | `git clone https://github.com/projectM-visualizer/presets-milkdrop-texture-pack` |

### Engines & Tools

| Repo | Stars | Purpose |
|------|-------|---------|
| `milkdrop2077/MilkDrop3` | 1415 | **Modern MilkDrop 3.x** — standalone app, WASAPI/loopback audio, `.milk2` double-presets, beat detection. Release: `MilkDrop3.exe` (71 MB) |
| `milkdrop2077/milkdrop2077` | 49 | **Preset generator/masher/randomizer** — feed a folder of `.milk`, get unique combinations |
| `jberg/milkdrop-preset-converter` | 22 | Convert `.milk` → JSON for **Butterchurn** (WebGL browser visualizer) |
| `gattis/milkshake` | 229 | WebGL MilkDrop preset renderer |

## Quick Setup (MusicBee Example)

```bash
# 1. Clone curated presets + textures
git clone https://github.com/projectM-visualizer/presets-cream-of-the-crop
git clone https://github.com/projectM-visualizer/presets-milkdrop-texture-pack

# 2. MusicBee: Preferences → Visualizations → MilkDrop
#    Preset directory → presets-cream-of-the-crop
#    Textures directory → presets-milkdrop-texture-pack
```

**AIMP / foobar2000 (Shpeck/projectM):** Same folders, point the plugin to them.

## Programmable Visualizations (Writing Your Own)

MilkDrop uses **HLSL shaders** + per-frame/per-vertex scripts (`.milk` files are text).
- Edit `.milk` files directly — reload in player to test live
- Key variables: `time`, `bass`, `mid`, `treble`, `beat`, `uv`, `texsize`
- MilkDrop 3 / projectM support `.milk2` (double-preset blending)

**Starter template:** See `templates/basic-preset.milk` (create one if needed).

## References

- `references/github-preset-repos.md` — Full repo list with API-verified details, verified preset counts, working automation pattern
- `references/player-setup-guide.md` — Per-player configuration steps
- `scripts/setup-musicbee-ultimate.ps1` — Complete automation script (run after manual MusicBee Portable extract)
- `templates/basic-preset.milk` — HLSL shader starter template for custom presets

## Pitfalls

- **Textures missing** → many presets fail silently; always clone `presets-milkdrop-texture-pack`
- **MusicBee MilkDrop** uses embedded MilkDrop 2.x — some `.milk2` (v3) features won't work
- **foobar2000 + Shpeck** loads actual `vis_milk2.dll` — full compatibility but 32-bit only
- **Portable MusicBee** — extract ZIP, run `MusicBee.exe`, no install/UAC
- **PYTHONPATH leak** — if running preset tools from Hermes env, use `env -u PYTHONPATH -u VIRTUAL_ENV` (see memory)
- **MajorGeeks/MEGA bot protection** — direct download of MusicBee Portable via script fails (404, HTML challenge pages). **Workaround:** manual download from https://getmusicbee.com/downloads/ → "Portable Edition" → extract to target folder, then run automation script for presets/config.
- **PowerShell execution policy** — default blocks `.ps1` scripts. Fix: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` (once per user) or run with `-ExecutionPolicy Bypass`.
- **Git clone not idempotent** — fails if destination exists. Automation must `Remove-Item -Recurse -Force` first or check `Test-Path`.
- **Cyrillic in heredoc strings breaks PowerShell** — use ASCII-only in script literals; emit Russian via `Write-Host` with explicit encoding.