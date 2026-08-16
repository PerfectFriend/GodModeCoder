Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, video-surveillance, rtsp, hsv, yolo, opencv, opencv, color-
C:\Vault\RTSP + HSV + YOLO Classes Detection.md


detection, surveillance]
source: textbook
status: learned
date: 2026-08-10
priority: 8
---

# RTSP + HSV + YOLO Classes Detection

## Summary
Combining **RTSP stream ingestion**, **HSV color filtering**, and **YOLO class detection** creates a robust video surveillance pipeline: RTSP for stream acquisition, HSV for fast color-based pre-filtering (reducing YOLO inference), and YOLO for accurate object classification. This hybrid approach reduces compute by 60-80% on edge devices.

## Architecture Overview

```
RTSP Stream → Frame Grabber → HSV Filter → ROI Extract → YOLO Inference → Alert/Log
                    │              │            │              │
                    ▼              ▼            ▼              ▼
              Thread 1         Thread 2    Thread 3       Thread 4
              (capture)       (color filter) (crop)        (inference)
```

## RTSP Stream Handling

### Robust RTSP Capture
```python
import cv2
import threading
import queue
import time

class RTSPCapture:
    def __init__(self, rtsp_url, buffer_size=1):
        self.rtsp_url = rtsp_url
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = False
        self.cap = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        # Wait for first frame
        while self.frame_queue.empty():
            time.sleep(0.01)
    
    def _capture_loop(self):
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                # Reconnect on failure
                time.sleep(1)
                self.cap.release()
                self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
                continue
            
            # Non-blocking queue put (drop old frames)
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self.frame_queue.put(frame)
    
    def get_frame(self, timeout=1.0):
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
```

### RTSP URL Formats
```python
# Common formats
RTSP_URLS = {
    "hikvision": "rtsp://user:pass@192.168.1.64:554/Streaming/Channels/101",
    "dahua": "rtsp://user:pass@192.168.1.65:554/cam/realmonitor?channel=1&subtype=0",
    "reolink": "rtsp://user:pass@192.168.1.66:554/h264Preview_01_main",
    "generic": "rtsp://user:pass@ip:554/stream",
    "onvif": "rtsp://user:pass@ip:554/onvif1",
}
```

## HSV Color Filtering (Pre-Processing)

### HSV Color Space Basics
```python
import cv2
import numpy as np

def create_hsv_mask(frame, hsv_ranges):
    """
    hsv_ranges: list of (lower_hsv, upper_hsv) tuples
    Example: [((0, 50, 50), (10, 255, 255)),  # Red
              ((170, 50, 50), (180, 255, 255))] # Red wrap-around
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    
    for lower, upper in hsv_ranges:
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        mask |= cv2.inRange(hsv, lower, upper)
    
    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask

# Common HSV ranges (H: 0-180, S: 0-255, V: 0-255)
HSV_RANGES = {
    "red": [
        ((0, 70, 50), (10, 255, 255)),
        ((170, 70, 50), (180, 255, 255))
    ],
    "orange": [((10, 100, 100), (25, 255, 255))],
    "yellow": [((25, 100, 100), (35, 255, 255))],
    "green": [((35, 50, 50), (85, 255, 255))],
    "blue": [((90, 50, 50), (130, 255, 255))],
    "purple": [((130, 50, 50), (160, 255, 255))],
    "white": [((0, 0, 200), (180, 30, 255))],
    "black": [((0, 0, 0), (180, 255, 50))],
    "skin": [((0, 20, 70), (20, 255, 255))],
}
```

