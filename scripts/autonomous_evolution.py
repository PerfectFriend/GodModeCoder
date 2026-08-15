#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Autonomous Evolution Cron — nightly 00:00-08:00 evolution cycles.

This is the PROFESSOR's nightly work: while the laptop is idle,
run evolution cycles, learn from AI news, update textbook,
evolve skills, mutate graph, and commit all to genetic memory (Vault + Git).

Schedule: cron "0 0 * * *" (start at midnight), runs until ~08:00.
Each cycle: SENSE → THINK → MUTATE → FITNESS → COMMIT → MEMORY → EVOLVE.
"""
import sys
import json
import random
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(r"C:\Users\yusya\GodModeCoder")
VAULT = Path(r"C:\Vault")
CHRONICLE = VAULT / "Evolution" / "chronicle.md"
GRAPH_YAML = REPO / "Graph.yaml"
GRAPH_CONFIG = REPO / "configs" / "graph.yaml"
PY = Path.home() / "AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"

# Evolution config
MAX_CYCLES = 8          # max cycles per night (00:00-08:00)
CYCLE_MINUTES = 50      # target ~50 min per cycle = 8 cycles in 8h
HARD_STOP = 7.75        # stop at 07:45 (45 min buffer before 08:00 sync)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def run_cmd(cmd, cwd=None, timeout=300):
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace')
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)

def pulse_check():
    """SENSE: run pulse.py --quiet, return (alive_count, total, dead_nodes)."""
    code, out, err = run_cmd(f'"{PY}" "{REPO / "scripts" / "pulse.py"}" --quiet', cwd=REPO)
    alive = 0
    total = 0
    dead = []
    for line in out.splitlines():
        if "живы" in line or "alive" in line.lower():
            import re
            m = re.search(r'(\d+)/(\d+)', line)
            if m:
                alive, total = int(m.group(1)), int(m.group(2))
        if "МЁРТВ" in line or "DEAD" in line or "☠" in line:
            dead.append(line.strip())
    return alive, total, dead

def ollama_review(diff_text):
    """THINK: ask Gemma 4 to review diff, return insights."""
    prompt = f"""Review this git diff. List bugs, security issues, and improvements concisely (numbered list, max 5 items):

{diff_text[:3000]}

Format: 1. [TYPE] description"""
    import urllib.request
    data = json.dumps({"model": "gemma4:latest", "prompt": prompt, "stream": False, "options": {"num_predict": 400}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read().decode())
        return resp.get("response", "").strip()
    except Exception as e:
        return f"Ollama error: {e}"

def get_recent_diff():
    """Get diff of last commit."""
    code, out, _ = run_cmd("git diff HEAD~1 --stat", cwd=REPO)
    code2, out2, _ = run_cmd("git diff HEAD~1", cwd=REPO)
    return out2 if out2 else out

def mutate_code(insights):
    """MUTATE: ask Gemma to apply fixes/refactors based on insights."""
    prompt = f"""Based on these code review insights, write a focused Python patch (unified diff format) that fixes the top issues.
Only output the diff. No explanation.

Insights:
{insights}

