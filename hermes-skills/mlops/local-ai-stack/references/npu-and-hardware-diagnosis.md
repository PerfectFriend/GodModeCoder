# NPU & Hardware Diagnosis on AMD Mini-PCs (proven 2026-08, Beelink SER9 / Ryzen 7 255)

Goal: answer "does this AI-marketed mini-PC actually have an NPU, and what is the real
performance lever?" without guessing. Full working transcript from a session on a
Beelink SER9 (AZW, `BIOS SER9L105`).

## 1. Identify the exact machine and chip

```powershell
Get-CimInstance Win32_ComputerSystem | Select Manufacturer,Model          # AZW / SER9
Get-CimInstance Win32_BIOS | Select SMBIOSBIOSVersion                     # SER9L105
Get-CimInstance Win32_Processor | Select Name,NumberOfCores,MaxClockSpeed # AMD Ryzen 7 255 w/ Radeon 780M, 8C/16T, 3.8 GHz
Get-CimInstance Win32_Processor | Select Family,Model                     # AMD64 Family 25 Model 117
```

Decode: **Family 25 Model 117 (0x75) = Hawk Point (Zen 4)** — the refresh of 8845HS/8745HS
silicon. (Strix Point / Krackan Point / Zen 5 have different model numbers and DO carry
XDNA2 NPUs; Hawk Point's XDNA1 NPU is optional silicon and Beelink routinely ships it
fused off.)

## 2. Check whether an NPU actually enumerates (the decisive test)

```powershell
# XDNA / XDNA2 NPUs appear as VEN_1022 & DEV_1502 / DEV_17F0 (per AMD kipudrv.inf)
Get-PnpDevice | ? { $_.InstanceId -match 'VEN_1022&DEV_1(502|7F0)' }
# → EMPTY = NPU is absent at the silicon/BIOS level. No driver can materialize it.
```

Supplementary evidence:
- The AMD NPU driver is installed but idle: `reg query HKLM\SYSTEM\CurrentControlSet\Services\IpuMcdmDriver`
  → `ImagePath ...\DriverStore\FileRepository\kipudrv.inf_amd64_*\ipustack.sys`; its INF declares
  `PCI\VEN_1022&DEV_1502` and `PCI\VEN_1022&DEV_17F0`. Driver present + device absent = fused-off NPU.
- No unknown/problem devices that could be a sleeping NPU: `Get-CimInstance Win32_PnPEntity | ? { $_.ConfigManagerErrorCode -ne 0 }` → only USB/HID/monitor noise.
- External confirmation (2026-08): notebookcheck Ryzen 7 255 — *"An NPU for AI acceleration is not installed / activated"*; Guru3D SER9 review — *"lacks a dedicated NPU"*; Reddit/Beelink — same pattern on SER8 (8745HS = "8845HS without the Ryzen AI NPU").

## 3. What you actually have to work with

```powershell
vulkaninfo --summary          # deviceName = AMD Radeon 780M Graphics; Integrated GPU
vulkaninfo | grep memoryHeaps # 3 heaps: 9.09 GiB + 4.55 GiB + 256 MiB ≈ 13.6 GiB GPU-accessible
Get-CimInstance Win32_VideoController | Select AdapterRAM   # ≈ 4 GB = BIOS UMA allocation, NOT the ceiling
```

- RAM: 20 GB visible of 24 GB physical (GPU reserve / Windows overhead).
- The iGPU is the real compute: Radeon 780M (RDNA3, 12 CU) via Vulkan ≈ 2.9 TFLOPS FP16.
- **BIOS UMA Frame Buffer (Del at boot) is the main speed lever** — raising it from the
  default (~4 GB) toward 8–16 GB lets larger model layers live in GPU memory instead of
  spilling to CPU. This is the single most useful BIOS change for LLM speed on this box.
- Zen 4 = AVX-512 available (helps CPU-side TTS/STT work; check with `coreinfo` or a CPUID probe).

## 4. Reddit research via pullpush API (no browser needed)

Reddit blocks plain curl; `api.pullpush.io` serves searchable JSON without auth:

```bash
curl -sL "https://api.pullpush.io/reddit/search/submission/?subreddit=BeelinkOfficial&q=NPU&size=10"
```

This surfaced the 8745HS-vs-8845HS "no NPU" Beelink pattern and SER9 HX 370 launch posts.
DuckDuckGo HTML (`html.duckduckgo.com`) works with a browser UA but returns ads/noise for
vendor questions; Bing search pages need JS. TechPowerUp URL slugs for CPUs are unreliable —
prefer notebookcheck (full spec tables in static HTML).

## Verdict pattern for AI-marketed mini-PCs

1. "AI PC" marketing ≠ NPU present. The 50-TOPS NPU claims usually refer to the *top* config
   of the same model line (SER9 + Ryzen AI 9 HX 370); the budget config (Ryzen 7 255) keeps the
   case, loses the NPU.
2. Driver presence (kipudrv.inf / IpuMcdmDriver) is installed by Adrenalin for ALL AMD chips —
   never conclude "NPU exists" from the driver alone; check PnP enumeration.
3. Don't chase a BIOS toggle for a fused-off block. Redirect effort to the levers that exist:
   UMA/VRAM allocation, Vulkan layer offload (`OLLAMA_GPU_LAYERS=99`), AVX-512 builds.
