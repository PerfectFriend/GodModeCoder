# Target-Driven Detection: /target Text Controls Real YOLO Filter

**Problem**: User sets `/target red car` but the detector is still hardcoded to yellow HSV. The target text was just a label, not driving the actual detection logic.

**Solution**: Parse free-text `/target` into (YOLO classes, HSV color ranges) that directly drive `detect_vehicles()`.

## Architecture (from panic_mode.py)

```python
# Synonym dictionaries (3 languages: RU/EN/ES)
CLASS_MAP = {
    0: ["person", "people", "human", "humanos", "люди", "человек", "standing", "standing", "стоя", "de pie"],
    2: ["car", "cars", "coche", "coches", "auto", "autos", "automóvil", "carro", "carros",
        "машина", "машину", "автомобиль", "автомобиля", "легковой", "авто", "автомобили"],
    5: ["bus", "buses", "autobus", "autobuses", "автобус", "автобуса"],
    7: ["truck", "trucks", "camion", "camiones", "грузовик", "грузовика", "грузовики"],
}

COLOR_MAP = {
    # Each color = list of (low_HSV, high_HSV) pairs
    # RED is TWO ranges (OpenCV H wraps at 180): 0-10 AND 170-180
    "red": [((0,100,80),(10,255,255)), ((170,100,80),(180,255,255))],
    "yellow": [((15,60,80),(40,255,255))],
    "orange": [((10,100,80),(20,255,255))],
    # ... 7 more colors
}

# parse_target() returns (classes_set, color_ranges_list) or (None, None) = keep current
def parse_target(text):
    tokens = re.split(r"[^a-zа-яё0-9]+", text.lower())
    classes, color_names = set(), set()
    for tok in tokens:
        if tok in CLASS_WORDS: classes.add(CLASS_WORDS[tok])
        if tok in COLOR_WORDS: color_names.add(COLOR_WORDS[tok])
    if not classes and not color_names:
        return None, None  # keep current filter
    if not classes: classes = VEHICLE_CLASSES  # color only -> all vehicles
    ranges = [r for cn in color_names for r in COLOR_MAP.get(cn, [])]
    return classes, ranges

# detect_vehicles() uses:
#   if TARGET_CLASSES: filter r.boxes.cls in TARGET_CLASSES
#   if COLOR_RANGES:   require color_fraction(box) >= 0.15
# color_fraction() ORs cv2.inRange masks across ALL active ranges
```

## Key Design Decisions

1. **Class only (e.g. "person standing") → NO color filter** — night/IR washes out color
2. **Color only (e.g. "blue") → all vehicle classes + that color**
3. **Nothing recognized → keep current filter** + "не распознал цвет/класс — фильтр не менялся"
4. **Persistence**: only target TEXT saved; on load_settings() filter re-derived via parse_target()
5. **Static test**: scripts/check_target_parse.py slices parse_target + dicts, exec's them (no YOLO boot)

## PITFALL — Multi-range colors MUST be nested pairs (bot died 2026-08-06)

```python
# WRONG (flat list - yellow worked, red crashed on unpack):
"red": [(0,100,80),(10,255,255),(170,100,80),(180,255,255)]

# CORRECT (list of pairs):
"red": [((0,100,80),(10,255,255)), ((170,100,80),(180,255,255))]
```

The unpack loop `for lo, hi in COLOR_RANGES` raises `ValueError: too many values to unpack` on flat lists. Yellow (one pair) worked, so the bug hid until user switched to `/target red car` — process exited silently, bot went SILENT (no crash report to user).

**Guard**: Add static structure check over COLOR_MAP in test script (every element len==2, each tuple len==3).