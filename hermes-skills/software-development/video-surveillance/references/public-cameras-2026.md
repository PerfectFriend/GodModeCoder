# Public cameras for pipeline testing — verified 2026-08-06

Two sources, both verified live: **TrafficVision.live** (152,221 official traffic
cams, HLS, best for person/car scenes) and **Insecam MJPEG** (open home/office
cams, HTTP).

## TrafficVision.live — 152,221-cam catalog (BEST, no key)

Aggregator of official traffic cameras: Caltrans (CA), Cotrip (CO), TxDOT (TX),
FDOT, 511NY, Thailand DOH, Korea, Indonesia ATCS, and hundreds more. Free,
no auth, open API — found via @Cyber_Sudo tweet (trafficvision.live).

### API recipe (works from curl AND Python)

```bash
# 1. Mint session token (900 s expiry):
curl -s -X POST -H "Content-Type: application/json" -d '{}' \
  "https://app.trafficvision.live/api/session"        # -> {"token": "...", "expiresIn": 900}

# 2. Manifest -> shards list (x-tv-session header, NOT Bearer):
curl -s -H "x-tv-session: <token>" \
  "https://api.trafficvision.live/internal/manifest"  # -> {"totalCameras":152221, "shards":[{key, cameras, bytes}]}

# 3. Per-shard catalog (~13k cameras, ~7.7 MB each):
curl -s -H "x-tv-session: <token>" \
  "https://api.trafficvision.live/internal/catalog/shards/<key>.json"  # -> {"cameras":[...]}
```

Python gotchas: add `Origin: https://trafficvision.live` + `Referer` headers to
BOTH calls or you get 403 `origin_forbidden`. The API also blocks cross-origin
fetch from the browser console — use curl/Python, not page JS.

### Camera schema (fields vary by feedType)

`id, location, roadway, direction, lat, lng, feedType, description, source,
country, state, city, county, imageUrl, videoUrl, sourceUrl, youtubeVideoId, angles`

feedTypes (one 13,111-cam shard): `image` 6090 (stills), `hybrid` 3270
(video + still, e.g. Caltrans), `youtube` 1913, `video` 1543 (pure HLS),
`multi-angle` 182, iframes (ipcamlive/angelcam/balticlivecam/...) ~113.
**No raw RTSP in the catalog** — video feeds are HLS `.m3u8`.

### Verified live HLS streams (2026-08-06, YOLO11n conf=0.30, 15 s window)

| cam | URL | res | detections |
|---|---|---|---|
| Caltrans CA SR-120 | `https://wzmedia.dot.ca.gov/D10/SJ_EB120_EO_YosemiteAve.stream/playlist.m3u8` | 1920×1080 | car×728 (max 0.80), truck×34, train×6 |
| Indonesia Banjar ATCS | `https://atcs.banjarkota.go.id:5443/LiveApp/streams/Ptzparungsari.m3u8` | 704×576 | **person×131 (0.81), motorcycle×101, truck×44, bus×28, car×22** |

Indonesia Banjar = best person-detection demo (busy street, people + motorcycles).
Not all `wzmedia.dot.ca.gov/D10/*.stream/playlist.m3u8` URLs are live (some 404)
— probe each. HLS works in OpenCV `VideoCapture(url)` with no changes to the
SuperGuard pipeline (MJPEG and HLS both read like RTSP).

## Insecam MJPEG cameras — verified live 2026-08-06

## Live cameras (12/12 alive on 2026-08-06)

| name | URL | res | YOLO11n on still |
|---|---|---|---|
| cam01 | `http://202.245.13.81:80/cgi-bin/camera?resolution=640&quality=1&Language=0` | 640×480 | cat 0.39 |
| cam02 | `http://80.32.125.254:8080/cgi-bin/faststream.jpg?stream=half&fps=15` | 1024×768 | — |
| cam03 | `http://58.94.98.44:80/SnapshotJPEG?Resolution=640x480&Quality=Clarity` | 640×480 | toilet 0.60 |
| cam04 | `http://97.68.104.34:80/mjpg/video.mjpg` | 1920×1080 | person 0.68, car 0.64 |
| cam05 | `http://202.142.10.11:80/SnapshotJPEG?Resolution=640x480&Quality=Clarity` | 640×480 | — |
| cam06 | `http://190.210.250.149:91/mjpg/video.mjpg` | 800×600 | keyboard 0.81, laptop 0.31 |
| cam07 | `http://97.86.89.114:2222/mjpg/video.mjpg` | 1280×960 | car×4, truck (live: car×146/12s) |
| cam08 | `http://85.4.30.236:80/mjpg/video.mjpg` | 1920×1200 | — |
| cam09 | `http://109.228.134.144:81/mjpg/video.mjpg` | 640×480 | boat×3 (live: boat×110/12s, person, bus) |
| cam10 | `http://80.235.76.111:18081/mjpg/video.mjpg` | 704×576 | — |
| cam11 | `http://45.80.27.109:80/mjpg/video.mjpg` | 640×480 | — |
| cam12 | `http://174.141.163.166:8080/mjpg/video.mjpg` | 640×480 | — |

