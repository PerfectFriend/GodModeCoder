#!/usr/bin/env python3
"""
Dead Node Extinction — авто-архивация узлов мёртвых >7 дней подряд.

Запуск cron (daily):
    python extinction.py

Логика:
  1. Читает pulse-history.csv — считает сколько дней подряд каждый узел мёртв
  2. Если узел мёртв >7 дней подряд → экстинкция:
     a. Перемещает Evolution/<node>.md → Evolution/archive/<node>.md
     b. Записывает extinction record в chronicle.md
     c. Удаляет узел из graph.yaml (опционально — требует подтверждения)
  3. Формирует отчёт (stdout для cron delivery)

Выход: stdout = отчёт, exit 0 = не было экстинкций, 1 = были экстинкции

Crontab (Hermes):
  job_id: (auto-create)
  name: dead-node-extinction
  schedule: every 24h
  script: extinction.py
  no_agent: true
  deliver: origin
"""

import csv
from pathlib import Path
from datetime import datetime, timedelta
import shutil

VAULT_DIR = Path(r"C:\Vault")
EVOLUTION_DIR = VAULT_DIR / "Evolution"
ARCHIVE_DIR = EVOLUTION_DIR / "archive"
CHRONICLE = EVOLUTION_DIR / "chronicle.md"
HISTORY_CSV = EVOLUTION_DIR / "pulse-history.csv"
GRAPH_YAML = Path(r"C:\Users\tomas\the-grimoire\ru\configs\graph.yaml")

DEAD_THRESHOLD_DAYS = 7


def load_pulse_history():
    """Load pulse-history.csv, return list of dicts sorted by date+time."""
    if not HISTORY_CSV.exists():
        return []
    with open(HISTORY_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return sorted(rows, key=lambda r: (r.get("date", ""), r.get("time", "")))


def find_long_dead_nodes(history, threshold_days=DEAD_THRESHOLD_DAYS):
    """Find nodes that have been dead for >= threshold_days consecutive entries.
    
    Checks the last `threshold_days` days of entries.
    A node is 'long dead' if it appears in dead_names for ALL entries in the last N days.
    """
    if not history:
        return []
    
    # Get unique dates sorted (most recent first)
    dates = sorted(set(r["date"] for r in history), reverse=True)
    
    if len(dates) < threshold_days:
        # Not enough history yet — can't confirm long-dead
        return []
    
    # Take last N unique dates
    recent_dates = dates[:threshold_days]
    
    # For each recent date, check if node was dead
    # A node is long-dead if it's dead in ALL recent dates
    from collections import defaultdict
    dead_counts = defaultdict(int)
    for date in recent_dates:
        day_entries = [r for r in history if r["date"] == date]
        if day_entries:
            # Take the last entry of that day
            last_entry = day_entries[-1]
            dead_names = last_entry.get("dead_names", "")
            if dead_names:
                for name in dead_names.split(","):
                    name = name.strip()
                    if name:
                        dead_counts[name] += 1
    
    # Node must be dead in ALL recent dates
    long_dead = [name for name, count in dead_counts.items() if count >= threshold_days]
    return long_dead


def extinguish_node(node_id, reason="Dead >7 days"):
    """Archive a dead node: move .md to archive/, record in chronicle."""
    node_file = EVOLUTION_DIR / f"{node_id}.md"
    
    if not node_file.exists():
        return False, f"File not found: {node_file}"
    
    # Create archive dir if needed
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Move to archive
    dst = ARCHIVE_DIR / f"{node_id}.md"
    if dst.exists():
        # Already archived — skip
        return False, f"Already archived: {dst}"
    
    shutil.move(str(node_file), str(dst))
    
    # Record in chronicle
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {ts} — AUTO-EXTINCTION: {node_id}\n"
    entry += f"**Reason:** {reason}\n"
    entry += f"**Archived to:** archive/{node_id}.md\n"
    entry += f"**Trigger:** extinction.py (dead >{DEAD_THRESHOLD_DAYS} days)\n---\n"
    
    with open(CHRONICLE, "a", encoding="utf-8") as f:
        f.write(entry)
    
    return True, f"Archived {node_id} → archive/{node_id}.md"


def main():
    history = load_pulse_history()
    if not history:
        print("No pulse history found — nothing to check.")
        return 0
    
    long_dead = find_long_dead_nodes(history)
    
    if not long_dead:
        print(f"✅ No nodes dead >{DEAD_THRESHOLD_DAYS} days. System healthy.")
        return 0
    
    print(f"🔍 Found {len(long_dead)} nodes dead >{DEAD_THRESHOLD_DAYS} days: {', '.join(long_dead)}")
    print()
    
    extinguished = []
    failed = []
    for node_id in long_dead:
        success, msg = extinguish_node(node_id, f"Dead >{DEAD_THRESHOLD_DAYS} consecutive days")
        if success:
            extinguished.append(node_id)
            print(f"  🔴 EXTINCT: {msg}")
        else:
            failed.append((node_id, msg))
            print(f"  ⚠️  SKIP: {msg}")
    
    print()
    if extinguished:
        print(f"💀 Extinction complete: {len(extinguished)} node(s) archived.")
        print(f"   Archived: {', '.join(extinguished)}")
        print(f"   These nodes should be removed from graph.yaml manually.")
        return 1
    else:
        print(f"No new extinctions (all already archived or missing).")
        return 0


if __name__ == "__main__":
    exit(main())
