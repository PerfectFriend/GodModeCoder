# Language Switch Target Bug — Analysis & Fix

## Bug
User switches language via `/setlocal` → bot answers with **wrong target** (e.g., "red car" becomes "human").

## Root Cause
1. `set_lang()` calls `save_settings()` which writes **current in-memory `TARGET_DESC`** to `sguard_settings.json`
2. If a **zombie process** (stale python.exe from previous run) answers the `/setlocal` callback:
   - Zombie has old `TARGET_DESC` in memory (e.g., "human" from earlier session)
   - Zombie's `save_settings()` overwrites file with its stale target
3. Next restart loads the corrupted target

## Timeline of Corruption
```
Time 1: User sets /target "red car" → new process saves "red car" to file
Time 2: User clicks /setlocal → Telegram delivers callback to ZOMBIE (50/50)
Time 3: Zombie's set_lang() → save_settings() writes "human" to file
Time 4: User restarts bot → load_settings() reads "human" → target is wrong
```

## Fix: `persist_target=False` on Language Switch
```python
def save_settings(persist_target=True):
    data = {"target": TARGET_DESC, "lang": LANG, "zone": ..., "auto": ...}
    if not persist_target:
        # Read PREVIOUS target from disk, preserve it
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                prev = json.load(f)
            pt = prev.get("target")
            if isinstance(pt, str) and pt.strip():
                data["target"] = pt
        except Exception:
            pass
    # write data with preserved target...
```

## Usage
- `save_settings(persist_target=False)` — ONLY in `set_lang()`
- `save_settings()` (default `True`) — in `/target`, `/zone`, `/autoguard`, `toggle_auto`

## Why This Works
Language switch **only changes `LANG`** in settings. Target, zone, auto-mode are orthogonal and must never be overwritten by a language change — especially not by a zombie's stale memory.

## Prevention
Combined with zombie-killer (runs at `__main__` entry), the race window is eliminated:
1. New process kills zombies first
2. Then loads settings
3. Language switch preserves on-disk target