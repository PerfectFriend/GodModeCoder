# Multilingual Target Parsing — COLOR_MAP / CLASS_MAP Design

## Goal
Parse free-text `/target` commands in **RU/EN/ES** into:
- `TARGET_CLASSES` — set of YOLO class IDs {0=person, 2=car, 5=bus, 7=truck}
- `COLOR_RANGES` — list of HSV (low, high) pairs for color filtering

## COLOR_MAP Structure
```python
COLOR_MAP = {
    "yellow": [((15,60,80),(40,255,255))],
    "red": [((0,100,80),(10,255,255)), ((170,100,80),(180,255,255))],
    "orange": [((10,100,80),(20,255,255))],
    "green": [((40,60,80),(80,255,255))],
    "cyan": [((80,60,80),(100,255,255))],
    "blue": [((100,60,80),(130,255,255))],
    "purple": [((130,60,80),(160,255,255))],
    "pink": [((160,60,80),(170,255,255))],
    "white": [((0,0,200),(180,50,255))],
    "gray": [((0,0,80),(180,50,200))],
    "black": [((0,0,0),(180,255,80))],
}
```
**Critical**: Each color value is a **list of (low, high) pairs**.
- Red = 2 pairs (HSV wraps at 180: 0-10 and 170-180)
- All others = 1 pair
- **Bug avoided**: flat list `[(0,100,80),(10,255,255),(170,100,80),(180,255,255)]` causes `ValueError: too many values to unpack` in `color_fraction()`

## CLASS_MAP Structure
```python
CLASS_MAP = {
    0: ["person", "persona", "человек", "люди", "people", "personas", "human", "humano"],
    2: ["car", "cars", "coche", "carros", "auto", "autos", "автомобиль", "автомобили", "машина", "машины", "легковой", "авто"],
    5: ["bus", "autobus", "автобус", "autobús", "автобусы"],
    7: ["truck", "camion", "грузовик", "camión", "грузовики", "camiones"],
}
```
Maps YOLO class ID → list of keywords in RU/EN/ES.

## parse_target() Algorithm
```python
def parse_target(text):
    words = text.lower().split()
    classes = set()
    colors = []
    for w in words:
        # Match class
        for cid, keywords in CLASS_MAP.items():
            if w in keywords:
                classes.add(cid)
        # Match color
        if w in COLOR_MAP:
            colors.extend(COLOR_MAP[w])
    return classes, colors
```

## Behavior
| Input | Classes | Colors | Notes |
|-------|---------|--------|-------|
| `red car` | {2} | red (2 pairs) | color + class |
| `жёлтая машина` | {2} | yellow | RU color + RU class |
| `persona de pie` | {0} | none | ES class, no color |
| `blue` | {2,5,7} | blue | color only → all vehicle classes |
| `truck` | {7} | none | class only, no color filter |
| `любой объект` | none | none | unrecognized → filter unchanged |

## color_fraction() Universal Filter
```python
def color_fraction(frame, box):
    if not COLOR_RANGES:
        return 0.0  # no color filter active
    # Check central body region against ALL active HSV ranges
    for (lo, hi) in COLOR_RANGES:
        mask = cv2.inRange(hsv, np.array(lo), np.array(hi))
        if mask.mean() > THRESHOLD:
            return mask.mean() / 255.0
    return 0.0
```
- Returns pixel fraction matching **ANY** active range
- 0.0 if no color filter (class-only targeting)
- Works for all 11 colors, including dual-range red

## i18n Keys
All messages go through `tr()`:
- `target_current`, `target_set`, `target_hint`, `target_not_set`
- `target_filter`, `target_filter_kept`, `any_color`, `color_filter`
- `yellow_found` (localized per language)