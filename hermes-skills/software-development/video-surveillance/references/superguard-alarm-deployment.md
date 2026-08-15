# SuperGuard Alarm — Deployment Notes (VALIDATED 2026-08-06)

## Product Identity
- **Brand**: SuperGuard (repo: `PerfectFriend/AISuperGuard`)
- **Core file**: `panic_mode.py` (~1000 lines, single-file bot)
- **Scenario**: Cable-theft protection → evolved to general AI security service
- **Languages**: EN (default), RU, ES via `/setlocal`

## GitHub Deployment
```
irm https://raw.githubusercontent.com/DarkPushkin/superguard-alarm/main/install_superguard.ps1 | iex
```
One-command install on clean Windows 10/11 (Admin):
1. Python 3.12 (winget)
2. NSSM (service wrapper)
3. Git clone → venv → pip install requirements
4. `sguard.env` created (prompts for secrets)
5. Windows Service `SuperGuardAlarm` registered (auto-start)
6. Firewall rule for Tuya plug port 6668

## Critical Files (in repo root)
```
panic_mode.py              # All logic (see skill sections for details)
requirements.txt           # opencv-python ultralytics tinytuya requests psutil numpy
install_superguard.ps1     # Windows installer
sguard.env.example         # Template (NEVER commit real values)
README.md                  # English (default)
README.ru.md               # Russian
README.es.md               # Spanish
.gitignore                 # secrets, logs, frames, __pycache__
test_i18n.py               # 48 keys × 3 langs validation
test_target_parse.py       # 11 parse_target cases
```

## Windows Service (NSSM)
```powershell
nssm install SuperGuardAlarm "C:\SuperGuard\venv\Scripts\python.exe" "C:\SuperGuard\panic_mode.py"
nssm set SuperGuardAlarm AppDirectory "C:\SuperGuard"
nssm set SuperGuardAlarm AppStdout "C:\SuperGuard\superguard.log"
nssm set SuperGuardAlarm AppStderr "C:\SuperGuard\superguard_err.log"
nssm set SuperGuardAlarm Start SERVICE_AUTO_START
Start-Service SuperGuardAlarm
```

## GPU on AMD Radeon 780M (Beelink SER9)
**Windows ROCm 7.2 ONLY** — WSL2 doesn't work, DirectML segfaults:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm7.2
```
Verified: 8-min track generation < 10s on `acestep-v15-turbo` + `acestep-5Hz-lm-1.7B` (shift=3.0, thinking=true, steps=8, cfg=7.0).

## sguard.env (standalone, NEVER in Hermes .env)
```env
SG_TELEGRAM_BOT_TOKEN=<own_token_from_BotFather>
SG_CHAT_ID=143293811
SG_PLUG_IP=192.168.137.109
SG_PLUG_KEY=<32_hex_chars_local_key>
```
Chat ID is per-user — same chat, different bot token (fixes 409 Conflict with Hermes gateway).

## Tuya Smart Plug (Nivian NVS-SOCKETF-W2) — Local Only
- Protocol 3.4 ONLY (3.1-3.3 → Err 904)
- tinytuya 1.20.0, fresh `Device` per request
- dps keys STRINGS: `'1'`=relay, `'20'`=V×10, `'22'`=W×10, `'23'`=Wh×100
- IP via hotspot `192.168.137.109`, MAC `d8:c8:0c:d6:45:6c`, chip CB2S-BK7231N
- Scan subnet TCP 6668 to find IP

## Zombie Killer Pattern
```python
# At startup, BEFORE load_settings()
kill_other_instances()  # PowerShell + psutil PID, kills stale python.exe panic_mode
```

## Settings Persistence
```json
// sguard_settings.json (auto-generated, survives restarts)
{
  "zone": [3, 3, 5],
  "target": "white car",
  "lang": "es",
  "auto": true
}
```
Race condition fix: `load_settings()` FIRST in `__main__`, then threads. Never hand-edit while process runs.

## Bot Menu — Follows /setlocal, Not Client UI Language
```python
# WRONG (reverted): language_code variants
# CORRECT: deleteMyCommands ru/es/en, ONE default in bot's LANG
set_bot_menu_async()  # daemon thread, never blocks poll_loop
```

## Two-Message Alarm Flow (Audit-First)
- **msg A**: trigger frame, NO button, NEVER deleted (user removes manually)
- **msg B**: live frame, refreshed 2s, deleted on cancel/auto-resolve
- Auto-resolve: 5 clean frames → plug OFF + delete msg B + single summary text with current mode + zone + target

## Target Parser — Free Text Controls Real Filter
```python
parse_target("red car")       → classes={2}, color=red (dual HSV ranges)
parse_target("persona de pie") → classes={0}, no color filter
parse_target("любой объект")  → keep current filter + "не распознал цвет/класс"
```

## Verification Commands
```bash
cd superguard-alarm
python -c "import ast; ast.parse(open('panic_mode.py', encoding='utf-8').read()); print('Syntax OK')"
python test_i18n.py           # 48 keys × 3 langs
python test_target_parse.py   # 11 cases
```
All pass in validated state.