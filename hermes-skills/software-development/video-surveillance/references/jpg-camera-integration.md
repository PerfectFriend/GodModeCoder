# JPG Camera Integration (Static Refresh via HTTP)

## Problem
Many DOT traffic cameras serve static JPEG images (not MJPEG/HLS/RTSP streams). OpenCV `VideoCapture` cannot reliably read these as a stream.

## Solution
Extended `Camera` class with dual-mode capture:

### Detection Logic
```python
def _detect_jpg(self, url):
    """Detect if URL is a static JPG/JPEG image."""
    url_lower = url.lower()
    return any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', 'snapshot', 'image'])
```

### JPG Loop (requests + cv2.imdecode)
```python
def _loop_jpg(self):
    import requests
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(self.url, headers=headers, timeout=10, stream=True)
            if resp.status_code == 200 and resp.content:
                img_array = np.frombuffer(resp.content, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if frame is not None and frame.size > 0:
                    with self.lock:
                        self.frame = frame
                        self.alive = True
                else:
                    with self.lock:
                        self.alive = False
            else:
                with self.lock:
                    self.alive = False
        except Exception as e:
            with self.lock:
                self.alive = False
        time.sleep(2)  # Refresh rate for JPG cameras
```

### Stream Loop (cv2.VideoCapture)
```python
def _loop_stream(self):
    """Loop for MJPEG/RTSP/HLS streams via cv2.VideoCapture."""
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
```

## Camera Initialization
```python
class Camera:
    def __init__(self, url, cam_id):
        self.url = url
        self.cam_id = cam_id
        self.name = CAMERA_NAMES.get(cam_id, f"Camera {cam_id}")
        self.is_jpg = self._detect_jpg(url)
        threading.Thread(target=self._loop, daemon=True).start()
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

## Sources Discovered (2026-08-07)

### California DOT (cwwp2.dot.ca.gov) - 967 cameras
- Mono County: 11 cams (Mammoth Mountain, Conway Summit, Stateline, Crestview, Toms Place)
- Inyo County: 2 cams (Coso Rest Area, Lone Pine)
- Kern County: 42 cams (US-395 corridor, SR-58 Cache Creek)
- Shasta County: I-5 Redding
- All: `https://cwwp2.dot.ca.gov/data/d9/cctv/image/<cam_id>/<cam_id>.jpg`

### Colorado DOT (cocam.carsprogram.org) - 669 cameras
- I-70 Road Surface: `https://cocam.carsprogram.org/Live_View/I70199RoadSurface.jpg`
- I-25: `https://cocam.carsprogram.org/Cellular/287N05430CAM1RHS-N.jpg`

### Ohio DOT (itscameras.dot.state.oh.us) - 1091 cameras
- Toledo: `https://itscameras.dot.state.oh.us:443/images/toledo/SR2-EB-Approach.jpg`
- Columbus: `https://itscameras.dot.state.oh.us:443/images/CMH/2134.jpg`
- Cincinnati: `https://itscameras.dot.state.oh.us:443/images/cincinnati/IR-75_at_Harrison.jpg`

### Other States
- Alabama: 1 cam (api.algotraffic.com)
- Colorado: 669 cams
- Kentucky: 222 cams (trimarc.org - some fail)
- Ohio: 1091 cams

## Key Implementation Details

1. **User-Agent header required** - Some DOT servers block requests without User-Agent
2. **Refresh rate**: 2 seconds for JPG cameras (configurable via `time.sleep(2)`)
3. **Thread safety**: Lock protects `self.frame` and `self.alive` between capture thread and `latest()` caller
3. **Error handling**: Network errors set `alive=False`, thread continues with 2s retry
4. **Frame format**: `cv2.imdecode` returns BGR numpy array compatible with YOLO
5. **Resolution**: JPG cameras vary (260×320 to 1920×1080) - YOLO handles resize internally via `imgsz=640`

## CameraManager Integration
```python
CAMERA_URLS = {
    1: "https://cwwp2.dot.ca.gov/data/d9/cctv/image/sr203mammothmountain/sr203mammothmountain.jpg",
    2: "https://cwwp2.dot.ca.gov/data/d9/cctv/image/us395conwaysummit/us395conwaysummit.jpg",
    # ... 1-8
}

CAMERA_NAMES = {
    1: "1: CA Mono - Mammoth Mountain",
    2: "2: CA Mono - Conway Summit",
    # ... 1-8
}

ACTIVE_CAMERA = 1  # Integer 1-8
```

## Pitfalls Avoided
1. **Don't use VideoCapture for JPG URLs** - OpenCV treats them as image sequences, fails on first read
2. **Unique filenames for Telegram** - Not needed for JPG (static), but `editMessageMedia` needs unique filenames for stream refresh
3. **Thread cleanup** - Daemon threads auto-exit on main process exit
4. **Lock contention** - `latest()` copies frame under lock (fast), capture thread holds lock briefly
5. **HTTPS cert verification** - `requests.get(verify=True)` by default, some DOT sites need `verify=False` (not needed for tested ones)