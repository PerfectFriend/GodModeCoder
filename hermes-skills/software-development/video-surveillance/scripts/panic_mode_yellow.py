#!/usr/bin/env python3
"""SuperGuard PANIC MODE v7 FINAL - YOLO sees a YELLOW vehicle -> alarm.
- msg A: trigger frame (what YOLO reacted to) - NEVER edited, NO BUTTON (clean
  photo), kept for audit; user removes it manually.
- msg B: live frame - updated every 2s via editMessageMedia (unique filename).
- NO inline buttons under photos AT ALL (client final: "кнопки под картинками
  убираем"). ALL control lives in the BOT MENU BUTTON next to the paperclip:
  setChatMenuButton(type=commands) + setMyCommands -> /autoguard (toggle AUTO
  mode), /togglealarm (force alarm ON/OFF), /zone (grid zone), /target (desc).
  Commands arrive as TEXT messages and are handled in the poll loop (match with
  and without @botusername suffix). /alarmoff was REMOVED (client: "убери она
  точно лишняя") - /togglealarm covers both directions. /auto and /stop were
  renamed - they collided with other bots.
- Manual cancel (/togglealarm when active): plug OFF + delete msg B only (msg A stays).
- AUTO mode (/autoguard): plug OFF automatically when yellow vehicle leaves the
  frame (5 clean frames); deletes live frame (msg B), KEEPS msg A in history,
  sends "Угроза устранена" text with the CURRENT MODE in the same message.
- Zone targeting (/zone N3x4 C9): grid split, cells C01..C12 left->right
  top->bottom; only objects whose CENTER falls in the cell are considered.
  /target <text> = free-text "what we search for", shown in alarm captions.
- Config from standalone sguard.env (own alarm bot token!) - the Hermes gateway
  long-polls ITS token; a second poller on the same token = 409 and dead
  buttons. Separate bot + same chat_id = buttons always work.
- PITFALL: no edit* helper may carry reply_markup either - a stale
  editMessageText with a keyboard resurrects buttons on every toggle.
VALIDATED 2026-08-06: yellow bus 18-65% fraction, non-yellow cars 0-5%;
menu commands verified working on the dedicated bot; zone C05 (center of 3x3)
verified live.
"""
import os, time, json, threading, hashlib, re
import requests
import cv2
import numpy as np
import tinytuya
from ultralytics import YOLO

# ---------------- config: standalone sguard.env (own bot, NOT hermes .env) ----
BASE = os.path.dirname(os.path.abspath(__file__))

def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

env = load_env(os.path.join(BASE, "sguard.env"))
TOKEN = env.get("SG_TELEGRAM_BOT_TOKEN")
CHAT_ID = int(env.get("SG_CHAT_ID", "143293811"))
PLUG_IP = env.get("SG_PLUG_IP", "192.168.137.109")
PLUG_ID = env.get("SG_PLUG_ID")
PLUG_KEY = env.get("SG_PLUG_KEY")
BOT_USERNAME = env.get("SG_BOT_USERNAME", "superguard_alarm_bot")
if not TOKEN:
    raise SystemExit("SG_TELEGRAM_BOT_TOKEN not set in sguard.env (create your own alarm bot via @BotFather)")
if not PLUG_ID or not PLUG_KEY:
    raise SystemExit("SG_PLUG_ID / SG_PLUG_KEY not set in sguard.env")

CAM_URL = env.get("SG_CAM_URL", "https://atcs.banjarkota.go.id:5443/LiveApp/streams/Ptzparungsari.m3u8")
UPDATE_EVERY = float(env.get("SG_UPDATE_EVERY", "2.0"))
DETECT_EVERY = float(env.get("SG_DETECT_EVERY", "1.5"))
YELLOW_MIN_FRACTION = float(env.get("SG_YELLOW_MIN_FRACTION", "0.15"))
MIN_CONF = float(env.get("SG_MIN_CONF", "0.35"))
MIN_YELLOW_VEHICLES = int(env.get("SG_MIN_YELLOW_VEHICLES", "1"))
REQUIRE_FRAMES = int(env.get("SG_REQUIRE_FRAMES", "2"))
AUTO_RESOLVE_FRAMES = int(env.get("SG_AUTO_RESOLVE_FRAMES", "5"))
VEHICLE_CLASSES = {2: "car", 5: "bus", 7: "truck"}

