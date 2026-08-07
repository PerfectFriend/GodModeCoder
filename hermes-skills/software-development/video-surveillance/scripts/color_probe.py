#!/usr/bin/env python3
"""Color calibration probe for vehicle-triggered alarms (panic mode).
Runs YOLO + HSV color analysis on a live camera for N seconds, printing per-vehicle
color fractions so you can set YELLOW_MIN_FRACTION / BLACK_V_MAX thresholds between
real signal and noise. Usage: python color_probe.py <camera_url> [seconds]

Validated 2026-08-06 on Indonesia Banjar public cam: yellow bus 18-24%,
non-yellow cars/trucks 0-5%, motorcycles V=73-116 (dark), cars V=149-172 (light).
"""
import sys, time, threading, cv2, numpy as np
from ultralytics import YOLO

URL = sys.argv[1] if len(sys.argv) > 1 else \
    "https://atcs.banjarkota.go.id:5443/LiveApp/streams/Ptzparungsari.m3u8"
DURATION = int(sys.argv[2]) if len(sys.argv) > 2 else 45
VEHICLES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
Y_LOW = np.array([15, 60, 80])
Y_HIGH = np.array([40, 255, 255])
MODEL = YOLO("yolo11n.pt")

class Cam:
    """Continuous background capture - always latest frame."""
    def __init__(self, url):
        self.url = url
        self.lock = threading.Lock()
        self.frame = None
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
            except Exception:
                pass
            time.sleep(2)

    def latest(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

cam = Cam(URL)
time.sleep(5)

def color_stats(frame, box):
    """(yellow_fraction, mean_brightness_V, mean_saturation_S) of central body zone."""
    x1, y1, x2, y2 = [int(v) for v in box]
    cx = (x1 + x2) // 2
    w, h = x2 - x1, y2 - y1
    if w < 20 or h < 20:
        return 0.0, 0.0, 0.0
    zone = frame[max(y1, y1 + h // 4):y2, max(x1, cx - w // 5):min(x2, cx + w // 5)]
    if zone.size == 0:
        return 0.0, 0.0, 0.0
    hsv = cv2.cvtColor(zone, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, Y_LOW, Y_HIGH)
    return (float(mask.mean() / 255.0),
            float(hsv[..., 2].mean()),
            float(hsv[..., 1].mean()))

t0 = time.time()
print(f"probing {URL} for {DURATION}s (per-vehicle: name conf yellow% V S)", flush=True)
while time.time() - t0 < DURATION:
    frame = cam.latest()
    if frame is None:
        time.sleep(1)
        continue
    r = MODEL(frame, conf=0.35, imgsz=640, verbose=False)[0]
    for b in r.boxes:
        cls = int(b.cls[0])
        if cls in VEHICLES:
            yf, V, S = color_stats(frame, b.xyxy[0].tolist())
            print(f"  {VEHICLES[cls]:>10} c={float(b.conf[0]):.2f} "
                  f"yellow={yf*100:5.1f}% V={V:5.1f} S={S:5.1f}", flush=True)
    time.sleep(2)
print("DONE - set YELLOW_MIN_FRACTION between noise (0-5%) and signal (18%+);",
      "black threshold V<90 works daytime.", flush=True)
