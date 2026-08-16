Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, video-surveillance, yolo11, n100, sg1210mp, openvino, edge-
C:\Vault\YOLO11n Edge Deployment on N100 SG1210MP.md


deployment, intel, ultralytics]
source: textbook
status: learned
date: 2026-08-10
priority: 8
---

# YOLO11n Edge Deployment on N100/SG1210MP

## Summary
**YOLO11n** (nano, 2.6M params) deployed on **Intel N100** (LattePanda MU) / **SG1210MP** with **OpenVINO INT8** achieves **21 FPS detection**, **15 FPS segmentation/pose** on iGPU — **5-7x faster than YOLOv8 on CPU**, **2-3x faster than YOLO11n on CPU**. Optimal for edge video surveillance on fanless x86 SBCs.

## Hardware Targets

| Platform | CPU | iGPU | RAM | Storage | OpenVINO Support |
|----------|-----|------|-----|---------|------------------|
| **LattePanda MU** | Intel N100 (4C/4T, 3.4 GHz) | Intel UHD (24 EU) | 8GB DDR5 | 64GB eMMC | ✅ Full (CPU/GPU/NPU) |
| **SG1210MP** | Intel N100 | Intel UHD | 8GB DDR5 | 128GB SSD | ✅ Full |
| **Generic N100 SBC** | Intel N100 | Intel UHD | 8-16GB | NVMe | ✅ Full |

## YOLO11n Specs

| Metric | YOLO11n | YOLOv8n | Improvement |
|--------|---------|---------|-------------|
| **Params** | 2.6M | 3.2M | **22% fewer** |
| **mAP50-95 (COCO)** | 39.5 | 37.3 | **+2.2** |
| **CPU ONNX (ms)** | 56.1 | 78.2 | **28% faster** |
| **T4 TensorRT (ms)** | 1.5 | 2.1 | **29% faster** |

## OpenVINO Deployment Pipeline

### 1. Environment Setup (Windows/Linux)
```bash
# Windows
conda create -n yolo11 python=3.10
conda activate yolo11
pip install ultralytics openvino-dev torch torchvision

# Linux (Ubuntu 22.04/24.04)
sudo apt update && sudo apt install python3.10-venv
python3.10 -m venv yolo11
source yolo11/bin/activate
pip install ultralytics openvino-dev torch torchvision
```

### 2. Export to OpenVINO (INT8 Quantization)
```python
from ultralytics import YOLO

# Load PyTorch model
model = YOLO("yolo11n.pt")

# Export to OpenVINO INT8 (requires calibration data)
model.export(
    format="openvino",
    imgsz=640,
    quantize=8,           # INT8 Post-Training Quantization
    data="coco8.yaml",    # Calibration dataset
    fraction=0.1,         # Use 10% for calibration
    nms=True,             # Add NMS to graph
    batch=1,
    device="cpu"          # Export on CPU
)
# Output: yolo11n_openvino_model/
```

### 3. Inference with OpenVINO
```python
from ultralytics import YOLO

# Load OpenVINO model
ov_model = YOLO("yolo11n_openvino_model/")

# Run on Intel iGPU
results = ov_model(
    "https://ultralytics.com/images/bus.jpg",
    device="intel:gpu"    # Use Intel iGPU
)

# Or specify device explicitly
results = ov_model.predict(
    source="rtsp://camera/stream",
    device="intel:gpu",
    stream=True,
    verbose=False
)
```

### 4. Benchmark Different Devices
```python
from ultralytics import YOLO

model = YOLO("yolo11n_openvino_model/")

# Benchmark on CPU, GPU, NPU
results = model.benchmark(
    data="coco8.yaml",
    device="intel:cpu"    # or "intel:gpu", "intel:npu"
)
```

## Performance Results (LattePanda MU / N100)

### OpenVINO iGPU (INT8)
| Task | Model | FPS | vs YOLOv8 CPU | vs YOLO11n CPU |
|------|-------|-----|---------------|----------------|
| **Detection** | YOLO11n | **21** | 5x | 2x |
| **Segmentation** | YOLO11n | **15** | 7x | 3x |
| **Pose/Keypoint** | YOLO11n | **15** | 5x | 2x |

### OpenVINO CPU (INT8)
| Task | Model | FPS |
|------|-------|-----|
| Detection | YOLO11n | 10 |
| Segmentation | YOLO11n | 6.9 |
| Pose | YOLO11n | 8.6 |

### Ultralytics CPU (INT8)
| Task | Model | FPS |
|------|-------|-----|
| Detection | YOLO11n | 8.6 |
| Segmentation | YOLO11n | 5.5 |
| Pose | YOLO11n | 7.11 |

## RTSP Stream Processing (Video Surveillance)

