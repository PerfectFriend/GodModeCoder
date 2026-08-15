---
name: hermes-gateway-setup
description: "Configure Hermes messaging gateways: bot tokens, verify."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Hermes, Gateway, Telegram, Messaging, Setup, Configuration]
---

# Hermes Gateway Setup (Messaging Platforms)

Wire Hermes to messaging platforms (Telegram, Discord, Slack, WhatsApp, ...) via the gateway: bot tokens, platform enablement, verification, auto-start. Worked example uses Telegram; other platforms follow the same shape.

## Trigger

User wants the agent reachable on a messaging platform, provides a bot token + user id, says "connect the bot", "set up feedback via Telegram", "настрой обратную связь через телеграм", etc.

## Core rules

- **Secrets go in `.env`** (`<hermes_home>/.env`), settings in `config.yaml`. Never store a bot token in config.yaml: `hermes config set gateway.telegram.bot_token ...` is NOT a recognized key — Hermes saves it with a warning and nothing reads it.
- **`.env` ships with commented template lines** (`# TELEGRAM_BOT_TOKEN=...`) — uncomment/fill those instead of appending new keys. Grep the template first: `grep -i "telegram" <hermes_home>/.env`.
- **Find the REAL Hermes home first** — on Windows it is NOT `$HOME/.hermes` (see Pitfalls). Editing the wrong `.env` makes the gateway read a stale token silently.

## Steps (Telegram example)

1. Resolve the real Hermes home (see Pitfalls).
2. Edit `<hermes_home>/.env`:
   - `TELEGRAM_BOT_TOKEN=<token from @BotFather>`
   - `TELEGRAM_ALLOWED_USERS=<numeric user id>` — comma-separated for several; restricts who can talk to the bot. Without this the bot answers anyone (or no one, depending on config).
   - Optional: `TELEGRAM_HOME_CHANNEL`, `TELEGRAM_HOME_CHANNEL_NAME`, `TELEGRAM_CRON_THREAD_ID`, `TELEGRAM_WEBHOOK_URL/PORT/SECRET` (setting a webhook URL switches from long polling to webhook mode).
3. Enable the platform: `hermes config set platforms.telegram.enabled true`
4. Start the gateway: `hermes gateway run` (background). First connect can take ~15s — the adapter discovers fallback IPs via DNS-over-HTTPS and retries ("attempt N/8"); this is normal, give it time.
5. Verify:
   - `hermes gateway status` → `✓ Gateway is running (PID: ...)`
   - `<hermes_home>/logs/gateway.log` → look for `✓ telegram connected` and `Gateway running with 1 platform(s)`, plus `set_my_commands OK` (57 commands registered).
   - Token sanity: `curl -s https://api.telegram.org/bot<TOKEN>/getMe` → HTTP 200.
6. Windows auto-start on login: `hermes gateway install` (Scheduled Task). A manually started gateway dies with the terminal.
7. Ask the user to message the bot — end-to-end proof.

## Undoing mistakes

- `hermes config unset <key>` removes a wrongly-set config key.

## Pitfalls

- **Wrong config key**: token belongs in `.env` as `TELEGRAM_BOT_TOKEN`, never in config.yaml (`gateway.telegram.bot_token` is unrecognized — the config-set warning is the tell).
- **Windows Hermes home**: `$HOME/.hermes` is NOT the Hermes home on Windows. The real home is `%LOCALAPPDATA%\hermes` (config.yaml, .env, skills/, logs/ all live there). Resolve it (e.g. where `hermes config set` reports writing, or `ls %LOCALAPPDATA%\hermes`) before touching `.env` — otherwise the token silently does nothing. Same trap applies to installing skills into `$HOME/.hermes/skills` (see grimoire-self-replication).
- **Background-output illusion**: `hermes gateway run` in background buffers its console — if it looks stuck on "Connecting...", read `logs/gateway.log`; it may already be connected.
- **Never echo full tokens** in replies — Hermes redacts secrets, and you should too (mask: `8883...-HMg`).
- **Network/region**: when api.telegram.org is slow or blocked, the adapter auto-discovers fallback IPs via DNS-over-HTTPS and retries up to 8 attempts. Don't debug until attempts exhaust.
- **Long-polling conflict**: if running a Bot API moderation script (e.g. trashclean via cron) alongside the gateway, both use `getUpdates` — only one receives each update. Switch gateway to webhook mode (`TELEGRAM_WEBHOOK_URL`) or accept missed messages. **See `references/telegram-moderation.md` for detailed conflict resolution, 409 troubleshooting, and the 2026-08-04 session fix.**

## Support files

- `references/telegram.md` — worked session: exact .env edits, log signatures, verification output.
- `references/telegram-moderation.md` — Bot API moderation (trashclean): group ID discovery from gateway logs, cron setup, long-polling conflict with gateway, TELEGRAM_ALLOWED_USERS vs direct API behavior.
- `references/cathedral-master-bot.md` — CathedralMaster_bot (Hermes gateway): token in `.env` as `TELEGRAM_BOT_TOKEN=8883...`, `TELEGRAM_ALLOWED_USERS=143293811`, `TELEGRAM_HOME_CHANNEL=143293811`, used for cron deliveries and evolution reports. Gateway status via `hermes gateway status`, logs in `<hermes_home>/logs/gateway.log`.
- `references/gateway-startup-windows-issues.md` — Windows startup problems: VBS script hardcoded paths, unclean shutdown polling conflicts, health check recommendations.