### Adaptive HSV (Auto-Calibration)
```python
class AdaptiveHSV:
    def __init__(self, initial_ranges):
        self.ranges = initial_ranges
        self.samples = []
        self.max_samples = 100
    
    def add_sample(self, hsv_roi):
        """Add HSV sample from user-selected ROI"""
        hsv_vals = hsv_roi.reshape(-1, 3)
        self.samples.append(hsv_vals)
        if len(self.samples) > self.max_samples:
            self.samples.pop(0)
        self._update_ranges()
    
    def _update_ranges(self):
        if len(self.samples) < 10:
            return
        all_samples = np.vstack(self.samples)
        h_min, s_min, v_min = np.percentile(all_samples, 5, axis=0)
        h_max, s_max, v_max = np.percentile(all_samples, 95, axis=0)
        
        # Handle hue wrap-around
        if h_max - h_min > 90:
            self.ranges = [
                ((int(h_min), int(s_min), int(v_min)), (180, 255, 255)),
                ((0, int(s_min), int(v_min)), (int(h_max), 255, 255))
            ]
        else:
            self.ranges = [((int(h_min), int(s_min), int(v_min)), 
                          (int(h_max), int(s_max), int(v_max)))]
```

## ROI Extraction from HSV Mask

### Contour-Based ROI Extraction
```python
def extract_rois(frame, mask, min_area=500, max_area=50000, padding=10):
    """
    Extract bounding boxes from HSV mask for YOLO inference
    Returns: list of (x, y, w, h) ROIs
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rois = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            x, y, w, h = cv2.boundingRect(cnt)
            # Add padding
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(frame.shape[1] - x, w + 2*padding)
            h = min(frame.shape[0] - y, h + 2*padding)
            rois.append((x, y, w, h))
    
    # Merge overlapping ROIs
    rois = merge_overlapping_rois(rois, iou_threshold=0.3)
    return rois

def merge_overlapping_rois(rois, iou_threshold=0.3):
    if len(rois) <= 1:
        return rois
    
    merged = []
    used = [False] * len(rois)
    
    for i, (x1, y1, w1, h1) in enumerate(rois):
        if used[i]:
            continue
        merged_roi = [x1, y1, w1, h1]
        used[i] = True
        
        for j, (x2, y2, w2, h2) in enumerate(rois):
            if used[j]:
                continue
            iou = calculate_iou((x1, y1, w1, h1), (x2, y2, w2, h2))
            if iou > iou_threshold:
                # Merge
                x_new = min(x1, x2)
                y_new = min(y1, y2)
                w_new = max(x1+w1, x2+w2) - x_new
                h_new = max(y1+h1, y2+h2) - y_new
                merged_roi = [x_new, y_new, w_new, h_new]
                used[j] = True
        
        merged.append(tuple(merged_roi))
    
    return merged

def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1+w1, x2+w2)
    yi2 = min(y1+h1, y2+h2)
    
    if xi2 <= xi1 or yi2 <= yi1:
        return 0.0
    
    inter = (xi2-xi1) * (yi2-yi1)
    area1 = w1 * h1
    area2 = w2 * h2
    union = area1 + area2 - inter
    
    return inter / union
```

## YOLO Class Detection on ROIs

### Selective YOLO Inference
```python
from ultralytics import YOLO

class SelectiveYOLO:
    def __init__(self, model_path, target_classes=None, conf_threshold=0.5):
        self.model = YOLO(model_path)
        self.target_classes = target_classes or ["person", "car", "truck", "bicycle", "motorcycle"]
        self.conf_threshold = conf_threshold
        self.class_names = self.model.names
    
    def detect_in_rois(self, frame, rois):
        """Run YOLO only on specified ROIs"""
        detections = []
        
        for x, y, w, h in rois:
            # Extract ROI
            roi = frame[y:y+h, x:x+w]
            if roi.size == 0:
                continue
            
            # Run YOLO on ROI
            results = self.model.predict(roi, verbose=False, conf=0.25)[0]
            
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                cls_name = self.model.names[cls_id]
                
                if cls_name in self.target_classes and conf >= self.conf_threshold:
                    # Convert ROI-relative coords to frame coords
                    bx, by, bw, bh = box.xywh[0].cpu().numpy()
                    detections.append({
                        "class": cls_name,
                        "confidence": conf,
                        "bbox": (
                            int(x + bx - bw/2),
                            int(y + by - bh/2),
                            int(bw),
                            int(bh)
                        ),
                        "roi": (x, y, w, h)
                    })
        
        return detections
```

