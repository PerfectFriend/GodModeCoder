# Free VST Plugins for MusicBee Enhancement

Curated list of free, high-quality VST plugins compatible with MusicBee's VST host (`Preferences → Plugins → VST → Rescan`).

## Dynamic EQ / Spectral Processing

| Plugin | Developer | Type | Download | Notes |
|--------|-----------|------|----------|-------|
| **TDR Nova** | Tokyo Dawn Records | Dynamic EQ (4-band) | https://www.tokyodawn.net/tDR-nova/ | Best free dynamic EQ; parallel compression, sidechain, mid/side |
| **TDR Kotelnikov** | Tokyo Dawn Records | Compressor | https://www.tokyodawn.net/kotelnikov/ | Wideband compressor, clean and transparent |
| **TDR SlickEQ** | Tokyo Dawn Records | EQ | https://www.tokyodawn.net/slick-eq/ | Mixing/mastering EQ with saturation models |

## Spectrum Analysis / Metering

| Plugin | Developer | Type | Download | Notes |
|--------|-----------|------|----------|-------|
| **SPAN** | Voxengo | Spectrum Analyzer | https://www.voxengo.com/product/span/ | Real-time FFT, multiple views, correlation meter |
| **SPAN Plus** | Voxengo | Spectrum Analyzer | https://www.voxengo.com/product/span-plus/ | Extended version with more features |
| **Loudness Meter** | Youlean | Loudness Meter | https://youlean.co/youlean-loudness-meter/ | LUFS, true peak, LRA — broadcast standards |

## Utility / Enhancement

| Plugin | Developer | Type | Download | Notes |
|--------|-----------|------|----------|-------|
| **MFreeformEqualizer** | MeldaProduction | EQ | https://www.meldaproduction.com/MFreeformEqualizer | Free-form EQ drawing, analyzer |
| **MCompressor** | MeldaProduction | Compressor | https://www.meldaproduction.com/MCompressor | Versatile compressor with visualization |
| **MVibrato** | MeldaProduction | Vibrato | https://www.meldaproduction.com/MVibrato | Creative modulation |
| **TAL-Reverb-4** | TAL Software | Reverb | https://tal-software.com/products/tal-reverb-4 | High-quality plate/hall reverb |
| **TAL-Chorus-LX** | TAL Software | Chorus | https://tal-software.com/products/tal-chorus-lx | Roland Juno-style chorus |

## Installation for MusicBee

1. Create VST folder: `MusicBee/Portable/Plugins/VST/` (or `MusicBee/Plugins/VST/`)
2. Download plugin ZIPs
3. Extract `.dll` files (64-bit / x64) into VST folder
4. In MusicBee: `Preferences → Plugins → VST` → Click `Rescan`
5. Enable desired plugins in DSP chain: `Preferences → Player → DSP`

## Recommended Chain for Music Playback

```
Input → [TDR Nova: gentle dynamic EQ] → [SPAN: monitoring] → Output
```

- **TDR Nova**: High-pass 30Hz, slight dynamic cut at 200Hz (mud), gentle air boost 10kHz+
- **SPAN**: Keep open on second monitor for visual feedback

## Notes

- MusicBee VST host supports **VST2 (.dll)** and **VST3 (.vst3)** — prefer VST2 for compatibility
- **64-bit only** — MusicBee is 64-bit; 32-bit plugins won't load
- Some plugins require **VST3 SDK** or **C++ redistributables** — install if plugin fails to load
- Latency: Keep DSP chain minimal for real-time playback; disable analyzer when not needed
- Presets: Save MusicBee DSP chain as preset for quick recall