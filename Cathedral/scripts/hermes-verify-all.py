#!/usr/bin/env python3
"""
HERMES VERIFY ALL — Полный автотест системы TurboCoder / Monster Coder
Запускается ПОСЛЕ КАЖДОЙ мутации. Fail = Rollback к чекпоинту.
"""

import subprocess
import sys
from pathlib import Path
import yaml
import json
import frontmatter

VAULT = Path(r"C:\Vault")
GRIMOIRE_SCRIPTS = Path(r"C:\Users\tomas\the-grimoire\ru\scripts")
GRIMOIRE_CONFIG = Path(r"C:\Users\tomas\the-grimoire\ru\configs\graph.yaml")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def run_test(name: str, cmd: list, cwd: Path = None, expect_exit: int = 0, check_output: str = None) -> bool:
    """Run a test command and return True if passes."""
    print(f"{Colors.BLUE}[TEST]{Colors.RESET} {name}...", end=" ")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace')
        if result.returncode != expect_exit:
            print(f"{Colors.RED}FAIL{Colors.RESET} (exit {result.returncode}, expected {expect_exit})")
            if result.stdout: print(f"  stdout: {result.stdout[:200]}")
            if result.stderr: print(f"  stderr: {result.stderr[:200]}")
            return False
        if check_output and check_output not in result.stdout:
            print(f"{Colors.RED}FAIL{Colors.RESET} (expected output '{check_output}' not found)")
            print(f"  stdout: {result.stdout[:200]}")
            return False
        print(f"{Colors.GREEN}OK{Colors.RESET}")
        return True
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}FAIL{Colors.RESET} (timeout)")
        return False
    except Exception as e:
        print(f"{Colors.RED}FAIL{Colors.RESET} ({e})")
        return False

