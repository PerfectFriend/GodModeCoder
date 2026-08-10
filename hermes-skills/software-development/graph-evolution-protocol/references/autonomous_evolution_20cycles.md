# Autonomous Evolution Workflow — 20 Cycles + Cron

Based on Master Inquisitor's requirements: "запускай процесс автономной эволюции на 20 циклов и добавь эту задачу в крон - запуск каждые 2 часа с отчётами в телеграм. не забывай что в каждом цикле - тесты, дебаг и бэкапы на USB драйв"

## One-Shot 20 Cycles

```bash
#!/bin/bash
# run_20_cycles.sh
# Run from: C:\Users\tomas\the-grimoire

set -e

BOT_TOKEN="<TELEGRAM_BOT_TOKEN>"  # from .env or config
CHAT_ID="143293811"
USB_PATH="D:/backups"

for i in {1..20}; do
    echo "=== ГРИМУАР: ЦИКЛ $i/20 ==="
    DATE_LABEL=$(date +%Y%m%d-%H%M%S)
    
    # 1. TESTS — Pulse health check
    echo "[TEST] Running pulse.py..."
    python ru/scripts/pulse.py --quiet
    PULSE_EXIT=$?
    if [ $PULSE_EXIT -ne 0 ]; then
        echo "[WARN] Pulse reported issues (exit $PULSE_EXIT)"
    fi
    
    # 2. DEBUG — Auto mutation with fitness gate
    echo "[DEBUG] Running mutate.py --auto..."
    python ru/scripts/mutate.py --auto --fitness-threshold 0.6
    MUTATE_EXIT=$?
    if [ $MUTATE_EXIT -ne 0 ]; then
        echo "[WARN] Mutation cycle had issues (exit $MUTATE_EXIT)"
    fi
    
    # 3. BACKUP — Full project backup to USB
    echo "[BACKUP] Creating backup on USB..."
    BACKUP_DIR="$USB_PATH/grimoire-cycle-$i-$DATE_LABEL"
    mkdir -p "$BACKUP_DIR"
    rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
        --exclude='node_modules' --exclude='.venv' --exclude='venv' \
        --exclude='*.log' --exclude='*.tmp' \
        . "$BACKUP_DIR/"
    
    # Also backup Hermes config and skills
    rsync -av --exclude='__pycache__' \
        "C:/Users/tomas/AppData/Local/hermes/" "$BACKUP_DIR/hermes-config/"
    
    echo "[BACKUP] Done: $BACKUP_DIR"
    
    # 4. REPORT — Telegram notification
    echo "[REPORT] Sending Telegram..."
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d chat_id="$CHAT_ID" \
        -d parse_mode="Markdown" \
        -d text="🤖 *Гримуар v3.0: Цикл $i/20*
✅ Pulse: $( [ $PULSE_EXIT -eq 0 ] && echo OK || echo 'ISSUES' )
✅ Mutate: $( [ $MUTATE_EXIT -eq 0 ] && echo OK || echo 'ISSUES' )
💾 Backup: \`$BACKUP_DIR\`
⏰ $(date '+%Y-%m-%d %H:%M:%S')"
    
    echo "=== Цикл $i завершён ==="
    sleep 30
done

echo "🎉 Все 20 циклов завершены!"
curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d chat_id="$CHAT_ID" \
    -d parse_mode="Markdown" \
    -d text="🏁 *Гримуар: 20 циклов эволюции ЗАВЕРШЕНЫ*
Все циклы выполнены. Бэкапы на USB.
$(date '+%Y-%m-%d %H:%M:%S')"
```

## Cron Job (Every 2 Hours)

```bash
# Create via hermes cronjob
hermes cronjob create \
  --name "grimoire-evolution-2h" \
  --schedule "every 2h" \
  --skills "graph-evolution-protocol" \
  --prompt "cd C:/Users/tomas/the-grimoire && bash run_20_cycles.sh" \
  --deliver "origin"
```

Or directly in crontab:
```bash
0 */2 * * * cd C:/Users/tomas/the-grimoire && bash run_20_cycles.sh >> logs/evolution_cron.log 2>&1
```

## Required Scripts in Grimoire Repo

The following scripts should exist in `C:\Users\tomas\the-grimoire\ru\scripts\`:

| Script | Purpose | Called By |
|--------|---------|-----------|
| `pulse.py` | Health check all nodes | Cycle test step |
| `mutate.py` | Auto-mutation with fitness gate | Cycle debug step |
| `backup.py` | Full project backup to USB | Cycle backup step |

## Backup Script Template (`backup.py`)

```python
#!/usr/bin/env python3
"""Backup grimoire project to USB with timestamp."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

USB_PATH = Path("D:/backups")
PROJECT = Path("C:/Users/tomas/the-grimoire")
HERMES = Path("C:/Users/tomas/AppData/Local/hermes")

def run(cmd, **kwargs):
    return subprocess.run(cmd, shell=True, check=False, **kwargs)

def main():
    label = sys.argv[1] if len(sys.argv) > 1 else f"auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    dest = USB_PATH / f"grimoire-{label}"
    dest.mkdir(parents=True, exist_ok=True)
    
    # Project backup
    run(f'rsync -av --exclude=".git" --exclude="__pycache__" --exclude="*.pyc" '
        f'--exclude="node_modules" --exclude=".venv" --exclude="venv" '
        f'--exclude="*.log" --exclude="*.tmp" "{PROJECT}/" "{dest}/project/"')
    
    # Hermes config backup
    run(f'rsync -av --exclude="__pycache__" "{HERMES}/" "{dest}/hermes-config/"')
    
    print(f"Backup complete: {dest}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Mutation Script Template (`mutate.py`)

```python
#!/usr/bin/env python3
"""Auto-mutation with fitness gate."""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true')
    parser.add_argument('--fitness-threshold', type=float, default=0.6)
    args = parser.parse_args()
    
    if not args.auto:
        print("Use --auto for automatic mutation")
        return 1
    
    print(f"Running auto-mutation with fitness threshold {args.fitness_threshold}")
    # TODO: Implement graph-based mutation logic
    # 1. Load graph.yaml
    # 2. Find nodes with low fitness
    # 3. Generate 2+ candidate mutations per node
    # 4. Test candidates (fitness evaluation)
    # 5. Commit best, archive rest
    # 6. Update chronicle.md
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Telegram Bot Token

Token stored in `.env` or Hermes config:
- `TELEGRAM_BOT_TOKEN` — main bot token
- `TELEGRAM_CLEANUP_CHAT_ID=-1004431090317` — group for cleanup bot

## USB Path

Ensure `D:/backups` is mounted and writable:
```bash
# Check
ls -la D:/backups/
# If not mounted, mount USB drive to D:
```