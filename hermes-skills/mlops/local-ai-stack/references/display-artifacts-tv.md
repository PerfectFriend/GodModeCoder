# White dots / sparkle on black backgrounds — LCD-TV-as-monitor diagnosis (proven 2026-08, SER9)

## Symptom
White sparkle dots flicker on dark/black backgrounds. "Almost everywhere, stronger
in some places" — NOT confined to one app (rules out per-app renderer bugs; it is a
system-level video-path issue).

## First realization: the "monitor" is actually a TV
`Get-CimInstance Win32_VideoController` → `VideoModeDescription "1920 x 1080"`.
`Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID` → UserFriendlyName
**"22W_LCD_TV"**, manufacturer "VES" (VES3700). It's a 22" LCD television used as a
PC display. This changes the whole diagnosis — TVs do their own aggressive image
processing that computer monitors don't.

## Facts measured on this box
- Connected via **HDMI** (user-confirmed). WMI `WmiMonitorConnectionParams`
  `VideoOutputTechnology=5` claims "DisplayPort" — trust the user/visual over WMI
  here; the controller may report oddly. (0=unin, 2=DVI, 3=HDMI, 4=DVI_A, 5=DP.)
- Refresh **59 Hz** (TV-standard 59.94, non-standard for a PC), `CurrentScanMode=4`.
- EDID native modes (`WmiMonitorListedSupportedSourceModes`) list only **1280x1024
  and below** — 1920x1080 is NOT native for this TV → it is scaling/interpolating,
  which can produce shimmer on fine patterns.
- System event log: **Display event 4107** = TDR ("graphics driver stopped responding
  and was recovered"). Also check `Win32_OperatingSystem.FreePhysicalMemory` — a
  huge BIOS UMA reservation (16 GB on a 24 GB box) can starve the system (0.8 GB
  free → swap) and cause exactly this TDR. See bios-uma-tuning.md.

## Triage order (probability-ranked, user-side first)
1. **TV's own image processing** (highest probability, ~80%): open the TV's on-screen
   menu → picture mode **"PC" or "Game"**; disable **Dynamic Contrast / DCR**,
   **noise reduction / DNR / MPEG-NR**; set **Sharpness = 0**; check
   **Black Level / HDMI RGB range** (Limited ↔ Full mismatch washes blacks or clips).
2. **HDMI cable**: weak / long / unshielded / worn connector → sparkle on dark.
   Reseat or swap for a quality HDMI 2.0 cable.
3. **Pixel format**: Adrenalin → Display → pixel format → **RGB 4:4:4 Full** (TVs
   sometimes negotiate YCbCr limited which can dither shadows).
4. **Adrenalin toggles**: disable **Radeon Image Sharpening** and **Enhanced Sync** —
   both are classic "white dots on black" generators.
5. **Refresh rate**: set 60.000 Hz if the TV accepts it (59 Hz is a TV artifact).

## Why this is NOT the GPU
- Sparkle appears "almost everywhere" but the chat window (Chromium/Electron, hw-
  accelerated) was clean → signal path issue (TV processing / cable / format), not a
  dead GPU.
- TDR 4107 in the log + RAM starvation after UMA change is a memory-pressure story,
  not a hardware fault — fix the RAM balance first (UMA 4–8 GB), then re-check.

## Reusable PowerShell probes
```powershell
Get-CimInstance Win32_VideoController | Select VideoModeDescription,CurrentRefreshRate,CurrentScanMode
Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID        # real model name
Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorConnectionParams   # cable type
Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorListedSupportedSourceModes  # EDID native modes
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Display'} -MaxEvents 5   # TDR 4107
Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory,TotalVisibleMemorySize   # swap check
```
