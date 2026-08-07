# Bulk model downloads on an APU workstation — operational discipline

Learned 2026-08 while pulling multiple multi-GB models (LLM + TTS + music) in
parallel over flaky Wi-Fi. The hard part is rarely the download itself — it is
knowing when it is actually progressing and not fighting your own restarts.

## Probe REAL progress — don't trust the tool's "list"

`ollama list` only shows fully-completed models; a download in-flight is absent
from it and lives as a `-partial` blob. The progress bar on `ollama pull` stderr
is only visible in a live terminal, not from a background process (you usually
see just "bash: no job control"). So measure the disk:

```bash
# biggest in-progress blob files (bytes):
ls -laS ~/.ollama/models/blobs/*-partial 2>/dev/null \
  | awk '{printf "%.2f GB %s\n", $5/1073741824, $9}'
# count remaining incomplete:
ls ~/.ollama/models/blobs/*-partial 2>/dev/null | wc -l   # -> 0 means done
```

Same idea for HuggingFace: `du -sh ~/.cache/huggingface/hub` grows on in-flight
downloads; a static size for 60s+ while a downloader claims to run means it is
stalled (check the `.locks/` deadlock case in `hf-model-prefetch.md`).

## "All background processes died at once" -> machine move/reboot, not a failure

The single most important triage. When EVERY background process (multiple
downloads, a TTS server, etc.) is suddenly gone with no individual error — and
especially if the same user later says they "moved the workstation / switched
the Wi-Fi / rebooted" — the cause was almost certainly the machine being shut
down or the network handing off, NOT that every tool independently broke.

Do exactly this:
1. Re-check the state of whatever is already on disk first (models survive a
   reboot in `~/.ollama/models`, HF blobs in `~/.cache/huggingface/hub`, an
   installed app in its dir). Most long work survives; it is a RESPUME, not a
   redo.
2. Re-launch every intended downloader once with resume + retry.
3. Walk away and let notify_on_complete fire — do not re-mount them repeatedly.

## Don't restart-hammer — it causes the very loops you are diagnosing

Mid-session I killed and relaunched the same three downloads multiple times,
chasing "why is it stalled". Each kill of an `ollama pull` on a reasoning model
was recorded as exit -15 (killed). Most such "stalls" were either (a) the
machine actually having been moved, or (b) genuinely slow ~4 Mbit/s throughput
(multiply bytes/min and look before judging). The disciplined pattern:

- Measure bytes/unit-time on the target file BEFORE killing anything.
- Launch ONE background worker per target, with `notify_on_complete`, resume
  enabled, and generous `--retry-all-errors` for curl.
- Never kill an in-flight `ollama pull` / `hf download` / curl on a hunch; let
  it finish or emit its own error.

## Fresh network handoff notes

- After plugging into a new Wi-Fi/different router, DNS can transiently fail
  (`dial tcp: lookup ... no such host` for Cloudflare R2 / ollama CDN) even
  though `nslookup` and `ping` then succeed. `ipconfig /flushdns` + retry clears
  it. Verify once, then relaunch.
- Real throughput, not "connected": `curl -s -o /dev/null -w "%{speed_download}"
  --max-time 10 <url>` — a strong network can still be ~4 Mbit/s capped.

## Killing an in-flight `ollama pull` WASTES the downloaded bytes

Verified 2026-08: killing a background `ollama pull` (exit -15) and re-running
it does NOT resume from the partial blob — Ollama re-pulls the manifest and can
RESTART the blob from zero (a 8.8 GB partial shrank to 3.5 GB after a kill+rerun
race with a competing process). Discipline: never kill a pull that is making
forward progress; if a SECOND downloader grabbed the same model, kill the
newcomer and let the original finish. `ollama pull` resumes cleanly only when
the process itself exits and the partial blob is intact.

## Two concurrent downloaders of the SAME model → blob shrinks / stalls

If two `ollama pull qwen3:14b` (or `hf download` + Voicebox loader) run at once,
blob size can REGRESS (8.8 GB → 3.5 GB) as manifests re-resolve and each writer
overwrites partial chunks. Symptom: partial file grows, then jumps backward.
Fix: keep exactly ONE downloader per model; verify with a second size sample
10–20 s later that size is monotonic non-decreasing before calling it stalled.