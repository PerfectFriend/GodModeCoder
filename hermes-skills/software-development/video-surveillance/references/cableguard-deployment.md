# CableGuard deployment & productization (2026-08-05)

Turning the surveillance prototype into a sellable product: camera discovery,
one-script install, GitHub packaging, hardware sizing. Repo: `PerfectFriend/cableguard`
(public, MIT). Local working copy: `C:\Users\tomas\video-surveillance\`.

## Camera discovery (`scripts/scan_cameras.py`)

Finds IP cameras in the LAN without knowing credentials:

- Auto-detects subnet via `ipconfig` IPv4 regex, or `--subnet 192.168.1.0/24`.
- Port scan (ThreadPoolExecutor, 64 workers): 554=RTSP, 80/8080=HTTP,
  8000/8899=Hikvision, 37777/34567=Dahua/XMeye.
- HTTP banner grab on 80/8080 → producer guess; prints ready RTSP URLs per vendor:
  - Hikvision: `rtsp://user:pass@IP:554/Streaming/Channels/101`
  - Dahua: `rtsp://user:pass@IP:554/cam/realmonitor?channel=1&subtype=0`
  - Uniview: `rtsp://user:pass@IP:554/unicast/c1/s0/live`
  - generic fallbacks: `/stream1`, `/live`, `/ch0`, `/h264`, `/videoMain`
- `tools/rtsp_preview.py <url> [--save out.jpg]` — verify picture before enabling surveillance.

## One-script install (the product's onboarding)

`install.sh` (Linux/macOS) and `install.ps1` (Windows) — curl-able, idempotent:

1. mkdir `~/cableguard` (or arg) → cd
2. python3/python check (winget/apt/brew fallback), ffmpeg check (warn-only — photos work, clips don't)
3. `python -m venv .venv` → pip install `opencv-python ultralytics pyyaml requests`
4. YOLO weights: `from ultralytics import YOLO; YOLO('yolo11n.pt')` (auto-download ~5.4MB)
5. `cp config.example.yaml config.yaml` if absent + warn "edit RTSP + chat_id"
6. Import check (`import cv2, ultralytics, yaml, requests`) → done banner with next steps

Pattern: **secrets never in repo** — `config.yaml` gitignored, `config.example.yaml` is the
committed template; installer copies template → user edits.

## GitHub packaging (what the product repo needs)

- README in the **customer's language** (Spanish for the cable-theft market — «Detección de
  ladrones de cable», «pértiga aislante», «casco», «chaleco reflectante»). English secondary.
- Docs: `docs/CAMERA-SETUP.md` (wiring diagram: camera → PoE injector → router; PC → WiFi same
  router; how to find the camera), `docs/esp32_alarm.ino` (firmware).
- LICENSE (MIT), `.gitignore` (config.yaml, alerts/, logs/, *.pt, .venv).
- Install instructions as one-liners: `curl -sSL https://raw.githubusercontent.com/<owner>/<repo>/main/install.sh | bash`.

## Hardware sizing for 8 cameras (≈255 € sweet spot)

| Load | Budget |
|---|---|
| 8× RTSP decode | use **hardware decode** (`h264_qsv` on Intel) — software decode pins CPU |
| YOLO11n 8 cams × 2 FPS | ~5-10% of a modern 4-core |
| RAM | 8 GB min, **16 GB recommended** (YOLO + OpenCV + 8 streams) |

- **Budget (~180 €)**: Beelink S12 Pro / Mini S12 (Intel N100, 16GB, 500GB NVMe) + TP-Link TL-SG1008P (8× PoE).
- **Optimum (~255 €, recommended for sale)**: Beelink EQ12 / GMKtec NucBox G5 + TP-Link TL-SG1210MP (8× PoE+, 120W) + TP-Link Archer C6 (router for internet/Telegram).
- **Headroom (~350 €)**: Beelink SER5 (Ryzen 7 5700U) — if client wants fine-tuning / more cams.
- PoE switch **replaces per-camera injectors** (8 injectors = cable mess); cameras on the switch's
  own network, router only for internet (RTSP over WiFi is bad — keep cameras wired).
- Passive-cooled N100 for dusty sites; SSD not HDD (clips write constantly).

## Demo without hardware

- `python demo_prototype.py --source synth --direct` — synthetic thief frame, full cycle
  (detect → Telegram → actuator sim). See `electrician-thief-prototype.md`.
- Real camera later: `python scripts/scan_cameras.py` → put URL in `config.yaml`
  (`enabled: true`) → `python demo_prototype.py --source rtsp://user:pass@IP:554/stream1`.

## Pitfalls

- RTSP placeholder IPs in the committed config timeout — always flip `enabled: true` per real camera.
- Creating the GitHub repo via CDP browser: form may reject first click with
  «You can't perform that action at this time» — re-open `/new`, fill name FIRST, wait for
  radio state, then click Create; it succeeds on retry (worked for PerfectFriend/cableguard).
- `gh` CLI / API token may be unavailable on a fresh box — the CDP-browser route (user's
  logged-in session) is a reliable fallback for repo creation + SSH-key add
  (see `cdp-browser-automation` skill).
