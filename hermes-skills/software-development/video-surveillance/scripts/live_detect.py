#!/usr/bin/env python3
"""Live detection on public cameras (MJPEG/HLS/RTSP) - capture -> YOLO -> per-class stats.
SuperGuard pipeline proof without client hardware. Works with any URL OpenCV can open:
rtsp://, http://...mjpg, https://.../playlist.m3u8 (HLS).
Usage: python live_detect.py [seconds_per_cam]   (edit CAMS below)
"""
import os, time, sys
import cv2
from ultralytics import YOLO

CAMS = {
    # TrafficVision.live verified HLS streams (2026-08-06)
    "indonesia_banjar": "https://atcs.banjarkota.go.id:5443/LiveApp/streams/Ptzparungsari.m3u8",
    "caltrans_CA_SR120": "https://wzmedia.dot.ca.gov/D10/SJ_EB120_EO_YosemiteAve.stream/playlist.m3u8",
    # Insecam verified MJPEG (2026-08-06)
    "parking": "http://97.86.89.114:2222/mjpg/video.mjpg",
    "harbor": "http://109.228.134.144:81/mjpg/video.mjpg",
}

SECONDS = float(sys.argv[1]) if len(sys.argv) > 1 else 15.0
SKIP = 3  # analyze every Nth frame
CONF = 0.30

def run_camera(name, url, seconds=SECONDS, skip=SKIP):
    print(f"\n=== {name} ===")
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        print("  FAIL: cannot open")
        return
    model = YOLO("yolo11n.pt")  # auto-downloads ~5.4MB on first run
    start = time.time()
    n_frames = n_analyzed = 0
    class_counts, max_conf = {}, {}
    while time.time() - start < seconds:
        ok, frame = cap.read()
        if not ok:
            print("  read fail, reconnect...")
            cap.release(); time.sleep(1)
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            continue
        n_frames += 1
        if n_frames % skip != 0:
            continue
        n_analyzed += 1
        h, w = frame.shape[:2]
        if w > 1280:  # downscale for speed
            sc = 1280 / w
            frame = cv2.resize(frame, (int(w*sc), int(h*sc)))
        r = model.predict(frame, conf=CONF, imgsz=640, verbose=False)[0]
        for box in r.boxes:
            nc = r.names[int(box.cls[0])]
            cf = float(box.conf[0])
            class_counts[nc] = class_counts.get(nc, 0) + 1
            max_conf[nc] = max(max_conf.get(nc, 0), cf)
    cap.release()
    print(f"  frames={n_frames} analyzed={n_analyzed}")
    if class_counts:
        print("  DETECTED: " + ", ".join(
            f"{k} x{v} (max {max_conf[k]:.2f})"
            for k, v in sorted(class_counts.items(), key=lambda x: -x[1])))
    else:
        print("  DETECTED: nothing")

if __name__ == "__main__":
    for name, url in CAMS.items():
        try:
            run_camera(name, url)
        except Exception as e:
            print(f"{name}: ERROR {e}")