# ---------------- zone targeting (grid) ----------------
# ZONE = (rows, cols, cell_num) e.g. (3, 4, 9) = N3x4 C9 -> left-bottom corner.
# None = whole frame. Cell numbering: left->right, top->bottom, C01..C12.
ZONE = None
TARGET_DESC = "жёлтый автомобиль (такси/служебный транспорт)"

def parse_zone(spec):
    """Parse 'N3x4 C9' / 'N9 C5' (square grids) / '3x4 c9' -> (rows, cols, cell) or None.
    Canonical syntax uses ENGLISH 'x' (client correction 2026-08-06); Cyrillic
    'х' is still tolerated as a convenience."""
    if not spec:
        return None
    s = spec.strip().lower().replace("х", "x").replace(" ", "").replace("_", "")
    m = re.fullmatch(r"n?(\d+)x(\d+)c(\d+)", s)
    if m:
        rows, cols, cell = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if cell < 1 or cell > rows * cols:
            return None
        return (rows, cols, cell)
    m = re.fullmatch(r"n(\d+)c(\d+)", s)   # N9 C5 -> 3x3 grid, cell 5
    if m:
        total, cell = int(m.group(1)), int(m.group(2))
        side = int(total ** 0.5)
        if side * side == total and 1 <= cell <= total:
            return (side, side, cell)
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

Y_LOW = np.array([15, 60, 80])    # HSV yellow range (OpenCV H:0-180)
Y_HIGH = np.array([40, 255, 255])

FRAME_DIR = os.path.join(BASE, "panic_frames")
os.makedirs(FRAME_DIR, exist_ok=True)

ALERT_TEXT = ("\u26a0\ufe0f ВНИМАНИЕ! ТРЕВОГА! СИГНАЛИЗАЦИЯ ВКЛЮЧЕНА!\n"
              "ДЛЯ ОТКЛЮЧЕНИЯ СИГНАЛИЗАЦИИ НАЖМИТЕ КНОПКУ!")

API = f"https://api.telegram.org/bot{TOKEN}"

# ---------------- telegram ----------------
def tg(method, **kwargs):
    r = requests.post(f"{API}/{method}", timeout=15, **kwargs)
    j = r.json()
    if not j.get("ok"):
        print(f"  TG ERROR {method}: {j}", flush=True)
    return j.get("result")

def set_bot_menu():
    """Menu button next to the paperclip: /autoguard, /togglealarm, /zone, /target.
    Commands arrive as TEXT messages and are handled in poll_loop."""
    tg("setMyCommands", data={"commands": json.dumps([
        {"command": "autoguard", "description": "Авторежим: вкл/выкл"},
        {"command": "togglealarm", "description": "Тревога вкл/выкл вручную"},
        {"command": "zone", "description": "Зона поиска: /zone N3x4 C9"},
        {"command": "target", "description": "Цель поиска: /target текст"}])})
    tg("setChatMenuButton", data={"chat_id": CHAT_ID,
                                  "menu_button": json.dumps({"type": "commands"})})

def send_photo(frame_bytes, caption):
    files = {"photo": ("frame.jpg", frame_bytes, "image/jpeg")}
    data = {"chat_id": CHAT_ID, "caption": caption}
    return tg("sendPhoto", files=files, data=data)

def send_control_msg(auto_on):
    txt = ("\u2699\ufe0f РЕЖИМ РАБОТЫ\n\n"
           "Текущий режим: " + ("\u2705 АВТОМАТИЧЕСКИЙ" if auto_on else "\U0001F6AB РУЧНОЙ") + "\n"
           "\u2022 Авто: розетка отключится сама, когда жёлтый автомобиль исчезнет\n"
           "\u2022 Ручной: отключение командой /togglealarm\n\n"
           "\U0001F4CD Управление: меню рядом со скрепкой \u2192 /autoguard и /togglealarm")
    return tg("sendMessage", data={"chat_id": CHAT_ID, "text": txt})

