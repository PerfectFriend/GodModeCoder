# Telegram Gateway — worked session (2026-08-03)

Real end-to-end setup on Windows (Hermes desktop, git-bash). Everything below is what actually ran and worked.

## Environment facts

- Real Hermes home: `C:\Users\tomas\AppData\Local\hermes` (config.yaml, .env, skills/, logs/).
- `$HOME/.hermes` = `C:\Users\tomas\.hermes` — a DIFFERENT directory Hermes does not read.
- Python on PATH was a Microsoft Store stub (`python3`/`python` not found in bash); used `python` from git-bash only for a small regex edit — prefer `uv run python` or plain sed-equivalent edits.

## Wrong turn (do not repeat)

`hermes config set gateway.telegram.bot_token "<token>"` → saved with warning:
`⚠ 'gateway.telegram.bot_token' is not a recognized config key — it was saved anyway, but Hermes may not read it.`
That key is dead weight; removed with `hermes config unset gateway.telegram.bot_token`.

## Correct sequence (verified working)

```bash
# 1. Enable platform
hermes config set platforms.telegram.enabled true

# 2. Fill .env (uncomment template lines via regex)
cd /c/Users/tomas/AppData/Local/hermes && python -c "
import re
with open('.env', 'r', encoding='utf-8') as f: c = f.read()
c = re.sub(r'^# TELEGRAM_BOT_TOKEN=.*$', 'TELEGRAM_BOT_TOKEN=<token>', c, flags=re.M)
c = re.sub(r'^# TELEGRAM_ALLOWED_USERS=.*$', 'TELEGRAM_ALLOWED_USERS=<user_id>', c, flags=re.M)
with open('.env', 'w', encoding='utf-8') as f: f.write(c)
"

# 3. Run gateway in background (terminal tool, background=true)
hermes gateway run

# 4. Verify
hermes gateway status          # ✓ Gateway is running (PID: ...)
tail logs/gateway.log          # ✓ telegram connected / Gateway running with 1 platform(s)
curl -s https://api.telegram.org/bot<TOKEN>/getMe   # HTTP 200
```

## Log signatures of success

```
INFO gateway.run: Connecting to telegram...
WARNING ...adapter: [Telegram] Discovering Telegram API fallback IPs via DNS-over-HTTPS…
INFO ...adapter: [Telegram] Auto-discovered Telegram fallback IPs: 149.154.166.110
WARNING ...adapter: [Telegram] Connecting to Telegram (attempt 1/8)…
INFO ...adapter: [Telegram] Connected to Telegram (polling mode)
INFO gateway.run: ✓ telegram connected
INFO gateway.run: Gateway running with 1 platform(s)
INFO ...adapter: [Telegram] set_my_commands OK ... (57 cmds)
```

Notes:
- Connect took ~14 s between "attempt 1/8" and "Connected" — that delay is normal (fallback-IP discovery + first poll).
- The gateway process in background mode buffers console output; the authoritative progress view is `logs/gateway.log`.
- Windows auto-start available via `hermes gateway install` (Scheduled Task); manual `hermes gateway run` dies with the terminal.
- Channel directory was `0 target(s)` at boot — TELEGRAM_HOME_CHANNEL not set yet; user messaging the bot is the live test.
