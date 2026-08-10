# BIOS UMA/VRAM tuning + "can this app use the GPU?" binary scan (Beelink SER9 / AMD iGPU)

Proven 2026-08 on Beelink SER9 (AZW), Ryzen 7 255 (Hawk Point, Zen 4), Radeon 780M, 24 GB LPDDR5.

## Why UMA is a balance, not "max it out"

- The 780M iGPU shares system RAM. Vulkan already sees ~13.6–15 GiB GPU-accessible heaps
  (measured: 9.09 + 4.55 + 0.25 GiB) even with a small UMA reservation.
- Windows `AdapterRAM` (~4 GB) is only the BIOS UMA Frame Buffer — NOT the GPU ceiling.
- **Measured result of UMA=16 GB on 24 GB box:**
  - Vulkan heaps grew to 15.75 + 3.89 + 0.25 ≈ 20 GiB (marginal gain for LLM).
  - Windows visible RAM collapsed 20 → 8 GB, free dropped to 0.8 GB → swap thrash.
  - CPU-side TTS (Voicebox Qwen3-TTS 1.7B, needs ~8 GB) starved.
  - qwen3:8b went 14 → ~16.7 tok/s (small win, not worth the RAM loss).
- **Recommendation: UMA = 4–8 GB** on a 24 GB machine. The GPU still gets ~15 GiB of
  shared heap; the OS and CPU workloads keep their RAM.

## BIOS walkthrough (AMI Aptio on SER9)

1. Full shutdown (not restart — Fast Startup), power on, tap `Del` repeatedly.
   Fallbacks: `F7` (boot menu), `F2`. Reliable from Windows:
   Settings → System → Recovery → Advanced startup → Restart now →
   Troubleshoot → Advanced options → UEFI Firmware Settings.
2. `Advanced → AMD CBS → NBIO Common Options → GFX Configuration`:
   - `Integrated Graphics Controller` = `Forces`
   - `UMA mode` = `UMA_Specified`  (NOT Auto — Auto can black-screen / require CMOS reset)
   - `UMA Frame Buffer Size` = manual value (4–8 GB recommended)
3. NPU check (usually pointless on Ryzen 7 255 — the XDNA block is fused off):
   look in `AMD CBS → CPU Common Options` / `Platform` / `SMU Common Options`
   for an NPU/IPU toggle. If absent, the die simply has no NPU.
4. `F10` → Save & Exit.
5. Verify after boot: `vulkaninfo` heaps grew, Windows RAM shrank — check
   `Get-CimInstance Win32_OperatingSystem` TotalVisibleMemorySize/FreePhysicalMemory.

## Technique: does a compiled AI app support GPU? Scan the binary

PyInstaller/Nuitka-packaged `*.exe` contain the runtime DLL names as plain strings.
```python
data = open('voicebox-server.exe','rb').read()
for pat in [b'torch_cpu.dll', b'torch_cuda.dll', b'torch_vulkan', b'torch_directml',
            b'DirectML.dll', b'vulkan-1.dll', b'onnxruntime-directml',
            b'DmlExecutionProvider', b'CUDAExecutionProvider', b'VulkanExecutionProvider']:
    print(pat.decode(), '->', data.count(pat))
```
- `torch_cpu.dll` present, GPU DLLs absent → CPU-only build; no device flag will help.
- Beware false positives: `cuda` substrings can be `numba.cuda` (JIT lib, not GPU accel).
- Also check CLI: `voicebox-server.exe --help` exposes only host/port/data-dir — no device
  switch on the CPU-only build.
- PyInstaller magic (`MEI\x14\xce\xfa\x9e`) may be absent for Nuitka/other packers —
  the DLL-string scan works regardless.
- Applies to any bundled AI tool (Voicebox verdict: CPU-only, needs ~8 GB RAM per 1.7B model).

## Related
- `npu-and-hardware-diagnosis.md` — determining NPU existence (PnP enumeration, kipudrv.inf).
- `voicebox-api.md` — Voicebox API quirks (SSE status, model warm-up).