### Full Pipeline Integration
```python
class SurveillancePipeline:
    def __init__(self, rtsp_url, model_path, hsv_color="red", target_classes=None):
        self.capture = RTSPCapture(rtsp_url)
        self.yolo = SelectiveYOLO("yolo11n_openvino_model/", target_classes)
        self.hsv_color = hsv_color
        self.running = False
    
    def start(self):
        self.capture.start()
        self.running = True
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
    
    def _process_loop(self):
        while self.running:
            frame = self.capture.get_frame(timeout=1.0)
            if frame is None:
                continue
            
            # 1. HSV Filter
            hsv_ranges = HSV_RANGES.get(self.hsv_color, [])
            if hsv_ranges:
                mask = create_hsv_mask(frame, hsv_ranges)
                rois = extract_rois(frame, mask)
            else:
                # No color filter - full frame
                rois = [(0, 0, frame.shape[1], frame.shape[0])]
            
            # 2. YOLO on ROIs
            detections = self.yolo.detect_in_rois(frame, rois)
            
            # 3. Handle detections
            for det in detections:
                self._handle_detection(det, frame)
            
            # 4. Visualization (optional)
            self._visualize(frame, detections)
    
    def _handle_detection(self, det, frame):
        print(f"ALERT: {det['class']} ({det['confidence']:.2f}) at {det['bbox']}")
        # Save snapshot, send alert, log to DB, etc.
        cv2.imwrite(f"alerts/{det['class']}_{time.time()}.jpg", frame)
    
    def _visualize(self, frame, detections):
        vis = frame.copy()
        for det in detections:
            x, y, w, h = det['bbox']
            cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(vis, f"{det['class']} {det['confidence']:.2f}", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Surveillance", vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
    
    def stop(self):
        self.running = False
        self.capture.stop()
        cv2.destroyAllWindows()
```

## Performance Optimization

### Threaded Pipeline (Producer-Consumer)
```python
class ThreadedPipeline:
    def __init__(self, rtsp_url, model_path):
        self.capture = RTSPCapture(rtsp_url)
        self.hsv_queue = queue.Queue(maxsize=4)
        self.yolo_queue = queue.Queue(maxsize=4)
        self.result_queue = queue.Queue(maxsize=4)
    
    def start(self):
        self.capture.start()
        threads = [
            threading.Thread(target=self._hsv_worker, daemon=True),
            threading.Thread(target=self._yolo_worker, daemon=True),
            threading.Thread(target=self._result_worker, daemon=True),
        ]
        for t in threads:
            t.start()
    
    def _hsv_worker(self):
        while True:
            frame = self.capture.get_frame()
            mask = create_hsv_mask(frame, HSV_RANGES["red"])
            rois = extract_rois(frame, mask)
            self.hsv_queue.put((frame, rois))
    
    def _yolo_worker(self):
        model = YOLO("yolo11n_openvino_model/")
        while True:
            frame, rois = self.hsv_queue.get()
            detections = detect_in_rois(model, frame, rois)
            self.yolo_queue.put((frame, detections))
    
    def _result_worker(self):
        while True:
            frame, detections = self.yolo_queue.get()
            # Handle alerts, logging, visualization
            pass
```

## Performance Metrics (N100 + OpenVINO)

| Stage | Time (ms) | CPU% | Notes |
|-------|-----------|------|-------|
| RTSP Capture | 2-5 | 5% | Network bound |
| HSV Filter | 3-8 | 10% | Parallelizable |
| ROI Extraction | 2-5 | 5% | Fast |
| YOLO (1-3 ROIs) | 15-40 | 30% | Main cost |
| **Total per frame** | **25-58** | **~50%** | **17-40 FPS** |

## References
- **OpenCV RTSP**: https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html
- **HSV Color Space**: https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html
- **Ultralytics ROI**: https://docs.ultralytics.com/modes/predict/#inference-sources
- **OpenVINO YOLO**: https://docs.ultralytics.com/integrations/openvino