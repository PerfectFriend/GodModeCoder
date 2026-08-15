---
name: superguard-evolution
description: Autonomous graph evolution for SuperGuard Alarm.
---

# SuperGuard Alarm — Autonomous Graphical Evolution System

**Trigger**: User says "приступай к автономной графической эволюции", "start autonomous evolution", or similar.

---

## System Overview

The evolution system implements the **Grimoire v3.0 Graph Evolution Protocol** applied to SuperGuard Alarm project:

```
SuperGuard Alarm Project
    │
    ├── nodes/           # Agent/Skill/Pipeline/Gateway/Memory/Watchdog nodes
    │   ├── alarm_engine.yaml
    │   ├── telegram_channel.yaml
    │   ├── actuator_tuya.yaml
    │   ├── evolution_oracle.yaml
    │   └── ...
    │
    ├── edges/           # FEEDS, CALLS, CONTROLS, EVALUATES, MUTATES, BACKUPS
    │
    ├── graph.yaml       # Registry: nodes, edges, fitness criteria
    ├── pulse.py         # Health check: HTTP/TCP/process/file/SKILL
    ├── chronicle.md     # Летопись: births, deaths, discoveries, mutations
    ├── archive/         # Могильник: extinct nodes with full genomes
    └── logs/            # Pulse logs, mutation logs, fitness evaluations
```

---

## Core Components

### 1. Graph Registry (`graph.yaml`)

```yaml
nodes:
  - id: alarm_engine
    type: PIPELINE
    role: core
    genome: "panic_mode.py"
    feeds: [telegram_channel, actuator_tuya]
    fitness: "detection_accuracy > 0.95, false_positive < 0.05, latency < 2s"
    state: ALIVE
    version: "1.0"

  - id: telegram_channel
    type: GATEWAY
    role: communication
    genome: "channels/telegram.py"
    feeds: [evolution_oracle]
    calls: [alarm_engine]
    fitness: "delivery_rate > 0.99, latency < 1s"
    state: ALIVE

  - id: actuator_tuya
    type: SKILL
    role: actuator
    genome: "actuators/tuya.py"
    feeds: [alarm_engine]
    fitness: "switch_success > 0.999, latency < 500ms"
    state: ALIVE

  - id: evolution_oracle
    type: AGENT
    role: oracle
    genome: "prompts/oracle.md"
    evaluates: [alarm_engine, telegram_channel, actuator_tuya]
    fitness: "mutation_quality > 0.8, no_regressions"
    state: ALIVE

edges:
  - from: alarm_engine
    to: telegram_channel
    type: FEEDS
  - from: alarm_engine
    to: actuator_tuya
    type: FEEDS
  - from: telegram_channel
    to: evolution_oracle
    type: CALLS
  - from: evolution_oracle
    to: alarm_engine
    type: EVALUATES
  - from: evolution_oracle
    to: alarm_engine
    type: MUTATES
```

### 2. Pulse System (`pulse.py`)

```python
#!/usr/bin/env python3
"""Pulse — homeostatic health check for all nodes."""

NODE_CHECKS = {
    "http": lambda url: requests.get(url, timeout=5).status_code == 200,
    "tcp": lambda host, port: socket.create_connection((host, port), timeout=3),
    "process": lambda script: subprocess.run(["pgrep", "-f", script], capture_output=True).returncode == 0,
    "file": lambda path: os.path.exists(path),
    "skill": lambda name: os.path.exists(f"{HERMES_HOME}/skills/{name}/SKILL.md"),
}

def check_node(node):
    genome = node.get("genome", "")
    if genome.startswith("http://") or genome.startswith("https://"):
        return "http", genome
    elif ":" in genome and not genome.startswith("."):
        host, port = genome.split(":")
        return "tcp", (host, int(port))
    elif genome.endswith(".py"):
        return "process", genome
    elif genome.startswith("skill:"):
        return "skill", genome[6:]
    else:
        return "file", genome

# Exit codes: 0 = all alive (silence = health), 1 = dead nodes reported
```

### 3. Chronicle (`chronicle.md`)

```
# Летопись Эволюции SuperGuard Alarm

## 2026-08-06 — Рождение системы
- **Рождение узлов**: alarm_engine, telegram_channel, actuator_tuya, evolution_oracle
- **Рождение рёбер**: FEEDS(alarm→telegram), FEEDS(alarm→actuator), CALLS(telegram→oracle), EVALUATES(oracle→alarm), MUTATES(oracle→alarm)
- **Fitness-критерии установлены**: detection_accuracy>0.95, delivery_rate>0.99, switch_success>0.999

## 2026-08-06 — Мутация #1: Actuator Abstraction
- **Мутация**: alarm_engine → actuator abstraction layer
- **Кандидаты**: 2 (TuyaActuator + BaseActuator ABC)
- **Fitness-гейт**: backward_compatible=True, new_actuators_ready=True
- **Результат**: ПРИНЯТ → alarm_engine v1.1

## 2026-08-06 — Открытие: Dual-Bot Architecture
- **Эмерджентность**: Два бота (CathedralMaster + SuperGuard Alarm) = разделение ответственности
- **Фиксация**: В графе — два GATEWAY узла, разные FEEDS
```

