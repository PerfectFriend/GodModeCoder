# Settings persistence for the SuperGuard alarm bot (VALIDATED 2026-08-06)

Client requirement (verbatim): «настройки должны фиксироваться намертво до их
изменения пользователем вручную» — zone, target, language and auto-mode must
survive process restarts. A restart that silently resets them to whole-frame /
default-target was reported as a BUG: «почему настройки сбрасываются по
умолчанию на полный кадр и поиск желтого автомобиля? этого не должно
происходить».

## Design

JSON file `sguard_settings.json` NEXT TO the script (same dir as `sguard.env`):

```json
{
  "zone": [3, 3, 5],
  "target": "red car",
  "lang": "ru",
  "auto": true
}
```

- `zone`: `[rows, cols, cell]` (1-based cell) or `null` = whole frame.
- `target`: free text; empty string = not set by user yet.
- `lang`: `ru` | `en` | `es`.
- `auto`: auto-resolve mode on/off.

## Code

```python
SETTINGS_FILE = os.path.join(BASE, "sguard_settings.json")

def save_settings():
    with alarm.lock:
        auto = alarm.auto
    data = {"zone": list(ZONE) if ZONE else None,
            "target": TARGET_DESC,
            "lang": LANG,
            "auto": auto}
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  settings save err: {e}", flush=True)

def load_settings():
    global ZONE, TARGET_DESC, LANG
    if not os.path.exists(SETTINGS_FILE):
        return  # very first run -> defaults are correct
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            s = json.load(f)
        z = s.get("zone")
        if isinstance(z, list) and len(z) == 3:
            rows, cols, cell = int(z[0]), int(z[1]), int(z[2])
            if 1 <= cell <= rows * cols:
                ZONE = (rows, cols, cell)
        t = s.get("target")
        if isinstance(t, str) and t.strip():
            TARGET_DESC = t.strip()
        lg = s.get("lang")
        if lg in L:
            LANG = lg
        with alarm.lock:
            alarm.auto = bool(s.get("auto", False))
    except Exception as e:
        print(f"  settings load err: {e}", flush=True)
```

Call `save_settings()` at the END of every mutating handler: `_handle_zone_cmd`
(both set and off paths), `_handle_target_cmd`, `toggle_auto`, `set_lang`.

## Pitfall 1 — load order (real bug)

`load_settings()` must be the FIRST statement of `__main__`, BEFORE the
`poll_loop` thread starts. Original code started poll_loop → slept 2 s → loaded
settings; a command arriving in that window read defaults and replied
«весь кадр» even though a zone was configured. Symptom: «при переключении
режима неправильно выдается значение zone - весь кадр».

## Pitfall 2 — file-overwrite race (real bug)

While hand-editing `sguard_settings.json` to restore a lost zone, the OLD
script instance was still running; the client's live `/autoguard` tap made it
call `save_settings()`, overwriting the file back to `zone: null` — undoing
the manual edit. Sequence that works:

1. Kill ALL script instances (check zombies — see SKILL.md zombie section:
   `Get-CimInstance Win32_Process` may show several `python.exe -u panic_mode.py`).
2. THEN edit / write `sguard_settings.json`.
3. THEN start the new process.

Log line proves the fix: `settings loaded: zone=N3x3 C05 (строка 2, столбец 2)
target=red car lang=ru auto=True`.
