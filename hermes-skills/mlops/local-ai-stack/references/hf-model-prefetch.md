# HuggingFace Hub model prefetch (2026) — reliable recipe

Forced by: Voicebox's built-in loader hangs forever on flaky links with
`ChunkedEncodingError` / `IncompleteRead` and never reaches `model_loaded:true`.
Prefetch the model yourself, then let the app pick up cached files.

## CLI rename (breaking)
- `huggingface-cli` is DEPRECATED (2026). It now prints:
  `Warning: huggingface-cli is deprecated and no longer works. Use hf instead.`
- Use `hf` subcommand: `hf download <owner>/<repo>`.

## Correct invocation
- Resume is automatic. Do NOT pass `--resume-download` — it is not a recognized
  flag (`hf` suggests `--force-download` / `--no-force-download`).
- Use `--force-download` to bypass cache and re-pull.

## hf_transfer (Rust accelerator) for multi-GB fetches
Despite the env flag name, the package `hf_transfer` is NOT always installed:
```
uv pip install hf_transfer        # install first
HF_HUB_ENABLE_HF_TRANSFER=1 HF_HUB_DOWNLOAD_TIMEOUT=0 hf download <owner>/<repo>
```
If `ModuleNotFoundError: No module named 'hf_transfer'` appears, the flag was
silently ignored and the download falls back to the fragile loader.

## Concurrent-downloader lock deadlock
If BOTH an `hf download` process AND Voicebox's own loader grab the same repo,
they deadlock on `~/.cache/huggingface/hub/.locks/` — blob size stalls at the
same byte for minutes.
Fix: kill one downloader, `rm -rf ~/.cache/huggingface/hub/.locks`, rmdir it,
then let a SINGLE downloader run to completion.

## Prefer the small sibling model
When a model keeps getting connection-reset mid-transfer, check for a smaller
variant rather than fighting the big one. Qwen3-TTS ships 0.6B / 1.7B /
1.7B-CustomVoice — the 0.6B fits and is CPU-friendly.

## On flaky corporate/roaming Wi-Fi
- Speed may be ~4 Mbit/s even when "connected" — verify real throughput with
  `curl -s -o /dev/null -w "%{speed_download}" --max-time 10 <url>` before
  assuming bandwidth.
- DNS can transiently fail during network handoff (`no such host`). `ipconfig
  /flushdns` + retry usually clears it. Re-running a pull/download is safe
  (resume is automatic).