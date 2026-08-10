#!/usr/bin/env python3
"""Ad-hoc verification for SuperGuard Alarm deployment."""
import sys, subprocess, re, os

BASE = r"C:\SuperGuard"
os.chdir(BASE)

def run(cmd, timeout=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=BASE)
    return r.returncode, r.stdout, r.stderr

print("=" * 60)
print("SUPERGUARD ALARM - AD-HOC VERIFICATION")
print("=" * 60)

# 1. Syntax check
print("\n[1] Syntax check panic_mode.py...")
rc, out, err = run(sys.executable + " -c \"import ast; ast.parse(open('panic_mode.py', encoding='utf-8').read()); print('OK')\"")
assert rc == 0, f"Syntax FAIL: {err}"
print("    PASS")

# 2. i18n test
print("\n[2] i18n test (48 keys x 3 langs)...")
rc, out, err = run(sys.executable + " test_i18n.py")
assert rc == 0 and "OK: all keys present" in out, f"i18n FAIL: {out} {err}"
print("    PASS")

# 3. Target parse test
print("\n[3] Target parse test (11 cases)...")
rc, out, err = run(sys.executable + " test_target_parse.py")
assert rc == 0 and "ALL OK" in out, f"Target parse FAIL: {out} {err}"
print("    PASS")

# 4. Verify key functions exist in source
print("\n[4] Verify critical functions in source...")
src = open("panic_mode.py", encoding="utf-8").read()
checks = [
    ("kill_other_instances", "Zombie killer"),
    ("save_settings(persist_target", "Target persistence on lang switch"),
    ("set_bot_menu_async", "Async menu update"),
    ("_handle_update", "Per-update isolation"),
    ("target_label", "Localized target label"),
    ("parse_target", "Target parser"),
    ("color_fraction", "Universal color fraction"),
    ("COLOR_MAP", "Color map with nested pairs"),
]
for fn, desc in checks:
    assert fn in src, f"Missing {fn} ({desc})"
    print(f"    PASS {desc}")

# 5. Verify COLOR_MAP structure (red = nested pairs)
print("\n[5] Verify COLOR_MAP red has nested pairs...")
m = re.search(r'"red"\s*:\s*(\[.*?\])', src, re.DOTALL)
assert m, "COLOR_MAP red not found"
red_val = m.group(1)
assert red_val.count("((") == 2, f"Red should have 2 nested pairs, got: {red_val}"
print("    PASS COLOR_MAP red = 2 nested HSV pairs")

# 6. Quick import test (no __main__)
print("\n[6] Import test (no __main__ execution)...")
rc, out, err = run(sys.executable + " -c \"import importlib.util; spec=importlib.util.spec_from_file_location('pm', 'panic_mode.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('Import OK')\"", timeout=30)
assert rc == 0, f"Import FAIL: {err}"
print("    PASS")

print("\n" + "=" * 60)
print("ALL VERIFICATIONS PASSED")
print("=" * 60)