#!/usr/bin/env python3
"""Probe: continuous background capture keeps the LATEST frame fresh.

Validated 2026-08-06 — the fix for the "frozen feed" bug where a single persistent
cv2.VideoCapture read every 2 s served STALE buffered frames (OpenCV HLS demuxer
buffers in order), while the camera was clearly live.

Usage:
    python bg_capture.py [hls_or_rtsp_url]
    (default: Indonesia Banjar ATCS public HLS)

Prints md5 of each grabbed frame every 2 s. All-different md5s = capture is fresh.
Identical md5s = something upstream is frozen (then blame the feed, not the loop).
"""
import hashlib
import sys
import threading
import time

import cv2

DEFAULT_URL = "https://atcs.banjarkota.go.id:5443/LiveApp/streams/Ptzparungsari.m3u8"


class Camera:
    """Reads the stream continuously, always keeps the LATEST frame."""

    def __init__(self, url):
        self.url = url
        self.lock = threading.Lock()
        self.frame = None
        self.w = self.h = 0
        self.alive = False
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            try:
                cap = cv2.VideoCapture(self.url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                while True:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    if ok:
                        with self.lock:
                            self.frame = buf.tobytes()
                            self.h, self.w = frame.shape[:2]
                            self.alive = True
            except Exception:
                pass
            with self.lock:
                self.alive = False
            time.sleep(2)  # reconnect

    def latest(self):
        with self.lock:
            return self.frame, self.w, self.h, self.alive


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"capturing {url}", flush=True)
    cam = Camera(url)
    time.sleep(5)  # let it buffer
    prev = None
    for i in range(6):
        frame, w, h, alive = cam.latest()
        if frame is None:
            print(f"{i}: no frame yet (alive={alive})", flush=True)
            time.sleep(2)
            continue
        md5 = hashlib.md5(frame).hexdigest()[:12]
        tag = "SAME (frozen!)" if md5 == prev else "fresh"
        print(f"{i}: {w}x{h} {len(frame)}B md5={md5} {tag}", flush=True)
        prev = md5
        time.sleep(2)
    print("DONE", flush=True)
