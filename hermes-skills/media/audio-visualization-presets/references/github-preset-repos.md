# GitHub MilkDrop/projectM Preset Repositories — API-Verified Details

*Last verified: 2026-08-03 via GitHub API*

---

## Curated Preset Collections

### `projectM-visualizer/presets-cream-of-the-crop` ⭐ 149
**Description:** Jason Fletcher's curated preset pack containing only the best of the best of all released Milkdrop presets. This is the default preset pack in most new projectM releases.

**Structure (from API):**
```
! Transition/
Dancer/
Drawing/
Fractal/
Geometric/
Hypnotic/
Particles/
Reaction/
Sparkle/
Supernova/
Waveform/
LICENSE.md
README.md
```

**Clone:** `git clone https://github.com/projectM-visualizer/presets-cream-of-the-crop`

**Verified file count:** 9,797 `.milk` files (2026-08-03)

---

### `projectM-visualizer/presets-milkdrop-original` ⭐ 33
**Description:** The original preset pack that was deployed with the last official Milkdrop release, textures excluded.

**Structure (from API):**
```
Milkdrop-Original/  (200+ .milk files)
README.md
```

**Notable authors (from file listing):** Geiss, Flexi, Rovastar, Unchained, Phat, Eo.S., Martin, ORB, Zylot, Stahlregen, Benski, Krash, Goody, Aderrasi, fiShbRaiN, shifter, baked, cope, fed, Idiot, Illusion, Mstress, PieturP, Redi Jedi, Reenen, Rocke, Rozzor, Tokyo corridor, yin, and many collaborations.

**Clone:** `git clone https://github.com/projectM-visualizer/presets-milkdrop-original`

**Verified file count:** ~400 `.milk` files in `Milkdrop-Original/` (2026-08-03)

---

### `projectM-visualizer/presets-milkdrop-texture-pack` ⭐ 43
**Description:** This repository contains all textures originally released with Milkdrop, plus a good number of other textures used in a large number of presets.

**Clone:** `git clone https://github.com/projectM-visualizer/presets-milkdrop-texture-pack`

---

## Engines & Tools

### `milkdrop2077/MilkDrop3` ⭐ 1415
**Description:** MilkDrop 3.0, supports any audio source, double-preset (.milk2), loading presets based on beat detection and much more.

**Release asset:** `MilkDrop3.exe` (71.4 MB) — standalone Windows executable

**Repo structure:**
```
code/
  audio/
  ns-eel2/
  resources/
    Milkdrop2/
  vis_milk2/
linux/
README.md
LICENSE.txt
MilkDrop3.sln
```

**Clone:** `git clone https://github.com/milkdrop2077/MilkDrop3`

---

### `milkdrop2077/milkdrop2077` ⭐ 49
**Description:** MilkDrop2077 is a free and open-source presets generator / masher and randomizer for MilkDrop / projectM / BeatDrop Music Visualizer.

**Clone:** `git clone https://github.com/milkdrop2077/milkdrop2077`

---

### `jberg/milkdrop-preset-converter` ⭐ 22
**Description:** Convert Milkdrop presets to Butterchurn JSON format.

**Clone:** `git clone https://github.com/jberg/milkdrop-preset-converter`

---

### `gattis/milkshake` ⭐ 229
**Description:** WebGL Milkdrop Preset Renderer.

**Clone:** `git clone https://github.com/gattis/milkshake`

---

### `jberg/butterchurn-presets` ⭐ 44
**Description:** Presets for Butterchurn Visualizer, converted from Milkdrop presets.

**Clone:** `git clone https://github.com/jberg/butterchurn-presets`

---

### `SpasilliumNexus/poweramp-visualizer-presets` ⭐ 54
**Description:** Custom Milkdrop (MILK) visualization presets for Poweramp v3.

**Releases:** https://github.com/SpasilliumNexus/poweramp-visualizer-presets/releases

**Clone:** `git clone https://github.com/SpasilliumNexus/poweramp-visualizer-presets`

---

## Summary: Recommended Minimum Clone Set

```bash
# Essential: curated best presets + required textures
git clone https://github.com/projectM-visualizer/presets-cream-of-the-crop
git clone https://github.com/projectM-visualizer/presets-milkdrop-texture-pack

# Optional: original full pack (200+ more presets)
git clone https://github.com/projectM-visualizer/presets-milkdrop-original

# Optional: modern MilkDrop 3 engine (standalone app)
# Download MilkDrop3.exe from https://github.com/milkdrop2077/MilkDrop3/releases
```

---

## Verified Preset Counts (2026-08-03)

| Source | Files | Notes |
|--------|-------|-------|
| `presets-cream-of-the-crop` | 9,797 `.milk` | Curated best-of, categorized folders |
| `presets-milkdrop-original/Milkdrop-Original` | ~400 `.milk` | Original last official release |
| **Merged `All` folder** | **10,184** | Deduplicated union of both |

---

## Working Automation Pattern (MusicBee Ultimate)

Since direct download of MusicBee Portable is blocked by bot protection, the reliable workflow is:

1. **Manual (30 sec):** Download MusicBee Portable ZIP from https://getmusicbee.com/downloads/ → extract to `~/MusicBeeUltimate/MusicBee/`
2. **Automated (script):** Run `scripts/setup-musicbee-ultimate.ps1` that:
   - Clones all 3 preset repos (idempotent, removes existing dirs first)
   - Merges `.milk` files into `~/MusicBeeUltimate/MilkDropPresets/All/`
   - Writes `MusicBee3Settings.ini` to `%APPDATA%\MusicBee\` with preset/texture paths
   - Creates VST plugin folder and desktop shortcut
   - Launches MusicBee

**Script usage:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-musicbee-ultimate.ps1
```

**Prerequisites:** MusicBee Portable already extracted, Git in PATH, PowerShell execution policy allows scripts.