def edit_control_msg(msg_id, auto_on):
    # NO reply_markup here - a stale keyboard here resurrects buttons on toggle
    txt = ("\u2699\ufe0f РЕЖИМ РАБОТЫ\n\n"
           "Текущий режим: " + ("\u2705 АВТОМАТИЧЕСКИЙ" if auto_on else "\U0001F6AB РУЧНОЙ") + "\n"
           "\u2022 Авто: розетка отключится сама, когда жёлтый автомобиль исчезнет\n"
           "\u2022 Ручной: отключение командой /togglealarm")
    return tg("editMessageText", data={"chat_id": CHAT_ID, "message_id": msg_id,
                                       "text": txt})

def edit_photo(frame_bytes, message_id, caption):
    fname = f"frame_{int(time.time()*1000)}.jpg"  # unique name - Telegram caches by filename
    files = {fname: frame_bytes}
    media = {"type": "photo", "media": f"attach://{fname}", "caption": caption}
    return tg("editMessageMedia", files=files,
              data={"chat_id": CHAT_ID, "message_id": message_id,
                    "media": json.dumps(media)})

def delete_msg(mid):
    return tg("deleteMessage", data={"chat_id": CHAT_ID, "message_id": mid})

def send_text(text):
    return tg("sendMessage", data={"chat_id": CHAT_ID, "text": text})

# ---------------- plug ----------------
def plug_set(on):
    d = tinytuya.Device(PLUG_ID, PLUG_IP, PLUG_KEY, version=3.4)
    d.set_socketTimeout(5)
    r = d.set_status(bool(on), 1)
    print(f"  PLUG {'ON' if on else 'OFF'}: ack={r.get('dps') if isinstance(r, dict) else r}", flush=True)
    return r

