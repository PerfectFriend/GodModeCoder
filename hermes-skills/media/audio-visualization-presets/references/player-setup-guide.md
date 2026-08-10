# Player Setup Guide — MilkDrop/projectM Integration

*For MusicBee, AIMP, foobar2000*

---

## MusicBee (Recommended — Easiest Setup)

**Version:** 3.5+ (current as of 2026)
**MilkDrop version embedded:** 2.x (not 3.x)

### Quick Setup

1. **Install MusicBee** — Portable version recommended:
   - Download: https://getmusicbee.com/downloads/
   - Choose "Portable" ZIP → extract anywhere → run `MusicBee.exe`
   - No admin/UAC, no registry pollution

2. **Enable MilkDrop Visualization:**
   - `Preferences` (Ctrl+,) → `Visualizations` → `MilkDrop`
   - Check "Enable MilkDrop visualization"
   - Click "Configure" → set:
     - **Preset directory:** `<path-to>\presets-cream-of-the-crop`
     - **Textures directory:** `<path-to>\presets-milkdrop-texture-pack`
   - OK → Apply

3. **Use:**
   - Play music → `View` → `Visualizations` → `MilkDrop` (or Ctrl+Shift+V)
   - `H` = preset help, `M` = preset menu, `L` = load preset, `S` = save preset
   - `F` = fullscreen, `Esc` = exit fullscreen

### Portable MusicBee + Presets (Self-Contained)

```
MusicBeePortable/
├── MusicBee.exe
├── Presets/
│   ├── cream-of-the-crop/     ← git clone presets-cream-of-the-crop
│   ├── milkdrop-original/     ← git clone presets-milkdrop-original (optional)
│   └── textures/              ← git clone presets-milkdrop-texture-pack
└── ...
```

Point MilkDrop config to `./Presets/cream-of-the-crop` and `./Presets/textures`.

---

## AIMP (Best for "Winamp Feel")

**Version:** 5.10+ (current as of 2026)
**Engine:** Native Winamp DSP/Visualization plugin support

### Setup

1. **Install AIMP** — https://www.aimp.ru/
   - Russian interface, lightweight, Winamp skin support (.wsz)

2. **Enable Visualizations:**
   - `Настройки` (Settings) → `Визуализации` (Visualizations)
   - Add plugin: `MilkDrop` (built-in) or load `vis_milk2.dll` (Winamp's original)
   - Configure preset/texture paths same as MusicBee

3. **Winamp Skins:**
   - `Настройки` → `Оформление` → `Скины` → load `.wsz` files
   - Thousands at: https://www.winamp.com/skins/

---

## foobar2000 (Maximum Customization)

**Version:** 2.1+ (current as of 2026)
**Engine options:**
- **Shpeck** (foo_vis_shpeck) — loads **real** `vis_milk2.dll` from Winamp 5.66
- **projectM** (foo_vis_projectm) — open-source MilkDrop-compatible engine

### Option A: Shpeck (Authentic MilkDrop)

1. **Install foobar2000** — https://www.foobar2000.org/

2. **Install Shpeck component:**
   - Download `foo_vis_shpeck.fb2k-component` from https://www.foobar2000.org/components/view/foo_vis_shpeck
   - Double-click to install, or `Preferences` → `Components` → `Install...`

3. **Get Winamp's `vis_milk2.dll`:**
   - Install Winamp 5.66 (last version) somewhere, or extract from portable
   - Copy `vis_milk2.dll` + `Plugins` folder to foobar2000 profile folder

4. **Configure Shpeck:**
   - `Preferences` → `Visualizations` → `Shpeck`
   - Point to `vis_milk2.dll`
   - Set preset/texture directories

**⚠️ Caveat:** Shpeck is 32-bit only. Works on 64-bit Windows via WoW64, but no native 64-bit build.

### Option B: projectM (Native 64-bit, Open Source)

1. **Install foo_vis_projectm** — https://www.foobar2000.org/components/view/foo_vis_projectm

2. **Configure:**
   - `Preferences` → `Visualizations` → `projectM`
   - Preset directory → `presets-cream-of-the-crop`
   - Texture directory → `presets-milkdrop-texture-pack`

**Advantage:** Native 64-bit, active development, no Winamp dependency.

---

## MilkDrop 3 Standalone (milkdrop2077/MilkDrop3)

**Use case:** Full-screen visualization without a music player, or as audio source for streaming.

### Setup

1. **Download:** https://github.com/milkdrop2077/MilkDrop3/releases → `MilkDrop3.exe` (71 MB)

2. **Run:** Double-click → selects audio source (WASAPI loopback = "What U Hear")

3. **Configure:** Press `M` → preset menu, `L` → load preset directory

4. **Preset directories:** Same as above — point to cloned repos

---

## Quick Comparison

| Feature | MusicBee | AIMP | foobar2000 (Shpeck) | foobar2000 (projectM) | MilkDrop3 Standalone |
|---------|----------|------|---------------------|----------------------|---------------------|
| **Ease of setup** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **MilkDrop version** | 2.x (embedded) | 2.x / Winamp 5.66 | Winamp 5.66 (real) | projectM (compat) | 3.x (modern) |
| **Portable** | Yes | Partial | Yes | Yes | Yes |
| **Winamp skins** | No | Yes (.wsz) | No | No | No |
| **64-bit native** | Yes | Yes | No (32-bit only) | Yes | Yes |
| **Preset hot-reload** | Yes | Yes | Yes | Yes | Yes |
| **Double-preset (.milk2)** | No | No | No | Partial | Yes |

---

## Troubleshooting

### "Presets not showing / black screen"
- **Textures missing** → clone `presets-milkdrop-texture-pack` and set texture directory
- **Wrong preset dir** → ensure path points to folder containing `.milk` files (not parent folder)

### "MusicBee MilkDrop crashes"
- Update GPU drivers
- Try disabling hardware acceleration in MilkDrop config
- Some `.milk2` (v3) presets incompatible with embedded v2 engine

### "foobar2000 Shpeck won't load vis_milk2.dll"
- Ensure `vis_milk2.dll` + `Plugins/` folder (with `nscrt.dll`, etc.) are together
- Run foobar2000 as admin once to register
- Use 32-bit foobar2000 if on 32-bit Windows

### "PYTHONPATH leak when running tools from Hermes"
```bash
# Use clean env for any Python-based preset tools
env -u PYTHONPATH -u VIRTUAL_ENV python your_script.py
```

---

## Keyboard Shortcuts (MilkDrop Universal)

| Key | Action |
|-----|--------|
| `H` | Help / preset info |
| `M` | Preset menu |
| `L` | Load preset dialog |
| `S` | Save preset |
| `F` | Fullscreen toggle |
| `Esc` | Exit fullscreen / close menu |
| `Space` | Next preset (random) |
| `Enter` | Next preset (sequential) |
| `Backspace` | Previous preset |
| `R` | Random preset |
| `P` | Pause visualization |
| `+`/`-` | Speed up/slow down |
| `F1`..`F12` | User preset slots (save with Shift+F1..F12) |