#!/usr/bin/env python3
"""SuperGuard zone-dwell test: YOLO + ByteTrack + ROI zone + dwell timer.

Detects person(s) staying in a defined zone longer than N seconds.
Proven live 2026-08-06 on public traffic camera (Indonesia Banjar):
10 tracked IDs, 2 alerts fired (6.1s, 5.9s) in a 30s window.

Usage:  python zone_dwell_test.py [dwell_seconds] [seconds]
NOTE: first run after ultralytics auto-installs 'lap' does NOT track properly
      (ByteTrack needs it) - rerun the script once before trusting results.
"""
import os, sys, time
import numpy as np
import cv2
from ultralytics import YOLO

# Live public camera (Indonesia - street with people). Swap for any RTSP/MJPEG/HLS URL.
URL = "https://atcs.banjarkota.go.id:5443/LiveApp/streams/Ptzparungsari.m3u8"

# Zone: normalized polygon (x,y in 0..1) - street area
ZONE = [(0.15, 0.25), (0.85, 0.25), (0.85, 0.95), (0.15, 0.95)]
DWELL_SECONDS = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
RUN_SECONDS = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
CONF = 0.35

model = YOLO("yolo11n.pt")


def point_in_zone(px, py, zone, w, h):
    poly = np.array([[x * w, y * h] for x, y in zone], dtype=np.float32)
    return cv2.pointPolygonTest(poly, (px, py), False) >= 0


print(f"Camera: {URL}")
print(f"Zone (normalized): {ZONE}")
print(f"Dwell threshold: {DWELL_SECONDS}s, running {RUN_SECONDS}s...\n")

cap = cv2.VideoCapture(URL)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
if not cap.isOpened():
    print("FAIL: cannot open stream")
    sys.exit(1)

tracks = {}      # track_id -> {first_seen, in_zone, zone_enter, in_zone_time}
alerts = set()   # track_ids that already fired dwell alert
start = time.time()
n_frames = 0

while time.time() - start < RUN_SECONDS:
    ok, frame = cap.read()
    if not ok:
        cap.release()
        time.sleep(1)
        cap = cv2.VideoCapture(URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        continue
    n_frames += 1
    if n_frames % 3 != 0:
        continue
    frame_h, frame_w = frame.shape[:2]
    now = time.time()

    results = model.track(frame, conf=CONF, imgsz=640, persist=True,
                          verbose=False, tracker="bytetrack.yaml")
    r = results[0]

    if r.boxes is not None and r.boxes.id is not None:
        boxes = r.boxes.xyxy.cpu().numpy()
        ids = r.boxes.id.cpu().numpy().astype(int)
        clss = r.boxes.cls.cpu().numpy().astype(int)
        confs = r.boxes.conf.cpu().numpy()
        for box, tid, cls, conf in zip(boxes, ids, clss, confs):
            if r.names[cls] != "person":
                continue
            cx = (box[0] + box[2]) / 2
            cy = (box[1] + box[3]) / 2
            in_zone = point_in_zone(cx, cy, ZONE, frame_w, frame_h)

            if tid not in tracks:
                tracks[tid] = {"first_seen": now, "in_zone": False,
                               "zone_enter": None, "in_zone_time": 0.0}
            tr = tracks[tid]

            if in_zone and not tr["in_zone"]:
                tr["zone_enter"] = now
                tr["in_zone"] = True
            elif in_zone and tr["in_zone"]:
                tr["in_zone_time"] = now - tr["zone_enter"]
                if tr["in_zone_time"] >= DWELL_SECONDS and tid not in alerts:
                    alerts.add(tid)
                    print(f"  *** ALERT: person#{tid} in zone "
                          f"{tr['in_zone_time']:.1f}s (conf {conf:.2f}) ***")
            elif not in_zone and tr["in_zone"]:
                tr["in_zone"] = False
                tr["zone_enter"] = None

cap.release()

print(f"\n=== RESULT ({n_frames} frames, {time.time()-start:.0f}s) ===")
print(f"Tracks seen: {len(tracks)}")
in_zone_now = [tid for tid, tr in tracks.items() if tr["in_zone"]]
print(f"Persons in zone at end: {in_zone_now}")
print(f"Persons dwelling >= {DWELL_SECONDS}s: {len(alerts)} -> {sorted(alerts)}")
