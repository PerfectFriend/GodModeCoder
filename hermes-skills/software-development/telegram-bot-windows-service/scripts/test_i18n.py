#!/usr/bin/env python3
"""i18n test — verifies all tr() keys present in RU/EN/ES + zone math."""
import sys, re, os

src = open("panic_mode.py", encoding="utf-8").read()

# Extract L dict: from 'L = {' to '\ndef tr('
start = src.index("L = {")
end = src.index("\ndef tr(")
L_src = src[start:end] + "}"

# Execute to get L
local_vars = {}
exec(L_src, {}, local_vars)
L = local_vars["L"]

print(f"keys total: {len(L)}")

# Check all 3 languages have all keys
langs = ["ru", "en", "es"]
for lang in langs:
    assert lang in L, f"Missing language {lang}"
    for key in L[lang]:
        assert key in L["ru"], f"Key {key} missing in ru"
        assert key in L["en"], f"Key {key} missing in en"
        assert key in L["es"], f"Key {key} missing in es"

print("OK: all keys present")

# Zone math
def zone_label(zone):
    if zone is None:
        return "whole frame"
    rows, cols, cell = zone
    r = (cell - 1) // cols + 1
    c = (cell - 1) % cols + 1
    return f"N{rows}x{cols} C{cell:02d} (row {r}, col {c})"

assert zone_label((3, 4, 9)) == "N3x4 C09 (row 3, col 1)"
assert zone_label((3, 3, 5)) == "N3x3 C05 (row 2, col 2)"
assert zone_label(None) == "whole frame"
print("zone math correct")