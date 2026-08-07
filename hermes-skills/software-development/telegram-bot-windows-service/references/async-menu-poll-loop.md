# Async Menu Updates — Timeout & Threading Pattern

## Problem
`setMyCommands` + `deleteMyCommands` ×3 languages = 5 sequential HTTP calls to Telegram API.
- Default timeout 15s × 5 = 75s potential block
- On slow networks (Spain → Telegram servers): frequent `Read timed out`
- **Poll loop frozen** for entire duration → bot "not responding"

## Solution: Background Thread + Reduced Timeout

### 1. Threaded Menu Update
```python
def set_bot_menu_async():
    threading.Thread(target=set_bot_menu, daemon=True).start()
```
Call from `set_lang()` instead of blocking `set_bot_menu()`.

### 2. Reduced Timeout
```python
def tg(method, **kwargs):
    r = requests.post(f"{API}/{method}", timeout=8, **kwargs)  # was 15
    j = r.json()
    if not j.get("ok"):
        print(f"  TG ERROR {method}: {j}", flush=True)
    return j.get("result")
```
8s timeout × 5 calls = 40s worst case, but **in background** so poll loop never freezes.

### 3. Per-Call Error Isolation
```python
def set_bot_menu():
    for lc in ("ru", "es", "en"):
        try:
            tg("deleteMyCommands", data={"language_code": lc})
        except Exception as e:
            print(f"  delMyCommands {lc} err: {e}", flush=True)
    try:
        tg("setMyCommands", data={"commands": _commands_payload(LANG)})
    except Exception as e:
        print(f"  setMyCommands err: {e}", flush=True)
    try:
        tg("setChatMenuButton", data={"chat_id": CHAT_ID,
                                      "menu_button": json.dumps({"type": "commands"})})
    except Exception as e:
        print(f"  setMenuButton err: {e}", flush=True)
```
One failed call doesn't block others.

## Per-Update Isolation (Complementary)
```python
for upd in j["result"]:
    try:
        _handle_update(upd)
    except Exception as e:
        print(f"  update err: {e}", flush=True)
```
One network error on one command doesn't lose subsequent commands in the same batch.

## Result
- Language switch: instant response, menu updates in background
- Poll loop: never blocked > 8s by Telegram calls
- Network errors: isolated, logged, bot continues
- User experience: bot always responsive