### 4. Mutation Protocol

```python
# Mutation candidate generation (minimum 2 candidates)
def propose_mutations(node_id, fitness_gap):
    prompt = f"""
    Node: {node_id}
    Current genome: {get_genome(node_id)}
    Fitness gap: {fitness_gap}
    Context: {get_context(node_id)}
    
    Propose exactly 2 distinct mutation candidates.
    Each must be a complete, runnable replacement.
    Focus on: {fitness_gap}
    """
    return llm_complete(prompt, n=2, temperature=0.7)

# Fitness gate
def fitness_gate(original, candidate1, candidate2):
    results = run_evaluation_suite([original, candidate1, candidate2])
    best = max(results, key=lambda r: r.fitness)
    if best != original and results[best].fitness > results[original].fitness * 1.05:
        return best
    return original
```

---

## Evolution Loop (Cron: every 6 hours)

```bash
# ~/.hermes/scripts/evolution_pulse.sh
#!/bin/bash
cd /c/Users/tomas/ai-radio  # Project root
python evolution/pulse.py --report-to-telegram
```

### Pulse Output Format

```
[timestamp] PULSE: МЁРТВЫЕ: node1, node2
# OR silence (exit 0) = all alive
```

### Telegram Report Format

```
📊 **PULSE REPORT** — 2026-08-06 14:00

✅ **ALIVE**: alarm_engine, telegram_channel, actuator_tuya, evolution_oracle
☠ **МЁРТВЫЕ**: none
📈 **FITNESS**:
  - alarm_engine: 0.97 (detection: 0.96, latency: 1.8s)
  - telegram_channel: 0.99 (delivery: 0.999)
  - actuator_tuya: 0.998 (switch: 0.999)

🧬 **MUTATIONS PENDING**: 0
📜 **CHRONICLE**: +2 entries
```

---

## Mutation Workflow

1. **FITNESS_LOW** event → Oracle proposes 2 candidates
2. **Fitness Gate** → automated test suite on both
3. **Oracle Review** (Telegram button) → approve/reject
4. **Commit** → replace node genome, version bump, chronicle entry
5. **Rollback** → if regression detected within 1 pulse cycle

---

## Telegram Commands for Evolution

| Command | Action |
|---------|--------|
| `/pulse` | Force pulse check, report to chat |
| `/graph` | Send current graph.yaml as file |
| `/chronicle` | Last 10 chronicle entries |
| `/mutate <node_id>` | Force mutation proposal for node |
| `/fitness <node_id>` | Run fitness evaluation |
| `/rollback <node_id>` | Revert to previous version |
| `/archive` | List archived nodes |

---

## Files Structure

```
evolution/
├── graph.yaml              # Registry
├── pulse.py                # Health check
├── chronicle.md            # Летопись
├── nodes/
│   ├── alarm_engine.yaml
│   ├── telegram_channel.yaml
│   ├── actuator_tuya.yaml
│   ├── evolution_oracle.yaml
│   └── ...
├── archive/                # Extinct nodes
│   ├── alarm_engine_v1.0.yaml
│   └── ...
├── logs/
│   ├── pulse.log
│   ├── mutations.log
│   └── fitness.log
├── prompts/
│   ├── oracle.md
│   └── mutation_prompt.md
└── scripts/
    ├── pulse.py
    ├── mutate.py
    ├── fitness.py
    └── report_telegram.py
```

---

## Integration with Hermes

- **Pulse cron**: `hermes cron create "evolution_pulse" "every 6h" "python evolution/pulse.py --report"`
- **Reports**: Via CathedralMaster_bot (Hermes gateway) → Telegram topic `reports`
- **Oracle approval**: Interactive Telegram buttons via gateway
- **Config**: `evolution/config.yaml` with tokens, chat_ids, thresholds

---

## Dual-Bot Architecture (Critical Discovery)

**Two separate Telegram bots with separate tokens:**

1. **CathedralMaster_bot** (Hermes gateway) - token in `~/.hermes/.env` as `TELEGRAM_BOT_TOKEN`
   - Handles evolution reports, Hermes gateway commands
   - Token: `7531368659:***` (CathedralMaster_bot)

2. **SuperGuard Alarm Bot** (standalone) - token in `sguard.env` as `SG_TELEGRAM_BOT_TOKEN`
   - Handles alarm commands, camera control, actuator control
   - Token: `8711875181:***` (SuperGuardAlarmBot)
   - Chat ID: `143293811` (same for both)

**Critical**: These MUST be separate tokens. Using same token causes 409 Conflict (long-poll collision).

---

## Zombie Process Killing (Critical for Stability)

**Problem**: Shell `kill` leaves python.exe alive → keeps long-poll → 409 Conflict with new instance.

**Solution**: PowerShell script kills ALL other `python.exe panic_mode.py` except current PID.

