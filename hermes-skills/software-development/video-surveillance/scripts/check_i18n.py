#!/usr/bin/env python3
"""Static i18n key-parity check for the SuperGuard alarm bot (panic_mode.py).

Slices the L = {...} dict literal OUT of the source and exec()s only that
fragment - so it never imports the module (which would boot YOLO + camera
threads and need sguard.env creds). Then verifies:
  1. ru/en/es dicts have IDENTICAL key sets (missing keys = untranslated msg)
  2. every tr('key', ...) call in the source references a real key
  3. zone grid math for the documented examples (N3x4 C9 -> row 3 col 1)

Usage:  python check_i18n.py path/to/panic_mode.py
Exit code 0 = pass, 1 = fail.
"""
import re
import sys


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "panic_mode.py"
    src = open(path, encoding="utf-8").read()

    # extract the L dict literal (from 'L = {' to the line before 'def tr')
    start = src.index("L = {")
    end = src.index("\ndef tr(", start)
    ns = {}
    exec(src[start:end], ns)
    L = ns["L"]

    keys = set(L["ru"])
    bad = False
    for lang in ("en", "es", "ru"):
        missing = keys - set(L[lang])
        if missing:
            bad = True
            print(f"{lang}: MISSING {sorted(missing)}")
    print("keys total:", len(keys))

    # every tr('key', ...) call in source must be a real key
    calls = set(re.findall(r"tr\('([a-z_]+)'", src))
    for k in sorted(calls - keys):
        bad = True
        print(f"source calls unknown key: {k}")

    # zone grid math: N3x4 C9 -> row 3, col 1 (bottom-left); N3x3 C5 -> center
    for (cell, rows, cols, want) in [(9, 3, 4, (3, 1)), (5, 3, 3, (2, 2))]:
        r = (cell - 1) // cols + 1
        c = (cell - 1) % cols + 1
        if (r, c) != want:
            bad = True
            print(f"zone math wrong: N{rows}x{cols} C{cell} -> ({r},{c}) want {want}")

    print("OK: all keys present, zone math correct" if not bad else "FAIL")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
