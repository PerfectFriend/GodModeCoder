# Evolution Cycle Protocol

## Overview
Autonomous evolution cycles run every 2 hours via Windows Task Scheduler (`superguard-evolution-2h`).

Each cycle: tests → debug → USB backup → Telegram report → version badge increment.

## Cycle Steps

### 1. Tests (must all pass)
```python
evolution_cycle.run_tests()
# Returns: {'syntax': bool, 'i18n': bool, 'target_parse': bool, 'graph': bool}
```
- **syntax**: `panic_mode.py` AST parse OK
- **i18n**: 39 critical keys present in all 3 languages (RU/EN/ES)
- **target_parse**: 11 target parsing cases pass
- **graph**: Graph.yaml structure valid

### 2. Debug Checks
```python
evolution_cycle.run_debug()
# Returns: {'bot_running': bool, 'fallback_config': bool, 'opencode_keys': bool, 'usb_drive': bool}
```
- **bot_running**: `panic_mode.py` process found via WMI
- **fallback_config**: LLM fallback chain configured
- **opencode_keys**: ~8 unique OpenCode Zen keys (deduplicated)
- **usb_drive**: `D:\` accessible for backups

### 3. USB Backup
```bash
# Destination: D:\backups\superguard_cycle_XXX_YYYYMMDD_HHMMSS
# Copies: panic_mode.py, sguard.env, sguard_settings.json, requirements.txt,
#         setup_autostart.ps1, evolution_cycle.py, README*.md, assets/, actuators/
```

### 4. Telegram Report
Sent to configured group/topic with:
- Cycle number and timestamp
- Test results (✅/❌)
- Debug check results
- Backup path
- Version badge (A00, A01, A02...)

### 5. Version Badge
Incremented each successful cycle. Format: `A{number:02d}` (A00, A01...A99, then B00...).

## Running Manually
```python
import sys
sys.path.insert(0, r'C:\Users\tomas\AppData\Local\Temp\xfetch')
import evolution_cycle
evolution_cycle.load_env()
success = evolution_cycle.run_cycle(cycle_number)
```

## Cron Setup
```powershell
# Windows Task Scheduler: superguard-evolution-2h
# Trigger: Every 2 hours
# Action: python C:\SuperGuard\evolution_cycle.py
```

## Key Files
- `evolution_cycle.py` — main orchestration
- `install_evolution_cron.ps1` — Task Scheduler installer
- `D:\backups\` — USB backup destination