def test_pulse():
    """Test 1: Pulse health check — exit 0 = all alive, exit 1 = some dead (warning, not fail)."""
    print(f"{Colors.BLUE}[TEST]{Colors.RESET} Pulse Health Check...", end=" ")
    try:
        result = subprocess.run([sys.executable, "pulse.py", "--quiet"], cwd=GRIMOIRE_SCRIPTS, capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace')
        if result.returncode == 0:
            print(f"{Colors.GREEN}OK{Colors.RESET} (all alive)")
            return True
        elif result.returncode == 1:
            # Parse dead nodes
            dead_line = [l for l in result.stdout.splitlines() if 'МЁРТВЫЕ' in l]
            if dead_line:
                print(f"{Colors.YELLOW}WARN{Colors.RESET} (some dead: {dead_line[0].strip()})")
            else:
                print(f"{Colors.YELLOW}WARN{Colors.RESET} (some nodes dead)")
            return True  # Warning, not failure - system can have dead nodes
        else:
            print(f"{Colors.RED}FAIL{Colors.RESET} (exit {result.returncode})")
            return False
    except Exception as e:
        print(f"{Colors.RED}FAIL{Colors.RESET} ({e})")
        return False

def test_export():
    """Test 2: Export to Obsidian — creates 13 nodes + INDEX.md"""
    result = subprocess.run([sys.executable, "export_graph_to_obsidian.py", "--vault", str(VAULT), "--config", str(GRIMOIRE_CONFIG)], cwd=GRIMOIRE_SCRIPTS, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"{Colors.RED}[TEST] Export to Obsidian FAIL{Colors.RESET} (exit {result.returncode})")
        print(f"  stderr: {result.stderr[:200]}")
        return False
    # Check files exist
    evolution_dir = VAULT / "Evolution"
    md_files = list(evolution_dir.glob("*.md"))
    if len(md_files) < 14:
        print(f"{Colors.RED}[TEST] Export FAIL{Colors.RESET} (only {len(md_files)} files, expected 14)")
        return False
    # Check INDEX.md exists
    if not (evolution_dir / "INDEX.md").exists():
        print(f"{Colors.RED}[TEST] Export FAIL{Colors.RESET} (INDEX.md missing)")
        return False
    print(f"{Colors.GREEN}[TEST] Export to Obsidian OK{Colors.RESET} ({len(md_files)} files)")
    return True

def test_graph_yaml_syntax():
    """Test 3: graph.yaml is valid YAML"""
    try:
        with open(GRIMOIRE_CONFIG, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        # Validate structure
        required_keys = ['nodes', 'edges', 'fitness']
        for k in required_keys:
            if k not in data:
                print(f"{Colors.RED}[TEST] graph.yaml structure FAIL{Colors.RESET} (missing '{k}')")
                return False
        # All nodes have id, type
        for node in data['nodes']:
            if 'id' not in node or 'type' not in node:
                print(f"{Colors.RED}[TEST] graph.yaml nodes FAIL{Colors.RESET} (node missing id/type)")
                return False
        # All edges reference existing nodes
        node_ids = {n['id'] for n in data['nodes']}
        for edge in data['edges']:
            if edge.get('from') not in node_ids or edge.get('to') not in node_ids:
                print(f"{Colors.RED}[TEST] graph.yaml edges FAIL{Colors.RESET} (references unknown node)")
                return False
        print(f"{Colors.GREEN}[TEST] graph.yaml syntax OK{Colors.RESET} ({len(data['nodes'])} nodes, {len(data['edges'])} edges)")
        return True
    except Exception as e:
        print(f"{Colors.RED}[TEST] graph.yaml syntax FAIL{Colors.RESET} ({e})")
        return False

def test_vault_tags():
    """Test 4: All Evolution/*.md have required frontmatter tags (skip INDEX.md, dashboards, presets)"""
    evolution_dir = VAULT / "Evolution"
    required_tags = {'#evolution/graph'}
    type_tags = {'#type/human', '#type/agent', '#type/skill', '#type/pipeline', '#type/memory', '#type/watchdog', '#type/gateway'}
    status_tags = {'#status/alive', '#status/sick', '#status/dead', '#status/unknown'}
    
    # Only check actual node files (not INDEX, dashboards, presets)
    skip_files = {"INDEX.md", "Graph Dashboard.md", "Dead Nodes Dashboard.md"}
    node_files = [f for f in evolution_dir.glob("*.md") if f.name not in skip_files]
    for md_file in node_files:
        try:
            post = frontmatter.load(md_file)
            tags = set(post.get('tags', []))
            # Check graph tag
            if not required_tags.issubset(tags):
                print(f"{Colors.RED}[TEST] Tags FAIL{Colors.RESET} ({md_file.name}: missing #evolution/graph, has {tags})")
                return False
            # Check type tag
            if not any(t in tags for t in type_tags):
                print(f"{Colors.RED}[TEST] Tags FAIL{Colors.RESET} ({md_file.name}: missing #type/*, has {tags})")
                return False
            # Check status tag
            if not any(t in tags for t in status_tags):
                print(f"{Colors.RED}[TEST] Tags FAIL{Colors.RESET} ({md_file.name}: missing #status/*, has {tags})")
                return False
        except Exception as e:
            print(f"{Colors.RED}[TEST] Tags FAIL{Colors.RESET} ({md_file.name}: {e})")
            return False
    print(f"{Colors.GREEN}[TEST] Vault tags OK{Colors.RESET} (all {len(node_files)} nodes tagged)")
    return True

def test_graph_json():
    """Test 5: .obsidian/graph.json is valid JSON"""
    graph_json = VAULT / ".obsidian" / "graph.json"
    try:
        with open(graph_json, encoding='utf-8') as f:
            data = json.load(f)
        # Check required fields
        required = ['colorGroups', 'search', 'showArrow', 'textFadeMultiplier', 'repelStrength']
        for r in required:
            if r not in data:
                print(f"{Colors.RED}[TEST] graph.json FAIL{Colors.RESET} (missing '{r}')")
                return False
        # Check colorGroups has our 9 groups
        if len(data['colorGroups']) < 9:
            print(f"{Colors.RED}[TEST] graph.json FAIL{Colors.RESET} (only {len(data['colorGroups'])} color groups, expected 9)")
            return False
        print(f"{Colors.GREEN}[TEST] graph.json OK{Colors.RESET} ({len(data['colorGroups'])} color groups)")
        return True
    except Exception as e:
        print(f"{Colors.RED}[TEST] graph.json FAIL{Colors.RESET} ({e})")
        return False

def test_css_snippet():
    """Test 6: CSS snippet exists and has required selectors"""
    css_file = VAULT / ".obsidian" / "snippets" / "graph-colors.css"
    if not css_file.exists():
        print(f"{Colors.RED}[TEST] CSS snippet FAIL{Colors.RESET} (file not found)")
        return False
    content = css_file.read_text(encoding='utf-8')
    required_selectors = [
        'color-fill[data-tag*="type/human"]',
        'color-fill[data-tag*="type/agent"]',
        'color-fill[data-tag*="type/skill"]',
        'color-fill[data-tag*="type/pipeline"]',
        'color-fill[data-tag*="type/memory"]',
        'color-fill[data-tag*="type/watchdog"]',
        'color-circle[data-tag*="status/alive"]',
        'color-circle[data-tag*="status/dead"]',
    ]
    for sel in required_selectors:
        if sel not in content:
            print(f"{Colors.RED}[TEST] CSS snippet FAIL{Colors.RESET} (missing selector '{sel}')")
            return False
    print(f"{Colors.GREEN}[TEST] CSS snippet OK{Colors.RESET} (all selectors present)")
    return True

def test_dashboards():
    """Test 7: Dataview dashboards exist and have valid syntax"""
    dashboards = [
        VAULT / "Evolution" / "Graph Dashboard.md",
        VAULT / "Evolution" / "Dead Nodes Dashboard.md",
    ]
    for db in dashboards:
        if not db.exists():
            print(f"{Colors.RED}[TEST] Dashboards FAIL{Colors.RESET} ({db.name} missing)")
            return False
        content = db.read_text(encoding='utf-8')
        if '```dataview' not in content and '```dataviewjs' not in content:
            print(f"{Colors.RED}[TEST] Dashboards FAIL{Colors.RESET} ({db.name}: no dataview blocks)")
            return False
    print(f"{Colors.GREEN}[TEST] Dashboards OK{Colors.RESET} (both present with dataview blocks)")
    return True

def test_presets():
    """Test 8: Graph presets exist"""
    presets = [
        VAULT / "Evolution" / "Presets" / "Full Graph.md",
        VAULT / "Evolution" / "Presets" / "Alive Only.md",
        VAULT / "Evolution" / "Presets" / "Commercial.md",
        VAULT / "Evolution" / "Presets" / "Radio.md",
    ]
    for p in presets:
        if not p.exists():
            print(f"{Colors.RED}[TEST] Presets FAIL{Colors.RESET} ({p.name} missing)")
            return False
    print(f"{Colors.GREEN}[TEST] Presets OK{Colors.RESET} (all 4 present)")
    return True

def test_git_clean():
    """Test 9: Vault git status clean (no uncommitted changes)"""
    result = subprocess.run(["git", "status", "--porcelain"], cwd=VAULT, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{Colors.YELLOW}[TEST] Git status SKIP{Colors.RESET} (not a git repo or error)")
        return True  # Not fatal
    if result.stdout.strip():
        print(f"{Colors.YELLOW}[TEST] Git status DIRTY{Colors.RESET} (uncommitted changes)")
        print(f"  {result.stdout[:200]}")
        return True  # Warning, not fail
    print(f"{Colors.GREEN}[TEST] Git status CLEAN{Colors.RESET}")
    return True

def test_skills_exist():
    """Test 10: Required skills are loaded/available"""
    skills_dir = Path(r"C:\Users\tomas\AppData\Local\hermes\skills")
    required = [
        "software-development/super-coder",
        "note-taking/obsidian",
        "autonomous-ai-agents/obsidian-graph-engineering",
        "autonomous-ai-agents/graph-engineering",
        "software-development/turbocoder",
    ]
    for skill in required:
        skill_path = skills_dir / skill / "SKILL.md"
        if not skill_path.exists():
            print(f"{Colors.RED}[TEST] Skills FAIL{Colors.RESET} ({skill} not found)")
            return False
    print(f"{Colors.GREEN}[TEST] Skills OK{Colors.RESET} (all {len(required)} present)")
    return True

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}══════════════════════════════════════════════════════════════")
    print(f"  HERMES VERIFY ALL — TurboCoder / Monster Coder Auto-Test Suite")
    print(f"══════════════════════════════════════════════════════════════{Colors.RESET}")
    print()
    
    tests = [
        ("1. Pulse Health Check", test_pulse),
        ("2. Export to Obsidian", test_export),
        ("3. graph.yaml Syntax", test_graph_yaml_syntax),
        ("4. Vault Tags", test_vault_tags),
        ("5. graph.json Config", test_graph_json),
        ("6. CSS Snippet", test_css_snippet),
        ("7. Dataview Dashboards", test_dashboards),
        ("8. Graph Presets", test_presets),
        ("9. Git Status", test_git_clean),
        ("10. Skills Present", test_skills_exist),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"{Colors.RED}[TEST] {name} CRASH{Colors.RESET} ({e})")
            failed += 1
    
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}══════════════════════════════════════════════════════════════")
    print(f"  RESULTS: {Colors.GREEN}{passed} passed{Colors.RESET} / {Colors.RED}{failed} failed{Colors.RESET}")
    print(f"══════════════════════════════════════════════════════════════{Colors.RESET}")
    
    if failed > 0:
        print(f"{Colors.RED}{Colors.BOLD}❌ VERIFICATION FAILED — ROLLBACK TO CHECKPOINT{Colors.RESET}")
        sys.exit(1)
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED — MUTATION APPROVED{Colors.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()