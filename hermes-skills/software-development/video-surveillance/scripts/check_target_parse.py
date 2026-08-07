#!/usr/bin/env python3
"""Static check for parse_target() in panic_mode.py WITHOUT importing the module
(booting it would start YOLO/camera/Telegram).

Slices the dict literals + parse_target() body out of the source text, exec's
them into a fresh namespace, and asserts real-world cases. Run from the dir
containing panic_mode.py:
    python check_target_parse.py /path/to/panic_mode.py
"""
import sys, io, os, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

src_path = sys.argv[1] if len(sys.argv) > 1 else 'panic_mode.py'
src = open(src_path, encoding='utf-8').read()

# --- slice out the pieces we need (same pattern as check_i18n.py) ---
ns = {}
for name in ['VEHICLE_CLASSES', 'COLOR_MAP', 'COLOR_SYN', 'CLASS_MAP', 'CLASS_SYN']:
    i = src.index(name + ' = {')
    j = src.index('\n}\n', i) + 3
    ns[name] = None
    exec(src[i:j], ns)

i = src.index('def parse_target(')
j = src.index('def _ranges_color_name', i)
exec(src[i:j], ns)

parse_target = ns['parse_target']
COLOR_MAP = ns['COLOR_MAP']

def color_of(ranges):
    if not ranges:
        return None
    for cname, pairs in COLOR_MAP.items():
        if sorted(ranges) == sorted(pairs):
            return cname
    return None

# (text, expected classes set or None=keep, expected color name or None=no filter)
cases = [
    ("red car", {2}, "red"),
    ("жёлтая машина", {2}, "yellow"),
    ("человек в положении стоя", {0}, None),
    ("person standing", {0}, None),
    ("truck", {7}, None),
    ("белый грузовик", {7}, "white"),
    ("blue", {2, 5, 7}, "blue"),
    ("красный", {2, 5, 7}, "red"),
    ("автобус amarillo", {5}, "yellow"),
    ("carro rojo", {2}, "red"),
    ("любой объект", None, None),  # unrecognized -> keep current filter
]
ok = True
for text, exp_cls, exp_col in cases:
    classes, ranges = parse_target(text)
    got_cls = set(classes) if classes else None
    got_col = color_of(ranges)
    status = "OK " if got_cls == exp_cls and got_col == exp_col else "FAIL"
    if status == "FAIL":
        ok = False
    print(f"{status} '{text}' -> classes={got_cls} color={got_col} (exp {exp_cls}/{exp_col})")
print("ALL OK" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
