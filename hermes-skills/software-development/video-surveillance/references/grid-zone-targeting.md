# Grid zone targeting — working implementation (panic_mode.py v4, 2026-08-06)

Client-specified feature: split the frame into a grid (1x2, 2x2, 2x3, 3x3, 3x4, 4x3, ...),
number cells C01..C12 left→right top→bottom, and search only inside the chosen cell.
Plus a free-text target description. All validated live on the Banjar camera.

## Commands (arrive as plain text messages in the poll loop)

| Command | Effect |
|---|---|
| `/zone N3x4 C9` | set zone: 3 rows × 4 cols, cell 9 (left-bottom corner). Accepts Cyrillic `х`, no spaces, lowercase: `n3х4c9` |
| `/zone N9 C5` | square shorthand: 9 cells = 3×3 grid, cell 5 (only perfect squares) |
| `/zone off` / `none` / `0` / `всё` | clear zone → whole frame |
| `/zone ?` / empty | help text + current zone |
| `/target <текст>` | set what we search for (shown in alerts) |
| `/target ?` / empty | show current target |
| `/togglealarm` | force alarm ON (or OFF if active) regardless of YOLO — manual test/demo |

## Full code (glue-in)

```python
# ---- globals ----
ZONE = None                 # (rows, cols, cell) or None = whole frame
TARGET_DESC = "жёлтый автомобиль (такси/служебный транспорт)"

# ---- parsing ----
def parse_zone(spec):
    if not spec:
        return None
    s = spec.strip().lower().replace("х", "x").replace(" ", "").replace("_", "")
    m = re.fullmatch(r"n?(\d+)x(\d+)c(\d+)", s)          # N3x4 C9 / 3x4c9
    if m:
        rows, cols, cell = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return (rows, cols, cell) if 1 <= cell <= rows * cols else None
    m = re.fullmatch(r"n(\d+)c(\d+)", s)                 # N9 C5 -> 3x3 square
    if m:
        total, cell = int(m.group(1)), int(m.group(2))
        side = int(total ** 0.5)
        return (side, side, cell) if side * side == total and 1 <= cell <= total else None
    return None

def in_zone(zone, box, W, H):
    """True if object center falls inside the zone cell (normalized 0-1 coords)."""
    if zone is None:
        return True
    rows, cols, cell = zone
    r, c = divmod(cell - 1, cols)
    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2 / W
    cy = (y1 + y2) / 2 / H
    return (c / cols <= cx <= (c + 1) / cols and
            r / rows <= cy <= (r + 1) / rows)

def zone_label(zone):
    if zone is None:
        return "весь кадр"
    rows, cols, cell = zone
    return (f"N{rows}x{cols} C{cell:02d} "
            f"(строка {cell // cols + (1 if cell % cols else 0)}, "
            f"столбец {(cell - 1) % cols + 1})")
```

## Wiring

1. **detect_vehicles** — filter BEFORE color test:
```python
H, W = frame.shape[:2]
for b in r.boxes:
    cls = int(b.cls[0])
    if cls in VEHICLE_CLASSES:
        box = b.xyxy[0].tolist()
        if not in_zone(ZONE, box, W, H):
            continue          # object outside the zone: ignore entirely
        yf = yellow_fraction(frame, box)
        ...
```
2. **annotate** — draw zone as orange rectangle + label (visible on msg A trigger frame):
```python
if ZONE is not None:
    rows, cols, cell = ZONE
    r, c = divmod(cell - 1, cols)
    x1 = c * W // cols; x2 = (c + 1) * W // cols
    y1 = r * H // rows; y2 = (r + 1) * H // rows
    cv2.rectangle(out, (x1, y1), (x2, y2), (255, 165, 0), 2)
    cv2.putText(out, f"ZONE N{rows}x{cols} C{cell:02d}", (x1 + 4, y1 + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
```
3. **Status log line**: append `zone={zone_label(ZONE)}` — verified output:
   `[08:10:26] yellow=0/1 streak=0/2 clean=1/5 zone=весь кадр | car c=0.81 ...`
4. **Alarm caption (msg A)** — append both lines:
```python
caption = (f"{ALERT_TEXT}\n\n{time}\n{desc}"
           f"\n🔍 Ищем: {TARGET_DESC}\n📌 Зона: {zone_label(ZONE)}\n\n📷 кадр срабатывания")
```
5. **Resolve message («Угроза устранена»)** — same pattern: append
   `📌 Текущий режим: …`, `🔍 Цель: {TARGET_DESC}`, `📌 Зона: {zone_label(ZONE)}`
   in the SAME message (client explicitly: no separate mode-status message).

## Handler code (poll loop, message branch)

