#!/usr/bin/env python3
"""Target parse test — 11 multilingual cases."""
import sys
sys.path.insert(0, ".")
from panic_mode import parse_target, CLASS_MAP, COLOR_MAP

tests = [
    # (input, expected_classes, expected_color)
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
    ("любой объект", None, None),
]

print("Running target parse tests...")
for inp, exp_cls, exp_color in tests:
    cls, ranges = parse_target(inp)
    color = None
    if ranges:
        # Find color name from ranges
        for cname, cranges in COLOR_MAP.items():
            if cranges == ranges:
                color = cname
                break
    ok = (cls == exp_cls) and (color == exp_color)
    status = "OK" if ok else "FAIL"
    print(f"{status}  {inp!r:25} -> classes={cls} color={color!r:6} (exp {exp_cls}/{exp_color!r})")
    assert ok, f"Failed: {inp}"

print("ALL OK")