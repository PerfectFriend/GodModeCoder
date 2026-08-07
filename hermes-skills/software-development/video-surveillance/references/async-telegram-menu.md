# Async Telegram Bot Menu Updates — Never Block the Poll Loop

**Problem**: `set_bot_menu()` makes 5 sequential HTTP calls to Telegram (3×deleteMyCommands + setMyCommands + setChatMenuButton). Called synchronously from `/setlocal` handler, a slow network blocked `getUpdates` for up to ~75 seconds — every command the user sent in that window was silently ignored. Bot was RUNNING but appeared "dead".

**Root cause**: Synchronous HTTP calls in the update handler path. The poll loop processes updates sequentially; any blocking call in a handler freezes the entire bot.

**Solution**: Always run menu updates in a separate daemon thread. Never call synchronous Telegram API methods from the poll loop.

## Code Pattern (from panic_mode.py)

```python
def set_bot_menu():
    """Menu button next to the paperclip: commands for auto mode, alarm control,
    zone targeting, target description and interface language.
    Menu follows the bot language chosen via /setlocal (NOT the Telegram
    client language), so language_code variants are removed first.
    Runs in its own thread - Telegram calls here must NEVER block the poll
    loop (a slow network used to freeze the bot for up to 75s)."""
    # drop any per-client-language command sets previously registered
    for lc in ("ru", "es", "en"):
        try:
            tg("deleteMyCommands", data={"language_code": lc})
        except Exception as e:
            print(f"  delMyCommands {lc} err: {e}", flush=True)
    # single default set in the bot's current language
    try:
        tg("setMyCommands", data={"commands": _commands_payload(LANG)})
    except Exception as e:
        print(f"  setMyCommands err: {e}", flush=True)
    try:
        tg("setChatMenuButton", data={"chat_id": CHAT_ID,
                                      "menu_button": json.dumps({"type": "commands"})})
    except Exception as e:
        print(f"  setMenuButton err: {e}", flush=True)

def set_bot_menu_async():
    threading.Thread(target=set_bot_menu, daemon=True).start()
```

## Critical Rules

1. **`set_bot_menu_async()`** — ONLY entry point from handlers (`/setlocal`, startup)
2. **Every call individually try/except'd** — one failure doesn't cascade
3. **`tg()` timeout cut to 8s** (was 15s) — fail fast on slow network
4. **Per-update isolation in poll loop**:
   ```python
   for upd in j["result"]:
       try:
           _handle_update(upd)
       except Exception as e:
           print(f"  update err: {e}", flush=True)
   ```
   One network error on one command neither kills the loop nor skips remaining updates.

## When to Suspect This Issue

- User says "bot not responding / died" but process shows `running`
- Commands sent during language switch are ignored
- No traceback, no crash — just silence for tens of seconds
- Check: `set_bot_menu()` or any Telegram API call in the update handler path

## PITFALL — `language_code` scheme DOES NOT WORK for per-user language

First version pushed three `setMyCommands` variants with `language_code` (en default + ru + es) expecting each client to see their language. **Reality**: Telegram resolves `language_code` sets by the CLIENT'S APP UI LANGUAGE, NOT the bot's `/setlocal` choice. A Russian-UI client saw Russian menu even after bot was set to Spanish.

**Fix shipped**: `deleteMyCommands` the ru/es/en variants first, then ONE default `setMyCommands` in the bot's current `LANG` — menu follows `/setlocal` exactly, re-pushed on every language switch via `set_bot_menu_async()`.