```python
def control_text(auto_on):
    """ONE source of truth for the ⚙️ РЕЖИМ РАБОТЫ message — built from LIVE globals."""
    mode = "✅ АВТОМАТИЧЕСКИЙ" if auto_on else "⛔ РУЧНОЙ"
    return ("⚙️ РЕЖИМ РАБОТЫ\n\n"
            f"📌 Текущий режим: {mode}\n"
            f"📌 Зона поиска: {zone_label(ZONE)}\n"
            f"🔍 Цель поиска: {TARGET_DESC}\n\n"
            "💡 Управление: меню рядом со скрепкой → /autoguard, /togglealarm, /zone, /target")

def _refresh_control_msg():
    """Keep the pinned mode message in sync after /zone, /target, /autoguard changes."""
    with alarm.lock:
        cid = alarm.control_msg_id
        auto = alarm.auto
    if cid:
        edit_control_msg(cid, auto)     # editMessageText(control_text(auto))

def _handle_zone_cmd(text):
    global ZONE
    arg = text[len("/zone"):].strip()
    if not arg or arg in ("?", "help", "справка"):
        send_text(f"📌 Текущая зона поиска: {zone_label(ZONE)}\n\n"
                  f"Формат: /zone N3x4 C9\n• N{'{'}строк{'}'}x{'{'}столбцов{'}'} — разбиение (1x2, 2x2, 3x3, 3x4...)\n"
                  f"• C{'{'}номер{'}'} — ячейка слева направо, сверху вниз (C01..C12)\n"
                  f"• N9 C5 — квадратное разбиение 3x3, ячейка 5\n• /zone off — весь кадр")
        return
    if arg in ("off", "none", "всё", "все", "0"):
        ZONE = None
        send_text("📌 Зона поиска: ВЕСЬ КАДР (зона выключена).")
        _refresh_control_msg()
        return
    z = parse_zone(arg)
    if z is None:
        send_text(f"⚠️ Не понял формат «{arg}». Пример: /zone N3x4 C9 (левая нижняя ячейка при 3 строках, 4 столбцах).")
        return
    ZONE = z
    send_text(f"📌 Зона поиска установлена: {zone_label(z)}.\n🔍 Ищем только жёлтые автомобили в этой ячейке.")
    _refresh_control_msg()

def _handle_target_cmd(text):
    global TARGET_DESC
    arg = text[len("/target"):].strip()
    if not arg or arg in ("?", "help", "справка"):
        send_text(f"🔍 Текущая цель поиска: {TARGET_DESC}\nЗадать: /target человек в положении стоя")
        return
    TARGET_DESC = arg
    send_text(f"🔍 Цель поиска обновлена: {TARGET_DESC}")
    _refresh_control_msg()

def toggle_alarm():
    """Force alarm ON (even without yellow detection) or OFF manually."""
    active = alarm.active          # under alarm.lock
    if active:
        cancel_alarm()
        send_text("🚨 Сигнализация выключена вручную (команда togglealarm).")
    else:
        frame = CAM.latest()
        if frame is None:
            send_text("⚠️ Камера недоступна — не могу включить тревогу.")
            return
        desc = (f"🚨 ПРИНУДИТЕЛЬНАЯ ТРЕВОГА (вручную)\n🔍 Ищем: {TARGET_DESC}\n📌 Зона: {zone_label(ZONE)}")
        trigger_alarm(desc, annotate(frame, [], []))
        send_text("🚨 Тревога включена вручную (команда togglealarm). Отключение — повторная команда togglealarm.")
```

## Parser verification (unit tests that pass)

```
'N3x4 C9'  -> (3, 4, 9)     'N3х4 C9' -> (3, 4, 9)   # Cyrillic х works
'N9 C5'    -> (3, 3, 5)     '3x4c9'   -> (3, 4, 9)   # no spaces
'N2x2 C4'  -> (2, 2, 4)     'N1x2 C1' -> (1, 2, 1)
'N12 C6'   -> None (12 not a perfect square)  'N3x4 C13' -> None (out of range)
'garbage'  -> None          'N3x4 C0'  -> None (cell 0 invalid)
```

## Rules that shipped alongside (client verbatim, 2026-08-06)

- «после выполнения команды autoguard нужно выдать сообщение - какой именно режим включен» —
  `/autoguard` ALWAYS replies with the now-active mode; never toggle silently.
- «в том же сообщение где сообщается об устранении угрозы и отключении сигнализации -
  сообщай - какой режим работы сейчас активен. не нужно для этого городить отдельное
  сообщение» — mode goes INTO the resolve message, no separate message.
- «про живой кадр удалён это лишнее» — do NOT add "живой кадр удалён…" detail to the
  resolve text; keep it minimal: ✅ note + «🚨 Сигнализация отключена.» + mode + target + zone.
  Final resolve wording is NEUTRAL (not trigger-specific): «Угроза устранена: цель
  покинула зону поиска» — no more «(жёлтый автомобиль покинул кадр)».
- **ALL status texts come from LIVE globals — never hardcode the trigger description.**
  Client flagged TWICE: «в режиме работы всё еще про желтый автомобиль… отображались
  текущие данные из команд zone и target» and «в сообщении АВТОРЕЖИМ ВКЛЮЧЁН всё еще
  вижу про желтый автомобиль. а нужно про zone и target». After /zone or /target
  changes, the pinned ⚙️ РЕЖИМ РАБОТЫ message and the АВТОРЕЖИМ ВКЛЮЧЁН/ВЫКЛЮЧЕН
  replies must reflect the new values — build them via one `control_text(auto_on)`
  and `edit_control_msg()`; never keep a second hand-written copy of the text.
- Commands `/auto` and `/stop` were already taken in the client's bot ecosystem →
  renamed to `/autoguard`, `/alarmoff` (prefix with product name to stay unique);
  LATER `/alarmoff` was fully removed (client: «команду alarmoff убери она точно
  лишняя») since `/togglealarm` covers both directions — menu, handler branch and
  every text mention were deleted; grep the whole script for the command name
  after removal to catch stale references.