Target: GodModeCoder repo scripts/*.py"""
    import urllib.request
    data = json.dumps({"model": "gemma4:latest", "prompt": prompt, "stream": False, "options": {"num_predict": 800}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.loads(r.read().decode())
        return resp.get("response", "").strip()
    except Exception as e:
        return f"Ollama error: {e}"

def apply_patch(patch_text):
    """FITNESS: try to apply patch, run verification."""
    if not patch_text or "```" not in patch_text:
        return False, "No valid patch"
    # Extract diff from markdown code block
    import re
    m = re.search(r'```(?:diff|patch)?\n(.*?)\n```', patch_text, re.DOTALL)
    diff = m.group(1) if m else patch_text
    # Write to temp file and try git apply --check
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
        f.write(diff)
        patch_file = f.name
    code, _, err = run_cmd(f'git apply --check "{patch_file}"', cwd=REPO)
    if code != 0:
        return False, f"Patch check failed: {err}"
    # Apply
    code, _, err = run_cmd(f'git apply "{patch_file}"', cwd=REPO)
    if code != 0:
        return False, f"Patch apply failed: {err}"
    # Run verification
    code, out, err = run_cmd(f'"{PY}" "{REPO / "scripts" / "hermes-verify-all.py"}"', cwd=REPO, timeout=300)
    if code != 0 or "ALL TESTS PASSED" not in out:
        # Rollback
        run_cmd("git reset --hard HEAD", cwd=REPO)
        return False, f"Verification failed: {err[:200]}"
    return True, "Mutation applied & verified"

def commit_mutation(msg):
    """COMMIT: commit changes with evolution message."""
    run_cmd("git add -A", cwd=REPO)
    run_cmd(f'git commit -m "{msg}"', cwd=REPO)
    run_cmd("git push origin main", cwd=REPO)

def update_memory(cycle, insights, mutation_applied):
    """MEMORY: update Chronicle.md with evolution record."""
    entry = f"""
## {datetime.now():%Y-%m-%d %H:%M} — Evolution Cycle {cycle}
**Cycle:** {cycle}/{MAX_CYCLES} | **Mutation:** {'APPLIED' if mutation_applied else 'REJECTED'}

### Insights from Review
{insights[:1000]}

### Fitness Gate
{'PASSED — mutation committed' if mutation_applied else 'FAILED — rolled back'}

---
"""
    chron = CHRONICLE.read_text(encoding="utf-8")
    if chron.endswith("---\n"):
        chron = chron[:-4] + entry + "\n---\n"
    else:
        chron += entry
    CHRONICLE.write_text(chron, encoding="utf-8")
    # Also update graph.yaml timestamp
    import yaml
    g = yaml.safe_load(GRAPH_CONFIG.read_text(encoding="utf-8"))
    for n in g.get("nodes", []):
        if n.get("id") == "gardener":
            n["last_evolution"] = datetime.now().isoformat()
            n["cycle"] = cycle
    GRAPH_CONFIG.write_text(yaml.dump(g, allow_unicode=True, sort_keys=False), encoding="utf-8")

def evolve_graph():
    """EVOLVE: occasionally add/mutate graph nodes based on learning."""
    # 10% chance to add a new node from textbook insights
    if random.random() < 0.1:
        log("🧬 EVOLVE: Graph mutation triggered")
        # Could add node here based on textbook insights
        pass

def main():
    start_time = datetime.now()
    log(f"=== AUTONOMOUS EVOLUTION STARTED (Professorial Night Shift) ===")
    log(f"Start: {start_time:%H:%M} | Max cycles: {MAX_CYCLES} | Hard stop: 07:45")
    
    for cycle in range(1, MAX_CYCLES + 1):
        now = datetime.now()
        if now.hour >= HARD_STOP:
            log(f"⏰ Hard stop reached ({now:%H:%M} >= 07:45). Ending night shift.")
            break
        
        cycle_start = time.time()
        log(f"\n{'='*50}")
        log(f"CYCLE {cycle}/{MAX_CYCLES}")
        log(f"{'='*50}")
        
        # SENSE
        log("🔍 SENSE: Pulse check...")
        alive, total, dead = pulse_check()
        log(f"   Pulse: {alive}/{total} alive")
        if dead:
            log(f"   Dormant: {dead[:3]}")
        
        # THINK
        log("🧠 THINK: Ollama code review...")
        diff = get_recent_diff()
        insights = ollama_review(diff)
        log(f"   Review: {insights[:200]}...")
        
        # MUTATE
        log("🧬 MUTATE: Generating patch...")
        patch = mutate_code(insights)
        
        # FITNESS + COMMIT
        log("⚖️ FITNESS: Applying & verifying...")
        ok, msg = apply_patch(patch)
        if ok:
            commit_msg = f"gen-night: cycle {cycle} — {insights.split(chr(10))[0][:80]}"
            commit_mutation(commit_msg)
            log(f"   ✅ {msg}")
        else:
            log(f"   ❌ {msg}")
        
        # MEMORY
        log("💾 MEMORY: Updating Chronicle & Graph...")
        update_memory(cycle, insights, ok)
        
        # EVOLVE
        evolve_graph()
        
        # Timing
        elapsed = time.time() - cycle_start
        log(f"   Cycle time: {elapsed:.0f}s")
        
        # Sleep to maintain ~50 min/cycle
        sleep_time = max(10, CYCLE_MINUTES * 60 - elapsed)
        if cycle < MAX_CYCLES:
            log(f"😴 Sleeping {sleep_time:.0f}s until next cycle...")
            time.sleep(sleep_time)
    
    log(f"\n=== AUTONOMOUS EVOLUTION COMPLETE ===")
    log(f"Cycles run: {cycle} | Duration: {datetime.now() - start_time}")

if __name__ == "__main__":
    main()