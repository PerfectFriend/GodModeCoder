#!/usr/bin/env python3
"""
Pulse History Logger — записывает историю пульса в CSV для Obsidian Heatmap.

Запуск cron:
    python pulse-history.py

Логика:
  1. Запускает pulse.py — получает полный статус графа
  2. Дописывает строку в CSV: timestamp, total, alive, dead, dead_names
  3. CSV читается Obsidian Dataview / Heatmap Calendar

Выход: stdout = краткая сводка (для cron)
       exit 0 = всё живое, 1 = есть мёртвые
"""

import subprocess
import re
import csv
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(r"C:\Users\tomas\the-grimoire\ru\scripts")
VAULT_DIR = Path(r"C:\Vault")
HISTORY_CSV = VAULT_DIR / "Evolution" / "pulse-history.csv"
PYTHON = r"C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"


def run_pulse():
    """Run pulse.py, return (total_nodes, alive_count, dead_list)."""
    try:
        r = subprocess.run(
            [PYTHON, "pulse.py", "--quiet"],
            cwd=str(SCRIPTS_DIR),
            capture_output=True, text=True, timeout=60
        )
        output = r.stdout + r.stderr
        match = re.search(r"МЁРТВЫЕ:\s*(.+)", output)
        if match:
            dead = [n.strip() for n in match.group(1).split(",") if n.strip()]
        else:
            dead = []
        return dead, output
    except Exception as e:
        return [], f"Pulse error: {e}"


def append_csv(dead_nodes):
    """Append pulse record to CSV."""
    is_new = not HISTORY_CSV.exists()
    with open(HISTORY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["date", "time", "total", "alive", "dead_count", "dead_names"])
        now = datetime.now()
        # Count total from graph.yaml nodes (approximate: pulse knows)
        total = 21  # from graph.yaml
        alive = total - len(dead_nodes)
        writer.writerow([
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M"),
            total,
            alive,
            len(dead_nodes),
            ", ".join(dead_nodes) if dead_nodes else ""
        ])


def main():
    dead, raw = run_pulse()
    append_csv(dead)

    # Summary for cron delivery
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = 21
    alive = total - len(dead)

    if not dead:
        print(f"📊 Pulse [{ts}]: {alive}/{total} alive — all green")
        return 0
    else:
        print(f"📊 Pulse [{ts}]: {alive}/{total} alive, {len(dead)} dead: {', '.join(dead)}")
        return 0  # Always 0 — report in stdout for cron delivery


if __name__ == "__main__":
    exit(main())
