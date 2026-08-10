# panic_mode.py — Single-File Autonomous AI Security Bot

**Verified working 2026-08-06** — all features integrated and tested.

This is the final shipped state of the SuperGuard Alarm bot. Key architecture decisions:

1. **Separate Telegram bot token** (root fix for 409 Conflict with Hermes gateway)
2. **Zombie killer at startup** — kills stale python.exe panic_mode on same token
3. **Settings persistence** — load_settings() FIRST in __main__, before threads
4. **Target-driven detection** — `/target` text parses to real YOLO class + HSV color filter
5. **i18n: RU/EN/ES via `/setlocal`** — menu follows bot language (NOT client UI language)
6. **Async menu updates** — set_bot_menu_async() never blocks poll loop
7. **Per-update isolation** — one network error doesn't skip remaining updates
8. **Two-message alarm flow** — msg A (trigger, no button, stays forever) + msg B (live, 2s refresh, deleted on resolve)
9. **Auto mode with 5-frame auto-resolve** — plug OFF automatically, minimal resolve text
10. **Grid zone targeting** — N×M cells, canonical syntax `N3x4 C9` (English `x`)
11. **Windows Service via NSSM** — auto-start, logs, restart on crash
12. **Windows ROCm 7.2 ONLY for AMD Radeon 780M** — WSL2/DirectML don't work

## Files in this repo

- `panic_mode.py` — single-file bot (~1000 lines)
- `test_i18n.py` — 48 keys × 3 langs validation (static slice of L dict)
- `test_target_parse.py` — 11 parse_target cases (static slice of parse_target + dicts)

## Tests

```bash
python test_i18n.py
python test_target_parse.py
```

Both tests use static source slicing (no module import → no YOLO/camera boot).