### Multi-Camera Pipeline
```python
import cv2
from ultralytics import YOLO
import threading
import queue

class CameraProcessor:
    def __init__(self, rtsp_url, model_path, device="intel:gpu"):
        self.rtsp_url = rtsp_url
        self.model = YOLO(model_path)
        self.device = device
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = False
    
    def start(self):
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.process_thread = threading.Thread(target=self._process_loop)
        self.capture_thread.start()
        self.process_thread.start()
    
    def _capture_loop(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        while self.running:
            ret, frame = cap.read()
            if ret:
                if self.frame_queue.full():
                    self.frame_queue.get()  # Drop old frame
                self.frame_queue.put(frame)
    
    def _process_loop(self):
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                results = self.model.predict(
                    frame, device=self.device, verbose=False, imgsz=640
                )
                # Process detections: count, alert, log, etc.
                self._handle_detections(results)
    
    def _handle_detections(self, results):
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf > 0.5:
                    print(f"Camera {self.rtsp_url}: {r.names[cls]} {conf:.2f}")

# Usage
cameras = [
    CameraProcessor("rtsp://cam1:554/stream", "yolo11n_openvino_model/"),
    CameraProcessor("rtsp://cam2:554/stream", "yolo11n_openvino_model/"),
]
for cam in cameras:
    cam.start()
```

## Optimization for N100/SG1210MP

### BIOS Settings
```
Advanced → Graphics Configuration:
  - iGPU Memory: 4GB (or max available)
  - DVMT Pre-Allocated: 256M
  - DVMT Total Gfx Mem: MAX
  - Aperture Size: 256MB
  - Above 4GB Decoding: Enabled
```

### Windows Graphics Settings
```cmd
# Settings → System → Display → Graphics
# python.exe → High Performance → Intel UHD Graphics
# ffmpeg.exe → High Performance
```

### OpenVINO Environment
```bash
# Windows
set OPENVINO_INTEL_GPU=1
set OPENVINO_DEVICE=GPU

# Linux
export OPENVINO_INTEL_GPU=1
export OPENVINO_DEVICE=GPU
```

### Python Optimizations
```python
import os
os.environ["OPENVINO_INTEL_GPU"] = "1"

from ultralytics import YOLO

model = YOLO("yolo11n_openvino_model/")

# Warm-up
for _ in range(3):
    model.predict(np.zeros((640, 640, 3), dtype=np.uint8), device="intel:gpu", verbose=False)

# Inference loop
for frame in frames:
    results = model.predict(frame, device="intel:gpu", verbose=False, imgsz=640)
```

## Power & Thermal (Fanless SBC)

| Metric | Value |
|--------|-------|
| **Idle Power** | ~3W |
| **YOLO11n iGPU Load** | ~8-10W |
| **Temperature (Load)** | 55-65°C (passive heatsink) |
| **Throttling Threshold** | 90°C |

## Deployment Checklist

- [ ] BIOS: iGPU memory maxed, DVMT MAX
- [ ] OS: Windows 10/11 LTSC or Ubuntu 22.04/24.04 LTS
- [ ] Drivers: Latest Intel Graphics (Windows) / Mesa 24+ (Linux)
- [ ] OpenVINO: 2024.3+ (NPU support)
- [ ] Python: 3.10/3.11, ultralytics 8.2+, openvino-dev 2024.3+
- [ ] Model: yolo11n.pt → OpenVINO INT8 (quantize=8, data=coco8.yaml)
- [ ] Inference: device="intel:gpu", imgsz=640, batch=1
- [ ] RTSP: cv2.VideoCapture with buffer=1, threading
- [ ] Monitoring: GPU temp, FPS, detection latency

## Integration with Paranoidx/Sovereign

```python
# paranoidx_camera_node.py
class ParanoidxCamera:
    def __init__(self, camera_id, rtsp_url):
        self.camera_id = camera_id
        self.processor = CameraProcessor(rtsp_url, "yolo11n_openvino_model/")
        self.alert_webhook = "https://paranoidx.local/api/alert"
    
    def _handle_detections(self, results):
        for r in results:
            for box in r.boxes:
                cls_name = r.names[int(box.cls[0])]
                if cls_name in ["person", "car", "truck"] and box.conf[0] > 0.7:
                    self._send_alert(cls_name, float(box.conf[0]), r.orig_img)
    
    def _send_alert(self, cls, conf, frame):
        # Save snapshot, send to Paranoidx central
        cv2.imwrite(f"/alerts/{self.camera_id}_{cls}_{time.time()}.jpg", frame)
        requests.post(self.alert_webhook, json={
            "camera": self.camera_id,
            "class": cls,
            "confidence": conf,
            "timestamp": time.time()
        })
```

## References
- **LattePanda MU YOLO11**: https://www.lattepanda.com/blog-323240.html
- **Ultralytics OpenVINO**: https://docs.ultralytics.com/integrations/openvino
- **YOLO11 Docs**: https://docs.ultralytics.com/models/yolo11
- **OpenVINO Notebooks**: https://github.com/openvinotoolkit/openvino_notebooks/tree/latest/notebooks/yolov11-optimization
- **Intel N100 Specs**: https://www.intel.com/content/www/us/en/products/sku/230554/intel-processor-n100-6m-cache-up-to-3-40-ghz.html