```powershell
# kill_zombies.ps1 (auto-generated at runtime with actual PID)
$mypid = <actual_pid>
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
Where-Object { $_.CommandLine -match 'panic_mode' -and $_.ProcessId -ne $mypid } |
ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Output ('killed ' + $_.ProcessId) }
```

**Implementation in panic_mode.py**:
```python
def kill_other_instances():
    import psutil, subprocess
    mypid = psutil.Process().pid
    ps_script = f"$mypid = {mypid}\nGet-CimInstance Win32_Process ..."
    with open("kill_zombies.ps1", "w") as f:
        f.write(ps_script)
    subprocess.run(["powershell", "-NoProfile", "-File", "kill_zombies.ps1"], ...)
```

**Call FIRST in `__main__`** before `load_settings()`.

---

## Multi-Camera Support (8 Cameras)

**CameraManager class** manages multiple cameras:
```python
CAMERA_URLS = {
    "main": "https://...",      # Banjar PTZ (working)
    "cam_2": "",                # Placeholder for London
    "cam_3": "",                # Placeholder for NYC
    # ... cam_4 through cam_8
}
CAMERA_NAMES = {
    "main": "Main Camera (Banjar PTZ)",
    "cam_2": "London Traffic (UK)",
    # ...
}
```

**Features**:
- Skip empty URLs gracefully
- `/cam` command: list, status, switch cameras
- Camera name in alarm messages with i18n
- Camera persisted in settings.json

---

## Per-Language Telegram Menu Commands

**Must register commands for each language_code** (ru, en, es):

```python
def set_bot_menu():
    for lc in ("ru", "es", "en"):
        tg("deleteMyCommands", data={"language_code": lc})
        tg("setMyCommands", data={"language_code": lc, "commands": _commands_payload(lc)})
    tg("setChatMenuButton", data={"chat_id": CHAT_ID, "menu_button": ...})
```

**Commands**: `/autoguard`, `/togglealarm`, `/zone`, `/target`, `/setlocal`, `/cam`

---

## Full i18n for Camera Key

Added `"camera"` key to all 3 languages:
- RU: `"camera": "Камера"`
- EN: `"camera": "Camera"`  
- ES: `"camera": "Cámara"`

Used in alarm messages: `f"📷 {tr('camera')}: {cam_name}"`

---

## /setlocal Command (Restored)

```python
def lang_keyboard():
    return json.dumps({"inline_keyboard": [[
        {"text": "🇬🇧 EN", "callback_data": "set_lang:en"},
        {"text": "🇪🇸 ES", "callback_data": "set_lang:es"},
        {"text": "🇷🇺 RU", "callback_data": "set_lang:ru"}]]})
```

`set_lang(code)` switches language, rebuilds menu, refreshes control message, persists language ONLY (not target/zone).

---

## Actuator Abstraction Layer

```python
# actuators/__init__.py
from .base import BaseActuator, ActuatorRegistry
from .tuya import TuyaActuator
from .sonoff import SonoffActuator
# ... shelly, esphome, zigbee

ActuatorRegistry.register("tuya", TuyaActuator)
ActuatorRegistry.register("sonoff", SonoffActuator)
```

**BaseActuator(ABC)**: `turn_on()`, `turn_off()`, `get_status()`, `get_power()`

**TuyaActuator**: Local control via tinytuya 3.4, retry logic, thread-safe.

---

## Evolution Cycle (Every 2 Hours)

```python
# evolution_cycle.py
def run_cycle(cycle):
    # 1. Run tests (syntax, i18n, target_parse, graph)
    # 2. Debug checks (bot_running, fallback_config, opencode_keys, usb_drive)
    # 3. Backup to USB D:\backups\
    # 4. Send Telegram report
```

**Cron**: `every 2h` via `hermes cron create` or Windows Task Scheduler.

---

## Anti-Patterns

❌ Pulse without Telegram report (blind operation)  
❌ Single mutation candidate (not evolution)  
❌ No fitness gate (blind commits)  
❌ No rollback plan  
❌ Archive without chronicle entry  
❌ Pulse without fitness evaluation  
❌ Same token for two bots (409 Conflict)  
❌ Shell kill without zombie cleanup  
❌ `/setlocal` without per-language menu registration  
❌ Camera name not in alarm messages  
❌ Bot token placeholder instead of real token  
❌ Push without verifying sguard.env synced to C:\SuperGuard\  
❌ Forgetting to test plug connectivity after IP change  

---

## Reports Topic

All evolution reports go to Telegram via **CathedralMaster_bot** (Hermes gateway) in the `reports` topic (thread). The bot token is `TELEGRAM_BOT_TOKEN` in `~/.hermes/.env`, chat ID `143293811`.

To send report:
```python
requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": report, "parse_mode": "HTML", "message_thread_id": REPORTS_THREAD_ID}
)
```

---

## References

- `references/camera-discovery.md` — 2500+ live DOT traffic cameras, working JPG sources, integration patterns
- `references/chronicle.md` — Evolution chronicle entries
- `references/oracle.md` — Oracle prompt templates