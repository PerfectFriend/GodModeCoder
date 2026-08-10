# 8-Camera Architecture with Numbered Switching (SuperGuard Alarm)

## Overview
SuperGuard Alarm now supports **8 cameras numbered 1-8** with independent zone/target settings per camera, and a single active camera controlled by `/cam 1-8`.

## Architecture

### Camera Configuration (Integer Keys 1-8)
```python
CAMERA_URLS = {
    1: "https://cwwp2.dot.ca.gov/data/d9/cctv/image/sr203mammothmountain/sr203mammothmountain.jpg",
    2: "https://cwwp2.dot.ca.gov/data/d9/cctv/image/us395conwaysummit/us395conwaysummit.jpg",
    3: "https://cwwp2.dot.ca.gov/data/d9/cctv/image/us6stateline/us6stateline.jpg",
    4: "https://cwwp2.dot.ca.gov/data/d9/cctv/image/us395crestview/us395crestview.jpg",
    5: "https://cocam.carsprogram.org/Live_View/I70199RoadSurface.jpg",
    6: "https://itscameras.dot.state.oh.us:443/images/toledo/SR2-EB-Approach.jpg",
    7: "https://itscameras.dot.state.oh.us:443/images/CMH/2134.jpg",
    8: "https://cwwp2.dot.ca.gov/data/d2/cctv/image/i5redding/i5redding.jpg",
}

CAMERA_NAMES = {
    1: "1: CA Mono - Mammoth Mountain",
    2: "2: CA Mono - Conway Summit",
    3: "3: CA Mono - Stateline",
    4: "4: CA Mono - Crestview",
    5: "5: CO DOT - I-70 Road Surface",
    6: "6: OH DOT - Toledo SR-2 EB Approach",
    7: "7: OH DOT - Columbus CMH 2134",
    8: "8: CA DOT - Shasta I-5 Redding",
}

ACTIVE_CAMERA = 1  # Integer 1-8
```

### CameraManager (Integer ID Based)
```python
class CameraManager:
    def __init__(self):
        self.cameras = {}
        self.active_id = ACTIVE_CAMERA  # Integer 1-8
        self._init_all()
    
    def _init_all(self):
        for cam_id, url in CAMERA_URLS.items():
            if not url: continue
            self.cameras[cam_id] = Camera(url, cam_id)
    
    def get_active(self):
        return self.cameras.get(self.active_id)
    
    def set_active(self, cam_id):
        if cam_id in self.cameras:
            self.active_id = cam_id
            return True
        return False
```

### Camera Class (Dual-Mode: JPG + Stream)
```python
class Camera:
    def __init__(self, url, cam_id):
        self.url = url
        self.cam_id = cam_id
        self.name = CAMERA_NAMES.get(cam_id, f"Camera {cam_id}")
        self.is_jpg = self._detect_jpg(url)
        threading.Thread(target=self._loop, daemon=True).start()
    
    def _detect_jpg(self, url):
        url_lower = url.lower()
        return any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', 'snapshot', 'image'])
    
    def _loop(self):
        if self.is_jpg:
            self._loop_jpg()  # requests + cv2.imdecode
        else:
            self._loop_stream()  # cv2.VideoCapture
```

## Bot Commands

| Command | Action |
|---------|--------|
| `/cam 1-8` | Switch active camera |
| `/cam ?` | List 8 cameras with 🟢/🔴 status + `← ACTIVE` marker |
| `/cam status` | Detailed status of all 8 |
| `/zone ...` | Zone of **active** camera |
| `/target ...` | Target of **active** camera |
| `/togglealarm` | Alarm ON/OFF for **active** camera |
| `/autoguard` | Auto-mode for **active** camera |

## Alarm Behavior

### Per-Camera Independent Detection
- Each camera runs its own detection loop in background
- All 8 cameras monitored simultaneously
- Only active camera's commands (`/zone`, `/target`, `/togglealarm`) affect it

