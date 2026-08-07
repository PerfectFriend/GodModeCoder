#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pulse.py — GodModeCoder homeostasis check.

Exit 0 = all alive | Exit 1 = some dead (details printed).

The pulse is the heartbeat of the organism: every node in Graph.yaml
gets checked against its fitness criterion.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent


def check_git_healthy() -> bool:
    """Repo is a living genome: git must work."""
    r = subprocess.run(["git", "-C", str(REPO), "status", "--short"],
                       capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def check_untracked() -> list[str]:
    r = subprocess.run(["git", "-C", str(REPO), "status", "--short"],
                       capture_output=True, text=True, timeout=30)
    return [line for line in (r.stdout or "").splitlines() if line.strip()]


def check_graph_exists() -> bool:
    return (REPO / "Graph.yaml").exists()


def check_readme_exists() -> bool:
    return (REPO / "README.md").exists()


def check_chronicle_exists() -> bool:
    return (REPO / "Chronicle.md").exists()


def check_archive_dir() -> bool:
    return (REPO / "archive").exists()


def main() -> int:
    alive: list[tuple[str, str, bool]] = [
        ("git", "repository is a valid git genome", check_git_healthy()),
        ("graph", "Graph.yaml (DNA) present", check_graph_exists()),
        ("readme", "README.md (identity) present", check_readme_exists()),
        ("chronicle", "Chronicle.md (history) present", check_chronicle_exists()),
        ("archive", "archive/ (graveyard) present", check_archive_dir()),
    ]

    print("🧬 GodModeCoder PULSE")
    print("=" * 40)
    for node, desc, ok in alive:
        mark = "🟢" if ok else "🔴"
        print(f"  {mark} {node:<12} {desc}")
        if not ok:
            print(f"     → {node} DEAD")

    dirty = check_untracked()
    if dirty:
        print(f"\n  ⚠️  {len(dirty)} uncommitted change(s) — pending generations:")
        for line in dirty[:10]:
            print(f"     {line}")
        # Not dead — uncommitted work is a living state.

    n_dead = sum(1 for _, _, ok in alive if not ok)
    print("=" * 40)
    if n_dead:
        print(f"PULSE: {len(alive) - n_dead}/{len(alive)} nodes alive — exit 1")
        return 1
    print("PULSE: ALL NODES ALIVE — exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
