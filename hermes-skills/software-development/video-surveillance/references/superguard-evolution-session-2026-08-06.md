# SuperGuard Alarm Evolution Session — 2026-08-06

## Session Summary
Fixed and deployed SuperGuard Alarm bot (repo: PerfectFriend/AISuperGuard) with all critical fixes validated in production.

## Key Fixes Delivered

### 1. Zombie Killer at Startup
- MSYS `kill` only kills bash wrapper; `python.exe` survives long-polling
- Fix: `kill_other_instances()` using PowerShell WMI to find and kill other `panic_mode` python.exe processes
- Uses `psutil.Process().pid` to get actual python.exe PID (not bash wrapper)

### 2. Settings Persistence — load_settings() FIRST
- Race condition: `poll_loop` started before `load_settings()` → early commands saw defaults
- Fix: `load_settings()` is FIRST statement in `__main__`, before thread start
- File-overwrite race: old process `save_settings()` overwrites manual edits
- Correct sequence: kill ALL → edit JSON → start new process

### 3. Target-Driven Detection: /target Controls REAL Filter
- `parse_target(text)` tokenizes (ru/en/es) → returns `(TARGET_CLASSES, COLOR_RANGES)`
- Color words → HSV ranges from `COLOR_MAP` (11 colors, red = DUAL range 0-10 AND 170-180)
- Class words → YOLO classes `{0: person, 2: car, 5: bus, 7: truck}`
- Color only → all vehicle classes + that color
- Class only → that class, NO color filter
- Nothing recognized → keep current filter + localized message

**PITFALL — multi-range colors must be nested pairs (bot died 2026-08-06):**
```python
# WRONG (flat list - yellow worked, red crashed):
"red": [(0,100,80),(10,255,255),(170,100,80),(180,255,255)]

# CORRECT (list of pairs):
"red": [((0,100,80),(10,255,255)), ((170,100,80),(180,255,255))]
```

### 4. i18n: RU/EN/ES via /setlocal — Menu Follows Bot Language
- `tr(key, **kw)` with fallback chain `L[LANG] → L["ru"] → key`
- Static validation: `scripts/check_i18n.py` slices `L = {...}` literal, exec's it, diffs key sets across 3 languages (48 keys)
- **`language_code` scheme REVERTED**: Telegram resolves by CLIENT UI language, NOT `/setlocal`
- Fix: `deleteMyCommands` ru/es/en variants, ONE default `setMyCommands` in bot's `LANG`
- Re-push on every `/setlocal` via `set_bot_menu_async()`

### 5. Async Menu Updates — Never Block Poll Loop
- `set_bot_menu()` = 5 sequential HTTP calls → 75s freeze on slow network
- Fix: `set_bot_menu_async()` runs in daemon thread
- Every menu call individually try/except'd; `tg()` timeout cut to 8s

### 6. Per-Update Isolation
```python
def poll_loop():
    for upd in j["result"]:
        try:
            _handle_update(upd)
        except Exception as e:
            print(f"  update err: {e}", flush=True)
```
One network error on one command neither kills loop nor skips remaining updates.

### 7. Two-Message Alarm Flow (Audit-First)
1. **msg A** = trigger frame, caption "📷 кадр срабатывания", NO BUTTON, NEVER deleted (audit)
2. **msg B** = live frame ~1s later, caption "📺 живой кадр", refreshed every 2s, deleted on cancel
3. Cancel/Auto-resolve deletes ONLY msg B — msg A KEPT

### 8. Auto Mode — Auto-Resolve on 5 Clean Frames
- Toggle via `/autoguard` (menu button), always replies with current mode
- Track `clean` consecutive frames with 0 targets; `clean >= 5` → auto-resolve
- Plug OFF + delete msg B + single summary text with current mode/zone/target
- No separate status message; no "live frame deleted" line

### 9. Install Script for GitHub Deployment
`install_superguard.ps1` — one-command deploy on clean Windows (Python 3.12, NSSM, venv, deps, Windows Service, firewall)

### 10. GPU on AMD Radeon 780M — Windows ROCm 7.2 ONLY
WSL2 doesn't work, DirectML segfaults. Only working path:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm7.2
```

## Files in Repo (PerfectFriend/AISuperGuard)
```
panic_mode.py          # single-file bot (~1000 lines)
requirements.txt       # opencv-python ultralytics tinytuya requests psutil numpy
install_superguard.ps1 # Windows one-command installer
sguard.env.example     # template (DO NOT COMMIT REAL VALUES)
README.md              # English (default) — language switcher links in header
README.ru.md           # Russian — language switcher links in header
README.es.md           # Spanish — language switcher links in header
.gitignore             # secrets, logs, frames, __pycache__
test_i18n.py           # 48 keys × 3 langs validation
test_target_parse.py   # 11 parse_target cases
```

## Language Switcher Links in All READMEs
Every README has header:
```markdown
**[English](README.md) | [Русский](README.ru.md) | [Español](README.es.md)**
```

## Evolution Plan
Full roadmap in `EVOLUTION_PLAN.md` (14 weeks to production multi-device, multi-channel):
- Phase 1: Multi-Device Actuator Support (Week 1-2)
- Phase 2: Sonoff/Tasmota Support (Week 2-3)
- Phase 3: Shelly Support (Week 3-4)
- Phase 4: ESPHome/Zigbee/Matter (Week 4-5)
- Phase 5: DIY/Kincony (Week 5-6)
- Phase 6: WhatsApp Core (Week 6-7)
- Phase 7: WhatsApp Features (Week 7-8)
- Phase 8: Unified Config/UI (Week 8-9)