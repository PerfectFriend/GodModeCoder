---
name: superguard-alarm
description: Deploy/evolve SuperGuard Alarm bot — AI video surveillance.
---

# SuperGuard Alarm — Autonomous AI Security Service

**Trigger**: Deploy, configure, debug, or evolve the SuperGuard Alarm bot (panic_mode.py) on Windows.

---

## Project Structure

```
C:\SuperGuard\ (production)
C:\Users\tomas\AppData\Local\Temp\xfetch\ (dev)
├── panic_mode.py          # Main bot (~1100 lines)
├── sguard.env             # Secrets (token, chat_id, plug IP, local_key) — NEVER COMMIT
├── sguard_settings.json   # Persisted zone/target/lang/auto/camera
├── requirements.txt       # opencv-python, ultralytics, tinytuya, requests, psutil, numpy
├── setup_autostart.ps1    # NSSM Windows service installer (run as Admin)
├── install_superguard.ps1 # Full installer for fresh machine
├── evolution_cycle.py     # Autonomous evolution: tests, debug, USB backup, Telegram report
├── README.md / .ru.md / .es.md  # 3 languages with banners
├── assets/
│   ├── banner-header.png
│   └── banner-footer.png
└── actuators/             # Phase 1: TuyaActuator, SonoffActuator, ShellyActuator, ESPHomeActuator, ZigbeeActuator
```

---

## Key Commands

### Bot Commands (Telegram menu)

| Command | Description |
|---------|-------------|
| `/autoguard` | Toggle AUTO mode (plug OFF auto when target leaves) |
| `/togglealarm` | Manual alarm ON/OFF (plug ON, photo immediately, no YOLO) |
| `/zone` | Set zone: `N3x4 C9`, `N9 C5`, `off`, `?` |
| `/target` | Set target: `red car`, `white truck`, `person standing`, `?` |
| `/setlocal` | Interface language (RU/EN/ES) — inline buttons |
| `/cam` | Switch/list cameras: `/cam ?`, `/cam status`, `/cam main` |

### Local Dev

```bash
# Run directly
cd C:\SuperGuard
venv\Scripts\python panic_mode.py

# Run tests
python -c "import sys; sys.path.insert(0, r'C:\Users\tomas\AppData\Local\Temp\xfetch'); import evolution_cycle; ok, res = evolution_cycle.run_tests(); print(res)"

# Run evolution cycle (tests + debug + USB backup + Telegram report)
python -c "import sys; sys.path.insert(0, r'C:\Users\tomas\AppData\Local\Temp\xfetch'); import evolution_cycle; evolution_cycle.load_env(); evolution_cycle.run_cycle(1)"
```

---

## Windows Service (Auto-Start)

**Requires Administrator PowerShell:**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& 'C:\SuperGuard\setup_autostart.ps1' -InstallDir 'C:\SuperGuard' -ServiceName 'SuperGuardAlarm'
```

**What it does:**
- Installs NSSM to `C:\Program Files\NSSM\nssm.exe`
- Creates service `SuperGuardAlarm` with:
  - `SERVICE_AUTO_START` (starts on boot)
  - `AppExit Default Restart` (restart on crash)
  - `AppRestartDelay 5000` (5 sec delay)
  - `ObjectName "LocalSystem"` (network access)
  - Logs: `superguard.log`, `superguard_err.log`
- Adds firewall rules for Tuya plug port 6668

**Verify:**
```powershell
Get-Service SuperGuardAlarm
Get-Content C:\SuperGuard\superguard.log -Tail 20
```

---

## Multi-Camera Support

8 cameras configured in `CAMERA_URLS` / `CAMERA_NAMES`:
- `main` — Banjar PTZ (Indonesia) — currently active
- `cam_2`..`cam_8` — placeholders for London, NYC, Berlin, Tokyo, Sydney, Cape Town

**Alarm message includes camera:**
```
⚠️ ALARM!
📷 Camera: Main Camera (Banjar PTZ)
🔍 Looking for: car (any color)
📍 Zone: N3x3 C05
```

---

## Full i18n (RU/EN/ES)

- 48 i18n keys × 3 languages in `L` dict
- `/setlocal` → inline buttons (EN/ES/RU)
- `set_bot_menu()` registers commands for **all 3 languages** via `language_code` so users see menu in their Telegram client language
- `set_lang()` switches language on-the-fly + saves to `sguard_settings.json` (never touches target/zone/auto)
- `save_settings(persist_target=False)` on language switch prevents target resurrection bug

---

## Evolution Cycles

Cron: `superguard-evolution-2h` (Windows Task Scheduler, every 2 hours)

Each cycle:
1. **Tests** — syntax, i18n (39 keys), target_parse, graph
2. **Debug** — bot running, fallback config, OpenCode keys, USB drive
3. **USB Backup** — `D:\backups\superguard_cycle_XXX_YYYYMMDD_HHMMSS`
4. **Telegram Report** — sent to group/topic
5. **Version Badge** — increment (A00, A01...)

---

## Common Pitfalls

| Issue | Fix |
|-------|-----|
| Bot not responding | Token invalid (404 on getMe) — get new token from @BotFather for SuperGuardAlarmBot |
| 409 Conflict | Zombie python.exe holding long-poll — `kill_zombies.ps1` kills stale instances |
| `/setlocal` missing from menu | `set_bot_menu()` must register for all 3 languages via `language_code` |
| Target resurrects on lang switch | `save_settings(persist_target=False)` in `set_lang()` |
| Zone detection broken | `in_zone()` expects `W, H` order from `frame.shape[:2]` → `H, W` |
| Tuya plug not switching | Use `TuyaActuator` (tinytuya 3.4, fresh connection per command) |
| Service won't install | Must run PowerShell as Administrator |
| Camera init fails | Skip empty URLs in `CameraManager._init_all()` |

---

## GitHub Push Workflow

**Repo:** `PerfectFriend/AISuperGuard` (default branch: `main`)

1. Local prep: `git add . && git commit -m "msg" && git push origin main`
2. **Browser verify** (owner logged into Chrome):
   - Check `raw.githubusercontent.com/PerfectFriend/AISuperGuard/main/README.md`
   - Verify banners, language switcher, 3 READMEs
3. **Anti-patterns:**
   - ❌ Forget banners when rewriting README
   - ❌ Forget to update all 3 language READMEs
   - ❌ Push without checking raw.githubusercontent.com

---

## References

- `references/panic_mode_architecture.md` — Code structure and data flow
- `references/evolution_cycle_protocol.md` — Cycle phases and reporting format
- `references/nssm_service_config.md` — NSSM parameters and recovery settings