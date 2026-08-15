# panic_mode.py Architecture

## Code Structure (~1100 lines)

### Global State
- `ZONE` — tuple (rows, cols, cell) or None (whole frame)
- `TARGET_DESC` — free-text target description
- `TARGET_CLASSES` — set of YOLO class IDs to detect
- `COLOR_RANGES` — list of HSV (lo, hi) tuples for color filter
- `LANG` — current language code (ru/en/es)
- `alarm` — Alarm class instance (thread-safe)

### Key Classes
- **Alarm** — state machine (active/auto/trigger_msg_id/live_msg_id/control_msg_id)
- **Camera** — background thread capturing frames from URL
- **CameraManager** — manages 8 cameras, active camera switching
- **TuyaActuator** — plug control via tinytuya 3.4

### Main Loops
1. **poll_loop()** — Telegram long-poll (25s timeout), per-update isolation
2. **detection_loop()** — YOLO inference every DETECT_EVERY (1.5s)
3. **update_loop()** — live frame update every UPDATE_EVERY (2s) during alarm

### Critical Functions
- `in_zone(zone, box, W, H)` — **W/H order matters** (frame.shape[:2] gives H,W)
- `detect_vehicles(frame)` — YOLO + zone filter + color fraction
- `trigger_alarm(desc, frame)` — msg A (trigger, no buttons, eternal) + msg B (live, 2s, auto-delete)
- `stop_alarm(clear_chat, note)` — plug OFF, deletes msg B, keeps msg A
- `set_bot_menu()` — registers commands for ALL 3 languages via language_code
- `set_lang(code)` — switches language, saves settings (persist_target=False)
- `save_settings(persist_target)` — JSON persistence
- `load_settings()` — FIRST in __main__, restores zone/target/lang/auto/camera

### i18n System
- `L` dict: 48 keys × 3 languages
- `tr(key, **kw)` — translates with fallback to RU
- All bot messages built via `tr()` — no hardcoded text

### Zombie Protection
- `kill_other_instances()` — PowerShell kills other python.exe panic_mode processes
- Runs BEFORE load_settings() in __main__

### Actuator Abstraction (Phase 1)
- `BaseActuator` (ABC) — turn_on/turn_off/get_status/get_power
- `ActuatorRegistry` — factory pattern
- `TuyaActuator` — tinytuya 3.4 local control
- `SonoffActuator` — MQTT + HTTP (Tasmota)
- `ShellyActuator` — Gen1 CoAP/HTTP + Gen2/Plus WS/MQTT
- `ESPHomeActuator` — native API + MQTT fallback
- `ZigbeeActuator` — zigbee2mqtt/ZHA/deCONZ