# ---------------- camera: continuous bg capture ----------------
class Camera:
    """Daemon thread reads the stream in a tight loop, stores latest frame under lock.
    Single persistent VideoCapture serves frames from HLS buffer IN ORDER (feed looks
    frozen); reopening per frame costs ~4 s. Thread pattern = sub-ms fresh grabs."""
    def __init__(self, url):
        self.url = url
        self.lock = threading.Lock()
        self.frame = None
        self.alive = False
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            try:
                cap = cv2.VideoCapture(self.url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                while True:
                    ok, f = cap.read()
                    if not ok:
                        break
                    with self.lock:
                        self.frame = f.copy()
                        self.alive = True
            except Exception:
                pass
            with self.lock:
                self.alive = False
            time.sleep(2)

    def latest(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

CAM = Camera(CAM_URL)
MODEL = YOLO("yolo11n.pt")

def yellow_fraction(frame, box):
    """Fraction of yellow pixels in central body zone (skips roof glare/bumpers)."""
    x1, y1, x2, y2 = [int(v) for v in box]
    cx = (x1 + x2) // 2
    w, h = x2 - x1, y2 - y1
    if w < 20 or h < 20:
        return 0.0
    zone = frame[max(y1, y1 + h // 4):y2, max(x1, cx - w // 5):min(x2, cx + w // 5)]
    if zone.size == 0:
        return 0.0
    hsv = cv2.cvtColor(zone, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, Y_LOW, Y_HIGH)
    return float(mask.mean() / 255.0)

def detect_vehicles(frame):
    """Returns (yellow, all) lists of (name, conf, box, yellow_frac), zone-filtered."""
    r = MODEL(frame, conf=MIN_CONF, imgsz=640, verbose=False)[0]
    H, W = frame.shape[:2]
    yellow, allv = [], []
    for b in r.boxes:
        cls = int(b.cls[0])
        if cls in VEHICLE_CLASSES:
            box = b.xyxy[0].tolist()
            name = VEHICLE_CLASSES[cls]
            conf = float(b.conf[0])
            if not in_zone(ZONE, box, W, H):
                continue          # outside the zone: ignore entirely
            yf = yellow_fraction(frame, box)
            item = (name, conf, box, yf)
            allv.append(item)
            if yf >= YELLOW_MIN_FRACTION:
                yellow.append(item)
    return yellow, allv

# ---------------- alarm state ----------------
class Alarm:
    def __init__(self):
        self.active = False
        self.auto = False           # auto mode: plug OFF when yellow leaves frame
        self.trigger_msg_id = None  # msg A: trigger frame - NEVER edited, NO button
        self.live_msg_id = None     # msg B: live frame - updated, deleted on stop
        self.control_msg_id = None  # mode info message (NOT deleted on cancel)
        self.known = set()
        self.lock = threading.Lock()

alarm = Alarm()

def annotate(frame, yellow, allv):
    out = frame.copy()
    H, W = out.shape[:2]
    if ZONE is not None:
        rows, cols, cell = ZONE
        r, c = divmod(cell - 1, cols)
        x1 = c * W // cols; x2 = (c + 1) * W // cols
        y1 = r * H // rows; y2 = (r + 1) * H // rows
        cv2.rectangle(out, (x1, y1), (x2, y2), (255, 165, 0), 2)
        cv2.putText(out, f"ZONE N{rows}x{cols} C{cell:02d}", (x1 + 4, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
    for name, conf, box, yf in allv:
        x1, y1, x2, y2 = [int(v) for v in box]
        is_y = any(y == box for _, _, y, _ in yellow)
        color = (0, 0, 255) if is_y else (0, 255, 0)
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        cv2.putText(out, f"{name} {conf:.2f}{' YELLOW' if is_y else ''}",
                    (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    cv2.putText(out, f"yellow: {len(yellow)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    return out

def trigger_alarm(desc, frame):
    with alarm.lock:
        if alarm.active:
            print("  already active, ignore", flush=True)
            return
        alarm.active = True
    print("== PANIC TRIGGER ==", flush=True)
    plug_set(True)
    # msg A: trigger frame - clean photo, NO button; caption carries target + zone
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    frame_bytes = buf.tobytes()
    caption = (f"{ALERT_TEXT}\n\n\U0001F4C5 {time.strftime('%H:%M:%S')}\n{desc}"
               f"\n\U0001F50D Ищем: {TARGET_DESC}\n\U0001F4CD Зона: {zone_label(ZONE)}\n\n"
               f"\U0001F4F7 кадр срабатывания")
    res = send_photo(frame_bytes, caption)
    if not res:
        alarm.active = False
        return
    alarm.trigger_msg_id = res["message_id"]
    alarm.known.add(res["message_id"])
    save_local(frame_bytes)
    print(f"  trigger photo sent, msg_id={alarm.trigger_msg_id} (no button)", flush=True)
    # msg B: fresh live frame - gets the 2s updates (no inline button; menu commands)
    time.sleep(1.0)
    live = CAM.latest()
    if live is None:
        live = frame
    ok, buf = cv2.imencode(".jpg", live, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    caption = f"{ALERT_TEXT}\n\n\U0001F4C5 {time.strftime('%H:%M:%S')}\n\U0001F4FA живой кадр"
    res = send_photo(buf.tobytes(), caption)
    if res:
        alarm.live_msg_id = res["message_id"]
        alarm.known.add(res["message_id"])
        save_local(buf.tobytes())
        print(f"  live photo sent, msg_id={alarm.live_msg_id}", flush=True)
        threading.Thread(target=update_loop, daemon=True).start()

def save_local(frame_bytes):
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(FRAME_DIR, f"panic_{ts}_{hashlib.md5(frame_bytes).hexdigest()[:6]}.jpg")
    with open(path, "wb") as f:
        f.write(frame_bytes)

def update_loop():
    while True:
        time.sleep(UPDATE_EVERY)
        with alarm.lock:
            if not alarm.active:
                return
            mid = alarm.live_msg_id
        if mid is None:
            continue
        frame = CAM.latest()
        if frame is None:
            continue
        ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        caption = f"{ALERT_TEXT}\n\n\U0001F4C5 {time.strftime('%H:%M:%S')}\n\U0001F4FA живой кадр"
        if edit_photo(buf.tobytes(), mid, caption):
            save_local(buf.tobytes())
            print(f"  live photo updated {time.strftime('%H:%M:%S')}", flush=True)

def stop_alarm(clear_chat, note):
    """End alarm: plug OFF, stop updates.
    ALWAYS deletes every alarm msg EXCEPT the trigger frame (msg A) - it stays
    in history for audit; the user removes it manually (client decision: 'не
    надо его удалять вообще. пользователь руками удалит'). In auto mode
    (note non-empty) also send the 'Угроза устранена' summary text WITH the
    current mode in the SAME message (client: no separate mode-status msg;
    'про живой кадр удалён это лишнее' - keep it minimal)."""
    with alarm.lock:
        if not alarm.active:
            return
        alarm.active = False
        keep = alarm.trigger_msg_id
        mids = [m for m in alarm.known if m != keep]
        alarm.known.clear()
        alarm.live_msg_id = None
    plug_set(False)
    for mid in mids:
        try:
            delete_msg(mid)
            print(f"  deleted msg {mid}", flush=True)
        except Exception as e:
            print(f"  del {mid} err {e}", flush=True)
    if note:
        mode_txt = ("\u2705 АВТОРЕЖИМ АКТИВЕН" if alarm.auto else
                    "\U0001F6AB РУЧНОЙ РЕЖИМ АКТИВЕН")
        send_text(f"\u2705 {note}\n\n\U0001F6A8 Сигнализация отключена.\n"
                  f"\U0001F4CC Текущий режим: {mode_txt}\n"
                  f"\U0001F50D Цель: {TARGET_DESC}\n"
                  f"\U0001F4CD Зона: {zone_label(ZONE)}")
        print("  plug OFF, live frame removed, trigger frame kept", flush=True)
    else:
        print(f"  chat cleaned (trigger msg {keep} kept), plug OFF", flush=True)

def cancel_alarm():
    stop_alarm(clear_chat=True, note="")

def toggle_alarm():
    """Force alarm ON (even without yellow detection) or OFF manually."""
    with alarm.lock:
        active = alarm.active
    if active:
        cancel_alarm()
        send_text("\U0001F6A8 Сигнализация выключена вручную (команда togglealarm).")
    else:
        frame = CAM.latest()
        if frame is None:
            send_text("\u26a0\ufe0f Камера недоступна — не могу включить тревогу.")
            return
        desc = (f"\U0001F6A8 ПРИНУДИТЕЛЬНАЯ ТРЕВОГА (вручную)\n"
                f"\U0001F50D Ищем: {TARGET_DESC}\n"
                f"\U0001F4CD Зона: {zone_label(ZONE)}")
        trigger_alarm(desc, annotate(frame, [], []))
        send_text("\U0001F6A8 Тревога включена вручную (команда togglealarm). "
                  "Отключение — повторная команда togglealarm.")

def _handle_zone_cmd(text):
    """/zone N3x4 C9 | /zone N9 C5 | /zone off | /zone ? — set/clear/show zone."""
    global ZONE
    arg = text[len("/zone"):].strip()
    if not arg or arg in ("?", "help", "справка"):
        send_text(f"\U0001F4CD Текущая зона поиска: {zone_label(ZONE)}\n\n"
                  f"Формат: /zone N3x4 C9\n"
                  f"• N{'{'}строк{'}'}x{'{'}столбцов{'}'} — разбиение кадра (1x2, 2x2, 2x3, 3x3, 3x4...)\n"
                  f"• C{'{'}номер{'}'} — ячейка слева направо, сверху вниз (C01..C12)\n"
                  f"• N9 C5 — квадратное разбиение 3x3, ячейка 5\n"
                  f"• /zone off — весь кадр")
        return
    if arg in ("off", "none", "всё", "все", "0"):
        ZONE = None
        send_text("\U0001F4CD Зона поиска: ВЕСЬ КАДР (зона выключена).")
        return
    z = parse_zone(arg)
    if z is None:
        send_text(f"\u26a0\ufe0f Не понял формат «{arg}». Пример: /zone N3x4 C9 (левая нижняя ячейка при 3 строках, 4 столбцах).")
        return
    ZONE = z
    send_text(f"\U0001F4CD Зона поиска установлена: {zone_label(z)}.\n"
              f"\U0001F50D Ищем только жёлтые автомобили в этой ячейке.")

def _handle_target_cmd(text):
    """/target <описание> — что именно ищем (показывается в алертах)."""
    global TARGET_DESC
    arg = text[len("/target"):].strip()
    if not arg or arg in ("?", "help", "справка"):
        send_text(f"\U0001F50D Текущая цель поиска: {TARGET_DESC}\n"
                  f"Задать: /target человек в положении стоя")
        return
    TARGET_DESC = arg
    send_text(f"\U0001F50D Цель поиска обновлена: {TARGET_DESC}")

def toggle_auto():
    with alarm.lock:
        alarm.auto = not alarm.auto
        auto = alarm.auto
        cid = alarm.control_msg_id
    print(f"  AUTO mode {'ON' if auto else 'OFF'}", flush=True)
    if cid:
        edit_control_msg(cid, auto)   # NO reply_markup inside - see pitfall
    # always reply with which mode is now active (client rule)
    if auto:
        send_text("\u2705 АВТОРЕЖИМ ВКЛЮЧЁН\n\n"
                  "Розетка отключится автоматически, когда жёлтый автомобиль "
                  "исчезнет из кадра (5 чистых кадров). Ручное отключение — /togglealarm.")
    else:
        send_text("\U0001F6AB АВТОРЕЖИМ ВЫКЛЮЧЕН — РУЧНОЙ РЕЖИМ\n\n"
                  "Тревогу можно отключить только командой /togglealarm из меню.")

# ---------------- poll loop (bot menu commands arrive as text messages) -------
def poll_loop():
    offset = 0
    while True:
        try:
            j = requests.post(f"{API}/getUpdates",
                              json={"offset": offset, "timeout": 25},
                              timeout=35).json()
            if not j.get("ok"):
                print(f"  poll warn: {j.get('description')}", flush=True)
                time.sleep(1)
                continue
            for upd in j["result"]:
                offset = upd["update_id"] + 1
                if "callback_query" in upd:
                    # legacy inline buttons (only if someone re-introduces them)
                    cb = upd["callback_query"]
                    if cb.get("data") == "cancel_alarm":
                        cancel_alarm()
                    elif cb.get("data") == "auto_toggle":
                        toggle_auto()
                elif "message" in upd:
                    m = upd["message"]
                    mid = m.get("message_id")
                    if mid:
                        alarm.known.add(mid)
                    text = (m.get("text") or "").strip().lower()
                    # match with and without @botusername suffix (groups append it)
                    if text in (f"/autoguard", f"/autoguard@{BOT_USERNAME}"):
                        toggle_auto()
                    elif text in (f"/togglealarm", f"/togglealarm@{BOT_USERNAME}"):
                        toggle_alarm()
                    elif text.startswith("/zone"):
                        _handle_zone_cmd(text)
                    elif text.startswith("/target"):
                        _handle_target_cmd(text)
                    elif mid:
                        try:  # any other user message: keep the chat clean
                            delete_msg(mid)
                        except Exception:
                            pass
        except Exception as e:
            print(f"  poll err {e}", flush=True)
            time.sleep(2)

# ---------------- main detection loop ----------------
def detection_loop():
    streak = 0
    clean = 0   # consecutive frames without yellow (auto-resolve counter)
    while True:
        time.sleep(DETECT_EVERY)
        frame = CAM.latest()
        if frame is None:
            continue
        yellow, allv = detect_vehicles(frame)
        if len(yellow) >= MIN_YELLOW_VEHICLES:
            streak += 1
            clean = 0
        else:
            streak = 0
            clean += 1
        status = (f"[{time.strftime('%H:%M:%S')}] yellow={len(yellow)}/{MIN_YELLOW_VEHICLES} "
                  f"streak={streak}/{REQUIRE_FRAMES} clean={clean}/{AUTO_RESOLVE_FRAMES} "
                  f"zone={zone_label(ZONE)} | "
                  + ", ".join(f"{n} c={c:.2f} y={y*100:.0f}%" for n, c, _, y in allv) or "empty")
        print(status, flush=True)
        # fire alarm
        if streak >= REQUIRE_FRAMES and not alarm.active:
            y = yellow[0]
            desc = (f"\U0001F697 ОБНАРУЖЕН ЖЁЛТЫЙ АВТОМОБИЛЬ!\n"
                    f"({y[0]} conf={y[1]:.2f}, yellow={y[3]*100:.0f}%)")
            trigger_alarm(desc, annotate(frame, yellow, allv))
        # auto-resolve: threat gone while alarm active in AUTO mode
        elif alarm.active and alarm.auto and clean >= AUTO_RESOLVE_FRAMES:
            stop_alarm(clear_chat=False, note="Угроза устранена (жёлтый автомобиль покинул кадр)")

if __name__ == "__main__":
    threading.Thread(target=poll_loop, daemon=True).start()
    time.sleep(2)
    set_bot_menu()   # /autoguard, /togglealarm, /zone, /target next to the paperclip
    res = send_control_msg(alarm.auto)
    if res:
        alarm.control_msg_id = res["message_id"]
    print("SuperGuard panic mode: watching for YELLOW vehicle...", flush=True)
    detection_loop()
