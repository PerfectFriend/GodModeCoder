#!/usr/bin/env python3
"""Крон-обёртка для авто-экспорта эволюционного графа в Obsidian Vault.
Запускается Hermes cron каждые 6ч (no_agent=true, deliver=local)."""
import sys
import subprocess
from datetime import datetime
from pathlib import Path

VAULT = Path.home() / "ObsidianVault"
SCRIPT = Path.home() / "GodModeCoder" / "scripts" / "export_graph_to_obsidian.py"
CONFIG = Path.home() / "GodModeCoder" / "Graph.yaml"
VERIFY_SCRIPT = Path.home() / "GodModeCoder" / "scripts" / "hermes-verify-all-linux.py"
PYTHON = Path(sys.executable)

def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Starting graph pulse export...")
    
    # 1. Run exporter
    result = subprocess.run(
        [str(PYTHON), str(SCRIPT), "--vault", str(VAULT), "--config", str(CONFIG)],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        print(f"EXPORT FAILED: {result.stderr}")
        return 1
    print(result.stdout.strip())
    
    # 2. Git commit (history of evolution)
    try:
        subprocess.run(["git", "-C", str(VAULT), "add", "Evolution/"], check=True, capture_output=True)
        commit_msg = f"graph: pulse export {datetime.now():%Y-%m-%d %H:%M}"
        subprocess.run(["git", "-C", str(VAULT), "commit", "-m", commit_msg], check=True, capture_output=True)
        print(f"Git committed: {commit_msg}")
    except subprocess.CalledProcessError as e:
        print(f"Git commit failed (may be no changes): {e}")
    
    # 3. Run verification
    verify_result = subprocess.run(
        [str(PYTHON), str(VERIFY_SCRIPT)],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if verify_result.returncode != 0:
        print(f"VERIFICATION FAILED:\n{verify_result.stdout}")
        return 1
    print("✅ All verification tests passed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())