### Alarm Trigger Switches Active Camera
```python
def trigger_alarm(desc, frame, cam_id=None):
    if cam_id is not None:
        CAM_MANAGER.set_active(cam_id)
        global CAM, ACTIVE_CAMERA
        CAM = CAM_MANAGER.get_active()
        ACTIVE_CAMERA = cam_id
    # ... send alarm with camera name in caption
```

When any camera detects a threat:
1. That camera becomes the active camera
2. Alarm message includes camera name
3. Subsequent `/zone`, `/target`, `/togglealarm` commands apply to that camera
4. User can switch back with `/cam <num>`

## /cam Command Implementation

```python
def _handle_cam_cmd(text):
    """/cam <1-8> | /cam ? | /cam list | /cam status"""
    global CAM, ACTIVE_CAMERA
    arg = text[len("/cam"):].strip()
    
    if not arg or arg.lower() in ("?", "list", "список", "lista"):
        lines = []
        for k in range(1, 9):
            v = CAMERA_NAMES.get(k, f"Camera {k}")
            cam = CAM_MANAGER.cameras.get(k)
            status = "🟢" if cam and cam.alive else "🔴"
            marker = " ← ACTIVE" if k == ACTIVE_CAMERA else ""
            lines.append(f"{status} {v} ({k}){marker}")
        send_text("Доступные камеры (1-8):\n" + "\n".join(lines))
        return
    
    if arg.lower() in ("status", "статус", "estado"):
        # ... detailed status
        return
    
    try:
        num = int(arg)
        if 1 <= num <= 8:
            ACTIVE_CAMERA = num
            CAM = CAM_MANAGER.get_active()
            send_text(f"Камера переключена: {CAMERA_NAMES.get(num)}")
            save_settings()
            _refresh_control_msg()
            return
    except ValueError:
        pass
    send_text("Камера не найдена. Используйте номер 1-8. /cam ? для списка.")
```

## Settings Persistence

Added `camera` field to `sguard_settings.json`:
```json
{
  "zone": [3, 3, 5],
  "target": "red car",
  "lang": "en",
  "auto": true,
  "camera": 1
}
```

Loaded at startup:
```python
def load_settings():
    # ...
    cam = s.get("camera")
    if cam and cam in CAMERA_URLS:
        CAM_MANAGER.set_active(cam)
```

## Verified Working Cameras (2026-08-07)

| # | Camera | Source | Resolution | Type |
|---|--------|--------|------------|------|
| 1 | CA Mono - Mammoth Mountain | CA DOT | 260×320 | JPG |
| 2 | CA Mono - Conway Summit | CA DOT | 260×320 | JPG |
| 3 | CA Mono - Stateline | CA DOT | 260×320 | JPG |
| 4 | CA Mono - Crestview | CA DOT | 260×320 | JPG |
| 5 | CO DOT - I-70 Road Surface | CO DOT | 480×640 | JPG |
| 6 | OH DOT - Toledo SR-2 EB | OH DOT | 704×480 | JPG |
| 7 | OH DOT - Columbus CMH 2134 | OH DOT | 1920×1080 | JPG |
| 8 | CA DOT - Shasta I-5 Redding | CA DOT | 260×320 | JPG |

All 8 cameras verified working with OpenCV + YOLO11n detection.

## Key Files Modified

| File | Changes |
|------|---------|
| `panic_mode.py` | Complete 8-camera architecture, numbered switching, per-camera alarm |
| `sguard.env` | Updated with correct plug IP (192.168.137.197) |
| `sguard_settings.json` | Added camera field |

## Tests Passing

- Syntax: ✅
- i18n (RU/EN/ES): ✅ 48 keys × 3 langs
- target_parse: ✅ 11 cases
- graph: ✅
- Evolution cycle #12: ✅ (tests + debug + USB backup + Telegram report)
- Bot uptime: Stable 2+ hours