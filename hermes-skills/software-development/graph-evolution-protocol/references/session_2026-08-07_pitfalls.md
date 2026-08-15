# Session 2026-08-07: Key Operational Pitfalls Discovered

## Telegram Gateway Polling Conflict
- **Problem**: Restarting Hermes gateway causes `Conflict: terminated by other getUpdates request` - previous session holds `getUpdates` on Telegram servers
- **Root cause**: Telegram allows only one long-polling connection per token. Previous process didn't cleanly release connection.
- **Resolution**: Wait ~100s (5 retries × 20s) for session to expire, OR use `--replace` flag: `hermes gateway run --replace`
- **Check status**: `hermes gateway status` shows PID if running, "No gateway process detected" if not

## Token Masking in .env Files
- **Observation**: Tokens in `.env` files appear as `***` in logs/output
- **Reason**: Hermes masks tokens in logs for security. Real token loaded from process environment at runtime
- **Pitfall**: Don't read `.env` directly with `read_file` — Hermes blocks direct credential store access
- **Correct approach**: Use `hermes_cli` tools or process environment variables. Real token is in process env, not file.

## Windows bash/MSYS Path Handling
- **Problem**: `cd /d C:\path` doesn't work in bash/MSYS
- **Solution**: Use `cmd /c "cd /d C:\path && command"` or `powershell -Command "cd 'C:\path'; command"`

## Telegram Bot Token Management
- **15 bots created** with isolated gateways, each with own token, DB, cron settings
- **Only ONE bot should have CRON_ENABLED=true** (main/Cathedral) to avoid duplicate cron jobs
- **SuperGuard token**: Needs real token from `sguard.env` (8711875181:***)

## DJ On-Air Verification
- **Check**: `curl -s http://localhost:8090/radio | head -c 100` — should return MP3 stream header
- **DJ status**: Running on port 8090, PID 29180 (background process)

## Pulse Dead Nodes - Honest Reporting
- **Rule**: Dead nodes must be reported honestly. Not running = DEAD, not "unknown"
- **Current pulse**: 4/8 alive (dj, watchdog, radio_cache, superguard alive; gardener, music_pipeline, voice, isle_client dead)
- **Dead nodes are normal** when services aren't running — don't fake status

## Windows tasklist Encoding
- **Issue**: `tasklist` output is cp866 (OEM), not UTF-8
- **Fix**: Decode with `decode("cp866", errors="ignore")` or use PowerShell `Get-CimInstance Win32_Process`

## DJ Service Details
- **Process**: `scripts/dj.py` running on port 8090
- **PID**: 29180 (background, notify_on_complete)
- **Playlist**: Currently only news blocks (cache has no music yet)
- **Warning**: `silence_header.mp3` was missing, generated via ffmpeg

## Gateway Process Management
- **Main gateway**: PID 4488 (Cathedral), running since 22:00:38
- **DJ process**: PID 29180 (started 00:22:25)
- **Total python processes**: 6 running
- **Scheduled tasks**: 15 registered, 1 running (main gateway)

## Resource Projections (15 bots)
| Metric | Projected |
|--------|-----------|
| RAM (Working Set) | ~291 MB |
| Private Memory | ~1.6 GB |
| Virtual | ~65 GB (reserved, not RAM) |
| % of 24 GB | ~8% |

## Next Actions Needed
1. Start music_pipeline (`gen_music.py`)
3. Start voice service (`gen_voice_content.py`)
4. Add health endpoint on :8080 for gardener
4. Insert real SuperGuard token
5. `Start-ScheduledTask -TaskName "Hermes-Gateway-*"` for all 15
6. Install Flutter for isle_client