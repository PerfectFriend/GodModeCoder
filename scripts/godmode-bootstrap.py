#!/usr/bin/env python3
"""
GodMode Bootstrap — полный restauro сессии в один вызов.

Запуск:
    python godmode-bootstrap.py          # полный bootstrap
    python godmode-bootstrap.py --quiet  # тихий режим (только ошибки)
    python godmode-bootstrap.py --fix    # авто-чинить git dirty

Этапы:
  1. Pre-flight: pulse.py — проверка живости графа
  2. Vault sync: проверка количества файлов в Evolution/
  3. Git clean: git status — если dirty и --fix, коммит
  4. Smoke test: hermes-verify-all.py — 10 тестов
  5. Результат: ✅READY или ❌FAIL с инструкцией

Exit codes:
  0 — всё зелёное, можно работать
  1 — есть мёртвые узлы (WARN, допустимо)
  2 — verify FAIL (нужен rollback)
  3 — критическая ошибка (скрипт/путь не найден)
"""

import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Constants
SCRIPTS_DIR = Path(r"C:\Users\tomas\the-grimoire\ru\scripts")
VAULT_DIR = Path(r"C:\Vault")
EVOLUTION_DIR = VAULT_DIR / "Evolution"
PYTHON = r"C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

# Colors (ANSI)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log(msg, level="info"):
    """Print with color."""
    ts = datetime.now().strftime("%H:%M:%S")
    colors = {"info": CYAN, "ok": GREEN, "warn": YELLOW, "err": RED, "bold": BOLD}
    c = colors.get(level, "")
    print(f"{c}[{ts}] {msg}{RESET}")


def run(cmd, cwd=None, timeout=120):
    """Run command, return (exit_code, stdout)."""
    try:
        r = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError as e:
        return 3, str(e)
    except subprocess.TimeoutExpired:
        return 3, "TIMEOUT"


def step1_pulse():
    """Pre-flight: pulse check."""
    log("STEP 1/4: Pulse Health Check...", "bold")
    if not (SCRIPTS_DIR / "pulse.py").exists():
        log(f"  ❌ pulse.py not found at {SCRIPTS_DIR}", "err")
        return 3

    code, out = run([PYTHON, "pulse.py", "--quiet"], cwd=str(SCRIPTS_DIR))
    if code == 0:
        log("  ✅ All nodes alive", "ok")
        return 0
    elif code == 1:
        # WARN: dead nodes exist but script ran fine
        log(f"  ⚠️  {out}", "warn")
        return 1
    else:
        log(f"  ❌ Pulse error: {out}", "err")
        return 3


def step2_vault_sync():
    """Vault sync check."""
    log("STEP 2/4: Vault Sync Check...", "bold")
    if not EVOLUTION_DIR.exists():
        log(f"  ❌ Evolution/ dir missing: {EVOLUTION_DIR}", "err")
        return 3

    md_count = len(list(EVOLUTION_DIR.glob("*.md")))
    log(f"  📂 Evolution/ — {md_count} .md files", "info")
    if md_count < 15:
        log(f"  ⚠️  Expected ~21+ files, got {md_count}", "warn")
        return 1
    log("  ✅ Vault sync OK", "ok")
    return 0


def step3_git(fix=False):
    """Git clean check."""
    log("STEP 3/4: Git Status...", "bold")
    code, out = run(["git", "status", "--porcelain"], cwd=str(VAULT_DIR))
    if code != 0:
        log(f"  ❌ git status failed: {out}", "err")
        return 3

    if not out.strip():
        log("  ✅ Git clean", "ok")
        return 0

    dirty_count = len([l for l in out.strip().split("\n") if l.strip()])
    log(f"  ⚠️  Git DIRTY ({dirty_count} files)", "warn")

    if fix:
        log("  🔧 Auto-fixing: git add + commit...", "info")
        run(["git", "add", "-A"], cwd=str(VAULT_DIR))
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        code2, out2 = run(
            ["git", "commit", "-m", f"godmode-bootstrap: auto-fix {ts}"],
            cwd=str(VAULT_DIR),
        )
        if code2 == 0:
            log("  ✅ Git committed", "ok")
            return 0
        else:
            log(f"  ❌ Commit failed: {out2}", "err")
            return 3

    log("  💡 Run with --fix to auto-commit, or manual: cd C:\\Vault && git add -A && git commit", "info")
    return 1


def step4_verify():
    """Smoke test: hermes-verify-all.py."""
    log("STEP 4/4: Hermes Verify (10 tests)...", "bold")
    verify = SCRIPTS_DIR / "hermes-verify-all.py"
    if not verify.exists():
        log(f"  ❌ hermes-verify-all.py not found", "err")
        return 3

    code, out = run([PYTHON, "hermes-verify-all.py"], cwd=str(SCRIPTS_DIR), timeout=180)
    print(out)

    if "ALL TESTS PASSED" in out:
        log("  ✅ ALL TESTS PASSED — MUTATION APPROVED", "ok")
        return 0
    else:
        log("  ❌ VERIFY FAILED — rollback needed", "err")
        log("  💡 cd C:\\Vault && git log --oneline -5 && git reset --hard HEAD~1", "info")
        return 2


def main():
    parser = argparse.ArgumentParser(description="GodMode Bootstrap — full session restore")
    parser.add_argument("--quiet", action="store_true", help="Only show errors and warnings")
    parser.add_argument("--fix", action="store_true", help="Auto-fix git dirty")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  🚀 GODMODE BOOTSTRAP — Monster Coder Session Restore")
    print(f"{'='*60}\n")

    results = []
    results.append(step1_pulse())
    results.append(step2_vault_sync())
    results.append(step3_git(fix=args.fix))
    results.append(step4_verify())

    print(f"\n{'='*60}")
    worst = max(results)
    if worst == 0:
        print(f"  {GREEN}✅ BOOTSTRAP COMPLETE — YOU ARE MONSTER CODER{RESET}")
        print(f"  All systems green. Graph alive. Tests passed. Git clean.")
    elif worst == 1:
        print(f"  {YELLOW}⚠️  BOOTSTRAP OK WITH WARNINGS{RESET}")
        print(f"  Dead nodes or dirty git — non-blocking. You can work.")
    elif worst == 2:
        print(f"  {RED}❌ BOOTSTRAP FAILED — VERIFY ERROR{RESET}")
        print(f"  Rollback needed: cd C:\\Vault && git reset --hard HEAD~1")
    else:
        print(f"  {RED}❌ BOOTSTRAP CRITICAL ERROR{RESET}")
        print(f"  Scripts or paths missing. Check installation.")
    print(f"{'='*60}\n")

    sys.exit(worst)


if __name__ == "__main__":
    main()
