#!/usr/bin/env python3
"""SuperGuard LIVE STREAM SERVER (verified 2026-08-06).
Reads a camera (HLS/RTSP/MJPEG via OpenCV) and serves:
  /            - HTML page with live <img> MJPEG viewer
  /stream.mjpg - multipart MJPEG stream (works in any browser, ~15-20 fps)
  /status      - JSON status
Run: python stream_server.py --cam indonesia --port 8090
Give the phone the PC's LAN IP: http://192.168.1.x:8090/ (same network required).
"""
import argparse, json, socket, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import cv2

CAMS = {
    "indonesia": "https://atcs.banjarkota.go.id:5443/LiveApp/streams/Ptzparungsari.m3u8",
    "caltrans": "https://wzmedia.dot.ca.gov/D10/SJ_EB120_EO_YosemiteAve.stream/playlist.m3u8",
}

BOUNDARY = "superguard-frame"


class Camera:
    """Background capture thread: keeps latest JPEG frame."""

    def __init__(self, url):
        self.url = url
        self.lock = threading.Lock()
        self.frame = None
        self.w = self.h = 0
        self.ok = False
        self.started = time.time()
        self.frames_served = 0
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def _loop(self):
        while True:
            try:
                cap = cv2.VideoCapture(self.url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                while True:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                    if ok:
                        with self.lock:
                            self.frame = buf.tobytes()
                            self.h, self.w = frame.shape[:2]
                            self.ok = True
                    time.sleep(0.05)  # ~15-20 fps served
                cap.release()
            except Exception:
                pass
            with self.lock:
                self.ok = False
            time.sleep(3)  # reconnect

    def get_frame(self):
        with self.lock:
            return self.frame, self.w, self.h, self.ok

    def status(self):
        f, w, h, ok = self.get_frame()
        return {
            "url": self.url,
            "alive": ok,
            "size": f"{w}x{h}" if ok else "-",
            "uptime_s": int(time.time() - self.started),
            "frames": self.frames_served,
        }


CAM = None  # set at start


class Handler(BaseHTTPRequestHandler):
    server_version = "SuperGuard/1.0"

    def log_message(self, fmt, *args):
        pass  # quiet

    def _html(self):
        return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SuperGuard Live</title>
<style>
body{{background:#0b0e14;color:#e8e8e8;font-family:system-ui;margin:0;display:flex;flex-direction:column;align-items:center}}
h1{{font-size:18px;margin:12px}}
img{{width:min(96vw,720px);border-radius:10px;box-shadow:0 0 25px rgba(0,150,255,.25)}}
.live{{color:#4ade80;font-size:13px}}
</style></head><body>
<h1>📹 SuperGuard — live</h1>
<div class="live">● LIVE {CAM.status()['size']}</div>
<img src="/stream.mjpg" alt="stream">
<p style="font-size:12px;color:#888">Источник: {CAM.url}</p>
</body></html>"""

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            body = self._html().encode()
            self._send(200, "text/html; charset=utf-8", body)
        elif path == "/stream.mjpg":
            self._stream()
        elif path == "/status":
            body = json.dumps(CAM.status()).encode()
            self._send(200, "application/json", body)
        else:
            self._send(404, "text/plain", b"not found")

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _stream(self):
        self.send_response(200)
        self.send_header("Content-Type", f"multipart/x-mixed-replace; boundary={BOUNDARY}")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            while True:
                frame, w, h, ok = CAM.get_frame()
                if ok and frame:
                    self.wfile.write(b"--" + BOUNDARY.encode() + b"\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(frame)}\r\n\r\n".encode())
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
                    CAM.frames_served += 1
                time.sleep(0.06)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", default="indonesia", choices=list(CAMS))
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()

    global CAM
    url = args.cam if args.cam.startswith("http") else CAMS[args.cam]
    CAM = Camera(url)

    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    ips = socket.gethostbyname_ex(socket.gethostname())[2]
    print(f"SuperGuard stream: {url}", flush=True)
    print(f"  local:   http://127.0.0.1:{args.port}/", flush=True)
    for ip in ips:
        print(f"  LAN:     http://{ip}:{args.port}/   (phone must be on same network)", flush=True)
    print("  stream:  /stream.mjpg   status: /status", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
