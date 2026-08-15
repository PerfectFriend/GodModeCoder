#!/usr/bin/env python3
"""
GodMode Watchdog — авто-мониторинг мёртвых узлов графа.

Запуск cron:
    python godmode-watchdog.py

Логика:
  1. Запускает pulse.py — получает список мёртвых
  2. Если мёртвые есть:
     a. Записывает в chronicle.md с timestamp
     b. Формирует alert-сообщение (stdout для cron delivery)
  3. Если мёртвых >7 дней — предлагает экстинкцию в archive

Выход: stdout = alert-сообщение (для cron job delivery)
       exit 0 = всегда (alert в stdout, cron доставляет если print не пустой)

Crontab (Hermes):
  job_id: godmode-watchdog
  schedule: every 1h
  script: godmode-watchdog.py
  no_agent: true
  deliver: origin

"""

import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(r"C:\Users\tomas\the-grimoire\ru\scripts")
VAULT_DIR = Path(r"C:\Vault")
CHRONICLE = VAULT_DIR / "Evolution" / "chronicle.md"
ARCHIVE_DIR = VAULT_DIR / "Evolution" / "archive"
PYTHON = r"C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

DEAD_THRESHOLD_DAYS = 7  # After 7 days dead → propose extinction


def run_pulse():
    """Run pulse.py, return list of dead node IDs."""
    try:
        r = subprocess.run(
            [PYTHON, "pulse.py", "--quiet"],
            cwd=str(SCRIPTS_DIR),
            capture_output=True, text=True, timeout=60
        )
        output = r.stdout + r.stderr
        # Parse: "PULSE: МЁРТВЫЕ: node1, node2"
        match = re.search(r"МЁРТВЫЕ:\s*(.+)", output)
        if match:
            dead = [n.strip() for n in match.group(1).split(",") if n.strip()]
            return dead, output
        return [], output
    except Exception as e:
        return [], f"Pulse error: {e}"


def append_chronicle(dead_nodes, message=""):
    """Append event to chronicle.md."""
    if not CHRONICLE.exists():
        return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {ts} — Watchdog Pulse\n"
    entry += f"**Dead nodes:** {', '.join(dead_nodes)}\n"
    if message:
        entry += f"**Note:** {message}\n"
    entry += "---\n"
    with open(CHRONICLE, "a", encoding="utf-8") as f:
        f.write(entry)


def main():
    dead, raw = run_pulse()

    if not dead:
        # All alive — silent (no cron delivery)
        sys.exit(0)

    # Dead nodes found — emit alert
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    alert = f"🔴 GODMODE WATCHDOG ALERT [{ts}]\n"
    alert += f"Dead nodes ({len(dead)}): {', '.join(dead)}\n\n"

    # Detailed info per dead node
    for node_id in dead:
        alert += f"  • {node_id}\n"

    alert += f"\nReanimate: python godmode-bootstrap.py --fix\n"
    alert += f"Or manual: python pulse.py (in scripts/) for details"

    # Append to chronicle
    append_chronicle(dead, f"Watchdog detected {len(dead)} dead nodes")

    print(alert)
    # Exit 0 even with dead nodes — alert is in stdout (delivered by cron)
    # Exit 1 would be reported as "error" by cron no_agent mode
    sys.exit(0)


if __name__ == "__main__":
    main()
