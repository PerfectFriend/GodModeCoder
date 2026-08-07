# Running Qwen3-TTS on the AMD iGPU via torch-directml (GPU path for Voicebox)

Voicebox's bundled `voicebox-server.exe` is CPU-only (torch_cpu.dll, no GPU backends)
and needs ~8 GB system RAM. The alternative that actually reaches the Radeon 780M
on Windows is PyTorch with the **Microsoft torch-directml** backend. Verified 2026-08
on Beelink SER9 (Ryzen 7 255 + Radeon 780M, Windows 11 + git-bash).

## Proven install: torch-directml from Microsoft's engine pool

`torch-directml` is NOT on PyPI. The official index is the DirectML Azure DevOps feed.
A Python 3.11 venv named `tts-dml-env` (created with the Hermes venv's python via
`python -m venv`) is the testbed:

```bash
cd /c/Users/tomas
env -u PYTHONPATH -u VIRTUAL_ENV ./tts-dml-env/Scripts/python.exe -m pip install \
  --extra-index-url https://pkgs.dev.azure.com/dnceng/public/_packaging/directml/pypi/simple/ \
  torch-directml
```

Result: installs `torch 2.4.1` + `torch-directml 0.2.5.dev240914` (+ torchvision, torchaudio
pulled explicitly if you add them). **Always launch with `env -u PYTHONPATH -u VIRTUAL_ENV`**
so the Hermes venv / hermes-agent torch in PYTHONPATH doesn't shadow this one.

## Proven GPU verification (works)

```bash
env -u PYTHONPATH -u VIRTUAL_ENV ./tts-dml-env/Scripts/python.exe -c "
import torch, torch_directml
print('torch', torch.__version__)
n = torch_directml.device_count()
print('DML devices:', n)
for i in range(n): print(' device', i, ':', torch_directml.device_name(i))
d = torch_directml.device()
a = torch.randn(1000,1000, device=d)
print('matmul ok:', round((a @ a).sum().item(),2))
"
```

On the 780M this prints `AMD Radeon 780M Graphics` with `matmul ok` — the backend
computes on the iGPU and is a real Vulkan/DirectML alternative. `device_map={"": dml}`,
`torch_dtype=torch.float16` is the intended usage for the TTS model.

## qwen_tts dependency chain (for a standalone GPU TTS, in progress)

To use Voicebox's own `qwen_tts` Python API standalone on this GPU you need:
- `qwen_tts` package: **it is inside the extracted PyInstaller temp dir** — after
  `voicebox-server.exe` runs, `%LOCALAPPDATA%\Temp\_MEI*/qwen_tts/` holds the full
  source. Copy it into the venv: `cp -r _MEI*/qwen_tts ./tts-dml-env/qwen_tts`. The
  HF repo `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` (already in `~/.cache/huggingface/hub`)
  holds weights; `Qwen3TTSModel.from_pretrained(MODEL_DIR, device_map={"": dml}, torch_dtype=torch.float16)`.
2. Deps for `qwen_tts`:
   `transformers==4.57.3` (NOTE: `4.46.4` from the Qwen README does NOT exist; 4.46.3 and
   4.57.x are real — use 4.57.3), `accelerate`, `librosa`, `soundfile`, `einops`, `torchaudio`.
3. Full offline-clone call path: `tts.create_voice_clone_prompt(ref_audio=wav, x_vector_only_mode=True)`
   → `tts.generate_voice_clone(text, language="ru", do_sample=True, max_new_tokens=2048, ...)`.

### Current blocker (2026-08): `sox` module

`qwen_tts/core/tokenizer_25hz/vq/speech_vq.py` does `import sox` at module load. Standard
pip `sox` is a thin binding that needs the **native libsox C library**, which Windows lacks
and which isn't bundled. This fails the existing test run short of generation. Options to try
next (none proven yet):
- `tts_dml-env/Scripts/pip install sox soxr` and see if a wheel with bundled libsox exists
  (soxr IS available; the `sox` binding itself is the question).
- VQ/whisper path may only need sox offline for resampling; ship a stub if never called.

**Additional blocker (2026-08-05): Insufficient system RAM for 1.7B model on CPU**

The 1.7B model (~3.8 GB fp16, ~7.6 GB fp32) cannot be loaded on this machine's 7.8 GB total RAM
(~1-2 GB available after OS/processes). `AutoModel.from_pretrained` with `low_cpu_mem_usage=True`
segfaults (exit code 139) during weight loading. **Workaround: use the 0.6B model**
`Qwen3-TTS-12Hz-0.6B-Base` (~1.5 GB fp16, ~3 GB fp32) which fits in available RAM.

**`torch.inference_mode()` incompatibility fix locations (confirmed 2026-08-05):**
Replace `@torch.inference_mode()` → `@torch.no_grad()` in:
- `qwen_tts/inference/qwen3_tts_model.py` line 355: `create_voice_clone_prompt`
- `qwen_tts/core/models/modeling_qwen3_tts.py` line 1940: `extract_speaker_embedding`
- `qwen_tts/core/models/modeling_qwen3_tts.py` line 1956: `generate_speaker_prompt`

These decorators cause "Cannot set version_counter for inference tensor" on DirectML.

Do NOT claim GPU TTS works until a full `generate_voice_clone` returns audio — the install
and device path above IS proven; the synth completion is NOT yet.

## RAM budget note

Qwen3-TTS 1.7B in fp16 ≈ 3.4 GB — fits the 780M's ~15-20 GiB GPU-accessible heap alongside
Ollama qwen3:8b (~6 GB). Freeing system RAM from Voicebox (~8 GB CPU) is what makes "8 GB
system RAM / everything neural in VRAM" achievable.