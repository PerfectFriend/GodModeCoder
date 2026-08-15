# SuperGuard Camera Discovery — 2500+ Live DOT Traffic Cameras

**Source**: GitHub OpenTrafficCamMap (AidanWelch/OpenTrafficCamMap) + Public DOT APIs
**Date**: 2026-08-07
**Verified**: OpenCV 5.0.0 on Windows 11 (Radeon 780M)

---

## Working Camera Sources (2500+ total)

| Source | Cameras | Format | Status | Notes |
|--------|---------|--------|--------|-------|
| **California DOT (cwwp2.dot.ca.gov)** | 967 | JPG (static refresh) | ✅ **All work** | Mono 11, Inyo 2, Kern 42, Shasta... |
| **Colorado DOT (cocam.carsprogram.org)** | 669 | JPG | ✅ **All work** | I-70, US-287, I-25... |
| **Ohio DOT (itscameras.dot.state.oh.us)** | 1091 | JPG | ✅ **Mostly work** | Toledo, Cleveland, Cincinnati, Columbus... |
| **Alabama DOT** | 1 | JPG | ✅ Works | api.algotraffic.com |
| **Kentucky (trimarc.org)** | 222 | JPG | ⚠️ Mixed | Louisville area (some fail - block hotlink) |
| **Alaska (511.alaska.gov)** | ~20 | HTML page | ⚠️ Needs parsing | Anchorage, Fairbanks... |

---

## Top 10 Ready-to-Use URLs for SuperGuard

```python
CAMERA_URLS = {
    "main": "https://atcs.banjarkota.go.id:5443/LiveApp/streams/Ptzparungsari.m3u8",  # Current
    "ca_mono_1": "https://cwwp2.dot.ca.gov/data/d9/cctv/image/sr203mammothmountain/sr203mammothmountain.jpg",
    "ca_mono_2": "https://cwwp2.dot.ca.gov/data/d9/cctv/image/us395conwaysummit/us395conwaysummit.jpg",
    "ca_kern_1": "https://cwwp2.dot.ca.gov/data/d9/cctv/image/us395northofsr141/us395northofsr141.jpg",
    "co_i70": "https://cocam.carsprogram.org/Live_View/I70199RoadSurface.jpg?ts=1",
    "co_i25": "https://cocam.carsprogram.org/Cellular/287N05430CAM1RHS-N.jpg?ts=1",
    "oh_toledo": "https://itscameras.dot.state.oh.us:443/images/toledo/SR2-EB-Approach.jpg",
    "oh_cmh": "https://itscameras.dot.state.oh.us:443/images/CMH/2134.jpg",
    "oh_cincy": "https://itscameras.dot.state.oh.us:443/images/cincinnati/IR-75_at_Harrison.jpg",
    "ca_shasta": "https://cwwp2.dot.ca.gov/data/d2/cctv/image/i5redding/i5redding.jpg",
}
```

---

## Technical Notes for JPG Cameras (Static Refresh)

- OpenCV reads JPG as single frame: `cv2.VideoCapture(url)` → `cap.read()`
- Need to poll URL every 1-5 seconds for "live" effect
- Refresh rate depends on DOT (California: ~2-5s, Colorado: ~5-10s, Ohio: ~2-5s)
- Some block hotlink — need `Referer` header or session cookies
- Kentucky (trimarc.org) blocks some external requests

---

## Non-Working Formats

| Format | Reason |
|--------|--------|
| HLS/m3u8 (Wowza) | OpenCV 5.0 doesn't open reliably |
| RTSP | Requires auth, no public streams found |
| Some JPG | Hotlink protection / referer checks |

---

## Discovery Source

- **OpenTrafficCamMap**: 7029 total cameras (2950 JPG, 2919 HLS, 1160 other)
- **Repository**: https://github.com/AidanWelch/OpenTrafficCamMap
- **Data**: https://raw.githubusercontent.com/AidanWelch/OpenTrafficCamMap/master/cameras/USA.json
- **States with JPG**: Alabama (1), California (967), Colorado (669), Kentucky (222), Ohio (1091)

---

## Integration Pattern for CameraManager

```python
# For JPG cameras: use requests + cv2.imdecode instead of VideoCapture
def _jpg_loop(self):
    while True:
        try:
            resp = requests.get(self.url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                arr = np.frombuffer(resp.content, dtype=np.uint8)
                frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if frame is not None:
                    with self.lock:
                        self.frame = frame
                        self.alive = True
        except Exception:
            pass
        time.sleep(UPDATE_EVERY)
```