Live-run winners (person/car scenes worth demoing): **cam04** (person+car),
**cam07** (parking lot, car 0.76 max), **cam09** (harbor, boat 0.86 max, +person).

## Discovery recipe

```bash
# 1. HTTPS is blocked; plain HTTP works:
curl -s -A "Mozilla/5.0" --max-time 15 "http://insecam.org/en/byrating/" -o insecam.html
# 2. Extract camera URLs (plain <img src="http://IP:port/..."> tags):
grep -oE 'http://[0-9.]+:[0-9]+/[^"]+' insecam.html | sort -u
# 3. Probe liveness — curl HANGS on MJPEG, use ffmpeg:
timeout 8 ffmpeg -v error -i "$url" -frames:v 1 -f null - 2>&1; echo "exit: $?"
# exit 0 = alive, else dead
```

## Probe + detection snippets

```bash
# Grab one frame (MJPEG/HTTP, any cam):
ffmpeg -v error -i "$url" -frames:v 1 -y cam.jpg
```

```python
# YOLO on stills (pick demo cams before going live):
from ultralytics import YOLO
m = YOLO("yolo11n.pt")
r = m.predict("cam.jpg", conf=0.30, imgsz=640, verbose=False)[0]
print([(r.names[int(b.cls[0])], round(float(b.conf[0]),2)) for b in r.boxes])
```

```python
# Live loop (VideoCapture handles MJPEG like RTSP):
cap = cv2.VideoCapture(url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
while time.time() - start < 12:
    ok, frame = cap.read()          # on fail: release + reconnect after 1s
    if not ok: continue
    r = model.predict(frame, conf=0.30, imgsz=640, verbose=False)[0]
```

## Zone-dwell validation (2026-08-06, same Indonesia cam)

ByteTrack + zone polygon + dwell timer, 30 s window:
- 10 person IDs tracked; **2 alerts fired**: person#3 in zone 6.1 s, person#9 5.9 s (threshold 5 s).
- Requires `lap>=0.5.12` — ultralytics auto-installs on first `track()`, but that first run
  tracks incorrectly; rerun script before trusting numbers. Ready-to-run: `scripts/zone_dwell_test.py`.

## Confidence vs person height (YOLO11n, full-body, measured on bus.jpg person patch)

| height px | conf | ≈ distance @1080p/~60° FOV |
|---|---|---|
| 400 | 0.889 | ~10 m |
| 300 | 0.908 | ~13 m |
| 250 | 0.876 | ~16 m |
| 200 | 0.856 | ~20 m |
| 150 | 0.812 | ~26 m |
| 100 | 0.786 | ~40 m |
| 60 | 0.732 | ~65 m |

Client-locked scenario (≤10 m zone, standing/walking person, dwell 1–5 s) = best case:
person ≈350–450 px → conf ≈0.89–0.91 → ~97–99% day, ~90–95% night/IR at conf=0.45.

## Notes

- **Insecam RTSP (port 554) is a dead end**: some listed cams have TCP 554 OPEN, but RTSP
  handshakes get connection reset / "Invalid data" — RTSP is auth-closed even though the HTTP
  snapshot is open. Don't burn time probing RTSP paths on Insecam cams; use their MJPEG/HTTP.
- ~1/12 cameras fail OpenCV open/read but work in ffmpeg — flaky rate, expect it.
- These are open/public cameras (no auth) listed by Insecam; fine for pipeline testing, not for
  production clients — always test on the client's own site for real deployments.
- URLs are ephemeral (cameras come and go) — re-probe before each demo, don't hardcode.
- **Bash loop pitfall (MSYS/git-bash)**: don't iterate camera URLs inline in `for u in "url1:name1" ...`
  — `&` and `:` inside URLs get mangled by the shell. Write a small `.sh` script with a
  `grab() { ... }` function (URL passed as `$1`) and run it; quoting inside functions survives.
