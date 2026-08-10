# MusicBee3Settings.ini Key Reference

Complete reference for MusicBee configuration keys relevant to visualization setup.

## Visualization / MilkDrop Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Visualisation_MilkDrop_PresetFolder` | string | (empty) | Path to folder containing `.milk` preset files |
| `Visualisation_MilkDrop_TextureFolder` | string | (empty) | Path to folder containing texture files (`.jpg`, `.png`, `.bmp`) |
| `Visualisation_MilkDrop_AutoChangePresets` | bool | `False` | Automatically cycle through presets |
| `Visualisation_MilkDrop_AutoChangeInterval` | int | `30` | Seconds between preset changes (when auto-change enabled) |
| `Visualisation_MilkDrop_TransitionDuration` | float | `5.0` | Crossfade transition duration in seconds |
| `Visualisation_MilkDrop_ShowFPS` | bool | `False` | Display FPS counter in visualization window |
| `Visualisation_MilkDrop_ShowPresetName` | bool | `True` | Show preset name on preset change |
| `Visualisation_MilkDrop_FullscreenMonitor` | int | `0` | Monitor index for fullscreen mode |
| `Visualisation_MilkDrop_RenderResolution` | string | `1920x1080` | Render resolution (width x height) |
| `Visualisation_MilkDrop_BeatDetection` | bool | `True` | Enable beat detection for preset transitions |
| `Visualisation_MilkDrop_HardwareAcceleration` | bool | `True` | Use GPU acceleration |

## Library & Playback Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Library_AutoScanFolders` | string | (empty) | Semicolon-separated list of folders to auto-scan |
| `Library_MonitorFolders` | string | (empty) | Semicolon-separated list of folders to monitor for changes |
| `Player_OutputDevice` | string | `Default` | Audio output device name |
| `Player_DSP_EnableEqualizer` | bool | `False` | Enable 10/15/18-band equalizer |
| `Player_DSP_EqualizerPreset` | string | `Flat` | Equalizer preset name |
| `Player_DSP_Crossfeed` | bool | `False` | Enable crossfeed DSP |
| `Player_Volume` | int | `100` | Master volume (0-100) |
| `Player_ReplayGainMode` | string | `Album` | ReplayGain mode: `Off`, `Track`, `Album` |

## Interface Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Interface_Language` | string | `en-US` | UI language code (e.g., `ru-RU`, `en-US`, `de-DE`) |
| `Interface_Skin` | string | `MusicBee3.xmlc` | Skin filename |
| `Interface_CompactMode` | bool | `False` | Use compact player mode |
| `Interface_ShowVisualisation` | bool | `True` | Show visualization panel in main window |

## Startup Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Startup_CheckForUpdates` | bool | `True` | Check for updates on startup |
| `Startup_ShowSplashScreen` | bool | `True` | Show splash screen |
| `Startup_MinimizedToTray` | bool | `False` | Start minimized to system tray |

## Example Configuration

```ini
[MusicBee3Settings]
Visualisation_MilkDrop_PresetFolder=C:\Users\Username\MusicBeeUltimate\MilkDropPresets\All
Visualisation_MilkDrop_TextureFolder=C:\Users\Username\MusicBeeUltimate\MilkDropTextures
Visualisation_MilkDrop_AutoChangePresets=True
Visualisation_MilkDrop_AutoChangeInterval=30
Visualisation_MilkDrop_TransitionDuration=5
Visualisation_MilkDrop_ShowFPS=False
Visualisation_MilkDrop_ShowPresetName=True
Visualisation_MilkDrop_BeatDetection=True
Visualisation_MilkDrop_HardwareAcceleration=True
Library_AutoScanFolders=C:\Users\Username\Music
Library_MonitorFolders=C:\Users\Username\Music
Player_OutputDevice=Default
Player_DSP_EnableEqualizer=True
Player_DSP_EqualizerPreset=Flat
Player_Volume=100
Interface_Language=ru-RU
Interface_Skin=MusicBee3.xmlc
Interface_CompactMode=False
Startup_CheckForUpdates=True
Startup_ShowSplashScreen=False
```

## Notes

- Settings file location: `%APPDATA%\MusicBee\MusicBee3Settings.ini`
- For portable installs, MusicBee still uses `%APPDATA%` for settings (not the portable folder)
- Changes require MusicBee restart to take effect
- Boolean values: `True`/`False` (case-sensitive)
- Paths: Use absolute paths with backslashes or forward slashes