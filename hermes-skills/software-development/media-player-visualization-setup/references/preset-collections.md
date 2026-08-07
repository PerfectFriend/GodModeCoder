# Preset Collections Reference

Detailed inventory of MilkDrop preset repositories on GitHub.

## 1. presets-cream-of-the-crop (projectM-visualizer)
- **Stars**: 149
- **Description**: Jason Fletcher's curated preset pack containing only the best of all released Milkdrop presets. Default in most projectM releases.
- **Structure**: Organized by category folders:
  - `Transition/` — transition effects
  - `Dancer/` — dancer/motion presets
  - `Drawing/` — line/drawing presets
  - `Fractal/` — fractal-based presets
  - `Geometric/` — geometric shapes
  - `Hypnotic/` — hypnotic/trance presets
  - `Particles/` — particle systems
  - `Reaction/` — reaction-diffusion
  - `Sparkle/` — sparkle/glitter effects
  - `Supernova/` — supernova/explosion
  - `Waveform/` — waveform visualizations
- **File count**: ~200+ `.milk` files
- **License**: Various (original authors retained)

## 2. presets-milkdrop-original (projectM-visualizer)
- **Stars**: 33
- **Description**: Original preset pack from last official MilkDrop release (textures excluded)
- **Structure**: Flat folder `Milkdrop-Original/` with all presets
- **File count**: ~400+ `.milk` files
- **Authors**: Geiss, Flexi, Rovastar, Unchained, Phat, Eo.S., Martin, ORB, Zylot, Stahlregen, Aderrasi, Benski, Goody, Krash, and many more
- **Notable presets**: Glowsticks series, Fractopia, Tokamak, Cerebral Demons, Witchcraft, Mindblob, etc.

## 3. presets-milkdrop-texture-pack (projectM-visualizer)
- **Stars**: 43
- **Description**: All textures originally released with MilkDrop, plus additional textures used in many presets
- **Required for**: Many presets from both collections above reference these textures
- **File types**: `.jpg`, `.png`, `.bmp` texture files

## 4. MilkDrop3 (milkdrop2077/MilkDrop3)
- **Stars**: 1415
- **Description**: Modern MilkDrop 3.0 fork — standalone app, supports any audio source (WASAPI loopback), double-preset (.milk2), beat detection
- **Release**: `MilkDrop3.exe` (71 MB) — standalone Windows executable
- **Use case**: Run visualizations independent of media player

## 5. milkdrop2077 (milkdrop2077/milkdrop2077)
- **Stars**: 49
- **Description**: Preset generator/masher/randomizer for MilkDrop/projectM/BeatDrop
- **Use case**: Create new unique presets by combining/mutating existing ones

## Combined Stats
| Collection | Presets | Size |
|------------|---------|------|
| cream-of-the-crop | ~200+ | ~2 MB |
| milkdrop-original | ~400+ | ~4 MB |
| **Merged (AllPresets)** | **~600+** | **~6 MB** |
| Textures | ~100+ | ~50 MB |

## Download Commands

```bash
# Full clone (requires git)
git clone --depth 1 https://github.com/projectM-visualizer/presets-cream-of-the-crop
git clone --depth 1 https://github.com/projectM-visualizer/presets-milkdrop-original
git clone --depth 1 https://github.com/projectM-visualizer/presets-milkdrop-texture-pack

# No git? Use ZIP downloads:
# https://github.com/projectM-visualizer/presets-cream-of-the-crop/archive/refs/heads/main.zip
# https://github.com/projectM-visualizer/presets-milkdrop-original/archive/refs/heads/main.zip
# https://github.com/projectM-visualizer/presets-milkdrop-texture-pack/archive/refs/heads/main.zip
```

## MusicBee Configuration

In MilkDrop settings (Ctrl+Shift+M in visualization window):
- **Preset directory**: `<path>\AllPresets`
- **Texture directory**: `<path>\presets-milkdrop-texture-pack`
- **Auto-change presets**: Enabled
- **Change interval**: 30 seconds
- **Transition duration**: 5 seconds