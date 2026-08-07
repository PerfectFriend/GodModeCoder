# ACE-Step 1.5 on AMD iGPU / CPU-only (proven 2026-08)

ACE-Step 1.5 (ace-step/ACE-Step-1.5, MIT) — open music foundation model (~Suno v4.5–v5 quality),
10 s–10 min tracks, 1000+ styles, 50+ languages. The Windows portable `.7z` ships a
pre-baked `python_embeded/` and `PortableGit/`, but the clean path on a machine that already
has uv is a dedicated CPU venv.

## Setup on CPU-only (AMD iGPU has no ROCm — see SKILL.md)

1. Extract the 2.4 GB archive (`py7zr` — no 7-Zip on Windows): `py7zr.SevenZipFile(...).extractall(path='extracted')` → 7.6 GB / ~57k files, ~12 min. Don't `du` the in-progress dir (hangs, exit 124).
2. The stock `requirements.txt` pins CUDA wheels on Windows: `torch==2.7.1+cu128` and a
   `flash-attn` URL for cp311-win. For CPU-only build a trimmed copy:
   ```bash
   sed 's/^torch==2\.7\.1+cu128.*/torch==2.7.1/; s/^torchvision==0\.22\.1+cu128.*/torchvision==0.22.1/; s/^torchaudio==2\.7\.1+cu128.*/torchaudio==2.7.1/' requirements.txt \
     | grep -v -- '--extra-index-url' | grep -v 'flash-attn' > requirements-cpu.txt
   ```
   (linux/darwin lines with `+cu128` are harmless — they're platform-gated.)
3. Create venv + install:
   ```bash
   uv venv .venv-cpu --python 3.11
   uv pip install --python .venv-cpu/Scripts/python.exe -r requirements-cpu.txt
   ```

## CRITICAL pitfall: PYTHONPATH pollution from the Hermes venv

The Hermes agent session exports `PYTHONPATH=C:\Users\...\hermes-agent;C:\...\hermes-agent\venv\Lib\site-packages`.
Any other venv started from that shell INHERITS it and imports the WRONG torch
(symptom: `torch.__version__` reports 2.13.0+cpu from the Hermes venv while the ACE venv
has 2.7.1; `torchaudio` then fails with `OSError: Could not load this library: libtorchaudio.pyd`).

Fix — always launch ACE-Step (and any other secondary venv) with the path envs cleared:
```bash
env -u PYTHONPATH -u VIRTUAL_ENV ./.venv-cpu/Scripts/python.exe ...
```
Same rule applies inside Python scripts that `subprocess.run` the CLI: `env.pop("PYTHONPATH", None)`.

## CLI + TOML config (config-driven, no wizard needed)

`cli.py -c config.toml` — the TOML keys are FLAT and map 1:1 to argparse Namespace fields
(from `acestep.inference.GenerationParams` / `GenerationConfig`):
```toml
task_type = "text2music"
caption = "эмбиент, атмосферные пэды, медленный темп"
instrumental = true
duration = 60
seed = -1
inference_steps = 8
device = "cpu"
backend = "pt"
thinking = false
use_adg = false
offload_to_cpu = true
offload_dit_to_cpu = true
save_dir = "C:\\Users\\...\\cache\\music\\ambient"
audio_format = "wav"
```

TOML gotchas that WILL bite:
- **Windows backslashes in paths are reserved escapes** — `save_dir = "C:\Users\..."` fails with
  `toml: Reserved escape sequence used (line N)`. Escape as `\\` (or use forward slashes) AND
  escape the caption's quotes/backslashes. Do this in the code that emits the TOML, not by hand.
- `seed = -1` means random seed each run.
- `instrumental = true` skips lyrics/vocals — right for radio beds.
- First run auto-downloads weights into `<ace-step>/checkpoints/` (DiT + LM ≈ several GB) — check
  `du -sh checkpoints` to watch progress; `cli.py` buffers output, so run in background and poll
  the checkpoints dir / process CPU rather than waiting on stdout.

## Usage for a radio cache (Мастер-ФМ pattern)

`gen_music.py --style <style> --duration 120` → emits a TOML per track, runs the CLI with the
cleared env, and drops WAVs into `cache/music/<style>/`. Styles come from a YAML map of
style-name → caption. CPU generation of 60 s ambient ≈ minutes; schedule it for idle hours.
