# SuperGuard Alarm — Autonomous Evolution (Session 2026-08-06)

## Session Summary
Restored SuperGuard Alarm bot from broken state, fixed critical bugs, added multi-camera support (8 cameras), integrated actuator abstraction, and deployed autonomous evolution cycle with Telegram reporting.

## Key Fixes Applied

### 1. Critical Bug: `global tuya_actuator` syntax error
**File**: `panic_mode.py` line 1011
**Error**: `SyntaxError: name 'tuya_actuator' is assigned to before global declaration`
**Fix**: Removed `global` keyword — simple module-level assignment works:
```python
# Before (broken)
global tuya_actuator
tuya_actuator = TuyaActuator({...})

# After (fixed)
tuya_actuator = TuyaActuator({...})
```

### 2. Critical Bug: W/H swap in `in_zone()`
**File**: `panic_mode.py` lines 637, 322-330
**Issue**: `H, W = frame.shape[:2]` (H=height, W=width) but `in_zone(ZONE, box, W, H)` passed swapped → `cx/W` divided by height instead of width
**Fix**: Corrected call order: `in_zone(ZONE, box, W, H)` where `W=width, H=height`

### 3. Camera unavailable on manual toggle
**Cause**: `CAM.latest()` returned `None` during first 2 seconds before camera thread initialized
**Fix**: Graceful handling in `toggle_alarm()` — if frame is None, send "cam_unavailable" message instead of crashing

### 4. Zombie process long-poll conflict
**Issue**: Old python.exe processes survived shell kill, kept Telegram long-poll → 409 Conflict
**Fix**: `kill_zombies.ps1` with dynamic PID (`$mypid = $PID`) + `kill_other_instances()` in `__main__` using psutil + PowerShell

### 5. OpenCode Zen duplicate keys (24→8 unique)
**Detection**: Compare key values from `hermes auth list opencode-zen`
**Removed**: 16 duplicate keys (3 pairs from master, 4 pairs from new, etc.)
**Result**: 8 unique keys (1 env + 7 master)

## Multi-Camera Support (8 cameras)

### Architecture
- **CameraManager**: Manages 8 Camera threads, tracks alive status
- **CAMERA_URLS**: Dict with 8 entries (1 real + 7 placeholders)
- **CAMERA_NAMES**: Human-readable names for all 8
- **/cam command**: List, status, switch cameras via Telegram

### i18n keys added (RU/EN/ES)
- `"camera": "Камера" / "Camera" / "Cámara"`
- `"cam_status": "Камера: {status}" / "Camera: {status}" / "Cámara: {status}"`

### Alarm message enhancement
**Before**: No camera info
**After**: Alarm messages include camera name:
```
📷 Камера: Main Camera (Banjar PTZ)
📸 кадр срабатывания
```

### /cam command
- `/cam ?` / `/cam list` — list all cameras with alive status (🟢/🔴)
- `/cam status` — detailed status
- `/cam <name>` — switch active camera
- `/cam <unknown>` — "Camera not found" with hint

## Actuator Abstraction (Phase 1)

### Structure
```
actuators/
├── __init__.py          # Auto-registers all types
├── base.py              # BaseActuator ABC + ActuatorRegistry singleton
├── tuya.py              # TuyaActuator (local control via tinytuya 3.4)
├── sonoff.py            # SonoffActuator (MQTT + HTTP for Tasmota)
├── shelly.py            # ShellyActuator (Gen1 CoAP/HTTP + Gen2 WS/MQTT)
├── esphome.py           # ESPHomeActuator (native API + MQTT)
└── zigbee.py            # ZigbeeActuator (zigbee2mqtt, ZHA, deCONZ)
```

### Registered types
```python
ActuatorRegistry.list_types()
# ['tuya', 'sonoff', 'tasmota', 'shelly', 'shelly_gen1', 'shelly_gen2', 
#  'esphome', 'zigbee', 'zigbee2mqtt', 'zha', 'deconz']
```

### Integration
```python
from actuators import TuyaActuator
tuya_actuator = TuyaActuator({"ip": PLUG_IP, "device_id": PLUG_ID, "local_key": PLUG_KEY, "version": 3.4})
plug_set(on) → tuya_actuator.turn_on()
```

## Autonomous Evolution Cycle

### Script: `evolution_cycle.py`
- **Tests**: syntax, i18n, target_parse, graph
- **Debug**: bot running, fallback config, opencode keys, USB drive
- **Backup**: Critical files → `D:\backups\superguard_cycle_XXX_TIMESTAMP\`
- **Telegram report**: Summary with status emojis
- **Schedule**: Every 2 hours via Windows Task Scheduler (`superguard-evolution-2h`)

### Cron job (Hermes)
```bash
# Created via cronjob tool
cronjob action=create name=superguard-evolution-2h schedule="every 2h" \
  prompt="Run SuperGuard autonomous evolution cycle..." \
  workdir="C:\Users\tomas\AppData\Local\Temp\xfetch"
```

### Backup manifest
Each cycle creates `manifest.json` with cycle number, timestamp, file list, and Hermes config/env copies.

## i18n Verification
- **48 keys × 3 languages** = 144 strings validated
- All keys present in RU/EN/ES
- Missing keys fall back to RU

## OpenCode Zen Fallback Chain (config.yaml)
```yaml
fallback_providers:
  '0': { provider: opencode-zen, model: nemotron-3-ultra-free }
  '1': { provider: opencode-zen, model: deepseek-v4-flash-free }
  '2': { provider: opencode-zen, model: laguna-s-2.1-free }
  '3': { provider: gemini, model: gemini-2.0-flash }
  '4': { provider: kilocode, model: deepseek-v4-flash-free }
  '5': { provider: openai-api, model: gpt-4o-mini }
```
- `hermes auth reset opencode-zen` clears exhaustion
- Auto-rotation on 429 between keys and providers

## Verification Scripts

### `hermes-verify-superguard.py`
Validates:
- Syntax OK
- Test suite (4/4)
- Multi-camera structure (8 cameras, skip empty URLs)
- Camera name in alarm messages
- Camera i18n (RU/EN/ES)
- Actuator imports
- OpenCode Zen key count (~8)
- Actuator package imports (6 types)

## Remaining TODOs
1. **Add real camera URLs** to `CAMERA_URLS` for cam_2 through cam_8
2. **Test `/togglealarm`** manual trigger with camera info in Telegram
3. **Add API health-check** in evolution cycle (getUpdates + sendMessage probe)
4. **Phase 2**: Sonoff/Tasmota real device integration
5. **WhatsApp Cloud API** channel for alerts

## Files Modified This Session
- `panic_mode.py` — Main bot (all fixes + multi-camera + actuator integration)
- `actuators/__init__.py` — Auto-registration
- `actuators/base.py` — ABC + Registry
- `actuators/tuya.py` — TuyaActuator
- `actuators/sonoff.py` — SonoffActuator
- `actuators/shelly.py` — ShellyActuator
- `actuators/esphome.py` — ESPHomeActuator
- `actuators/zigbee.py` — ZigbeeActuator
- `evolution_cycle.py` — Autonomous cycle + Telegram reports
- `kill_zombies.ps1` — Fixed PowerShell syntax
- `sguard.env` — Config (unchanged)
- `sguard_settings.json` — Persistent settings (auto-managed)