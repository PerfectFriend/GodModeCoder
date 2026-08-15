#!/usr/bin/env python3
"""Pulse — homeostatic health check for all nodes in SuperGuard evolution graph."""

import os, sys, json, subprocess, time, socket, requests
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent.parent
GRAPH_FILE = SKILL_DIR / "references" / "graph.yaml"
CHRONICLE_FILE = SKILL_DIR / "references" / "chronicle.md"
HERMES_HOME = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes"

# Load graph
def load_graph():
    import yaml
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def check_http(url):
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 200
    except Exception:
        return False

def check_tcp(host, port):
    try:
        socket.create_connection((host, int(port)), timeout=3)
        return True
    except Exception:
        return False

def check_process(script_name):
    try:
        # Windows: use PowerShell to find python.exe with script in command line
        ps = f'powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \\"Name=\'python.exe\'\\" | Where-Object {{ $_.CommandLine -match \'{script_name}\' }} | Measure-Object | Select-Object -ExpandProperty Count"'
        result = subprocess.run(ps, shell=True, capture_output=True, text=True, timeout=10)
        count = int(result.stdout.strip() or 0)
        return count > 0
    except Exception:
        return False

def check_file(path):
    return os.path.exists(path)

def check_skill(name):
    skill_path = HERMES_HOME / "skills" / name / "SKILL.md"
    return skill_path.exists()

def check_node(node):
    """Return (check_type, check_target) for a node's genome."""
    genome = node.get("genome", "")
    if genome.startswith("http://") or genome.startswith("https://"):
        return "http", genome
    elif ":" in genome and not genome.startswith(".") and not genome.endswith(".py"):
        # host:port format
        parts = genome.split(":")
        if len(parts) == 2:
            return "tcp", (parts[0], parts[1])
    elif genome.endswith(".py"):
        return "process", genome
    elif genome.startswith("skill:"):
        return "skill", genome[6:]
    else:
        return "file", genome

def run_pulse(report_to_telegram=False):
    graph = load_graph()
    dead_nodes = []
    results = {}

    for node in graph.get("nodes", []):
        node_id = node["id"]
        check_type, target = check_node(node)

        if check_type == "http":
            alive = check_http(target)
        elif check_type == "tcp":
            alive = check_tcp(target[0], target[1])
        elif check_type == "process":
            alive = check_process(target)
        elif check_type == "skill":
            alive = check_skill(target)
        else:
            alive = check_file(target)

        status = "ALIVE" if alive else "DEAD"
        results[node_id] = {"status": status, "check": check_type, "target": str(target)}

        if not alive:
            dead_nodes.append(node_id)
            node["state"] = "DEAD"
        else:
            node["state"] = "ALIVE"

    # Output format: [timestamp] PULSE: МЁРТВЫЕ: node1, node2
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if dead_nodes:
        print(f"[{timestamp}] PULSE: МЁРТВЫЕ: {', '.join(dead_nodes)}")
        return 1
    else:
        # Silence = health (exit 0)
        return 0

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-to-telegram", action="store_true")
    args = parser.parse_args()

    exit_code = run_pulse(args.report_to_telegram)
    sys.exit(exit_code)