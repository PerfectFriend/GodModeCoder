# SuperGuard Alarm Evolution Plan — Session Reference (2026-08-06)

## Context
Project: **SuperGuard Alarm** (Autonomous AI Security Service)
- Repo: `PerfectFriend/AISuperGuard` (branch `main` default)
- Core: `panic_mode.py` (~1000 lines) — YOLO11n + HSV color filter + zone grid + Tuya plug + Telegram bot
- Multi-language: EN (default) / RU / ES via `/setlocal` inline buttons
- Self-zombie-killer: `kill_other_instances()` via psutil + PowerShell
- Async menu updates, per-update isolation, persistence via `sguard_settings.json`

## Evolution Plan Summary (EVOLUTION_PLAN.md)

### Part 1: Multi-Device Actuator Support
**Current**: Single Tuya plug (tinytuya 3.4, local key, port 6668)
**Target**: Plugin-based `ActuatorRegistry` with `BaseActuator(ABC)`

| Device Family | Protocol | Library | Cost/Relay | Power Monitoring | Local Only |
|--------------|----------|---------|------------|------------------|------------|
| **Tuya** | tinytuya 3.4/3.5 | `tinytuya` | $15-25 | ✅ DPS 20/22/23 | ✅ |
| **Sonoff (Tasmota)** | MQTT/HTTP | `paho-mqtt`/`aiohttp` | $8-18 | ✅ (Pow) | ✅ |
| **Shelly** | CoAP/HTTP/MQTT/WS | `aiohttp`/`aiocoap`/`websockets` | $12-22 | ✅ (PM) | ✅ |
| **Tasmota (Generic)** | MQTT/HTTP/WS | `paho-mqtt`/`aiohttp` | $3-15 | ✅ | ✅ |
| **ESPHome** | Native API/MQTT | `aioesphomeapi` | $3-15 | ✅ | ✅ |
| **Zigbee (Z2M)** | MQTT | `paho-mqtt` | $15-22 | ❌ | ✅ (via coordinator) |
| **Matter/Thread** | Matter | `matter-python` | $25-35 | ✅ | ✅ |
| **DIY (Kincony/ESP32)** | HTTP/MQTT/Custom | `aiohttp`/`paho-mqtt` | $5-20/relay | Optional | ✅ |

**Architecture**: `ActuatorRegistry` → `BaseActuator(ABC)` → plugins (`TuyaActuator`, `SonoffActuator`, `ShellyActuator`, `TasmotaActuator`, `ESPHomeActuator`, `ZigbeeActuator`, `MatterActuator`, `DIYActuator`)

### Part 2: WhatsApp Integration
**Recommended**: WhatsApp Cloud API (official Meta) — free 1000 conv/mo

| Component | Implementation |
|-----------|----------------|
| Inbound | Webhook `POST /webhook/whatsapp` (FastAPI) |
| Outbound | Templates (Meta Console) + `send_image/text/template` |
| Commands | Text → router → internal commands (`/autoguard`, `/zone`, `/target`, `/setlocal`) |
| Photos | Upload media → `media_id` → send |
| Live-frame | Same flow, auto-delete after 2s |
| Multi-lang | Templates `alarm_trigger_ru/en/es` + `tr()` i18n |

**Fallback**: `whatsapp-web.js` / `GoWhatsApp` if Cloud API unavailable

**Channel Architecture**:
```
MessageDispatcher
├── TelegramChannel (existing, refactored)
└── WhatsAppChannel (NEW, Cloud API primary)
```

### Timeline (14 weeks)
| Phase | Weeks | Deliverable |
|-------|-------|-------------|
| 1. Actuator Abstraction | 2 | `actuators/` package, Tuya refactor |
| 2. Sonoff/Tasmota | 2 | MQTT + HTTP support |
| 3. Shelly | 1 | Gen1 + Plus |
| 4. ESPHome/Zigbee/Matter | 2 | Native API, Z2M, Matter |
| 5. DIY/Kincony | 1 | KC868, ESP32 DIY |
| 6. WhatsApp Core | 2 | Cloud API, templates, webhook |
| 7. WhatsApp Features | 2 | Commands, photos, live, i18n |
| 8. Unified Config/UI | 2 | YAML config, web UI, health |

**Total**: 14 weeks → Production-ready multi-device, multi-channel

### Immediate Next Steps
1. Create `actuators/` package, extract `BaseActuator` ABC
2. Create `TuyaActuator` class (exact current behavior)
3. Add `ACTUATOR_TYPE` env var with fallback to `tuya`
4. Test zero behavior change
5. Document in `docs/ACTUATORS.md` and `docs/WHATSAPP.md`