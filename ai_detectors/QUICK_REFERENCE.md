"""
Quick Reference Guide - ThreatSense AI Detection Architecture
==============================================================

FILE: QUICK_REFERENCE.md
PURPOSE: Developer quick start and API reference

"""

# ThreatSense AI Detection - Quick Reference

## 🎯 System Overview

```
┌─────────────────┐
│  Video Stream   │ (Camera, File, or RTSP)
└────────┬────────┘
         │
    ╔════▼════╗
    ║ Models  ║ (Mediapipe, YOLO, CNN)
    ╚════╤════╝
         │
    ╔════▼═══════════════════════════╗
    ║   Threat Detectors             ║
    ║ ┌──────────────────────────────┐║
    ║ │ • Shoplifting Detector       │║
    ║ │ • Fall Detector              │║
    ║ │ • Assault Detector           │║
    ║ │ • Crowd Analyzer             │║
    ║ └──────────────────────────────┘║
    ╚════╤══════════════════════════╝
         │
    ╔════▼════════════╗
    ║  Results        ║
    ║  & Alerts       ║
    ║  (WebSocket)    ║
    ╚═════════════════╝
```

---

## 📦 Essential Imports

### Load Everything
```python
from ai_detectors import (
    ShopliftingDetector,
    FallDetector,
    AssaultDetector,
    CrowdAnalyzer
)
from ai_detectors.models import MediapipePoseDetector, YOLODetector
from example_integration import ThreatSenseProcessor
```

### Minimal Setup (Browser-based)
```python
from ai_detectors.models import MediapipePoseDetector
pose_detector = MediapipePoseDetector()
```

### Models Only
```python
from ai_detectors.models import MediapipePoseDetector, YOLODetector
pose = MediapipePoseDetector(model_complexity=0)
yolo = YOLODetector(model_name="yolov8m.pt")
```

---

## 🚀 Common Usage Patterns

### Pattern 1: Detect Single Frame
```python
import cv2
from ai_detectors import FallDetector
from ai_detectors.models import MediapipePoseDetector

detector = FallDetector()
pose_model = MediapipePoseDetector()

frame = cv2.imread("test.jpg")
poses = pose_model.detect(frame)
result = detector.detect(frame, poses, objects=[])

if result["alert_triggered"]:
    print(f"Alert: {result['threat_message']}")
```

### Pattern 2: Process Video Stream
```python
from example_integration import ThreatSenseProcessor

processor = ThreatSenseProcessor()
processor.process_video_stream(video_source=0)  # Webcam
```

### Pattern 3: WebSocket Integration
```python
from starlette.websockets import WebSocket
from example_integration import ThreatSenseProcessor

processor = ThreatSenseProcessor()

# In your WebSocket handler:
frame = receive_frame()
results = processor.process_frame(frame, websocket=ws)
await ws.send_json({"alerts": results["alerts"]})
```

---

## 🔧 Configuration (config.py)

### Adjust Detection Thresholds
```python
from ai_detectors.config import SHOPLIFTING_THRESHOLDS, FALL_THRESHOLDS

# Default values:
SHOPLIFTING_THRESHOLDS = {
    "min_hand_distance_to_hip": 40,      # pixels
    "min_trajectory_length": 50,         # pixels
    "min_frames_to_confirm": 5,          # frames
    "cooldown_ms": 3000                  # milliseconds
}

FALL_THRESHOLDS = {
    "aspect_ratio_threshold": 0.8,       # width/height ratio
    "min_frames_to_confirm": 3,
    "cooldown_ms": 5000
}

# Modify as needed:
SHOPLIFTING_THRESHOLDS["cooldown_ms"] = 1000  # Faster alerts
FALL_THRESHOLDS["aspect_ratio_threshold"] = 0.75  # More sensitive
```

### Adjust Model Parameters
```python
from ai_detectors.config import MEDIAPIPE_CONFIG, YOLO_CONFIG

MEDIAPIPE_CONFIG = {
    "static_image_mode": False,
    "model_complexity": 1,              # 0=lite, 1=full, 2=heavy
    "smooth_landmarks": True,
    "min_detection_confidence": 0.5,
    "min_tracking_confidence": 0.5
}

YOLO_CONFIG = {
    "confidence_threshold": 0.45,
    "iou_threshold": 0.5,
    "imgsz": 640
}
```

---

## 📊 Detector API Reference

### Detector Interface (All Detectors)
```python
# Initialization
detector = FallDetector()

# Run detection
result = detector.detect(
    frame: np.ndarray,           # Video frame (BGR)
    poses: List[Pose],           # From Mediapipe
    objects: List[Detection]     # From YOLO
) -> Dict

# Get statistics
stats = detector.get_detection_stats()
# Returns: {"total_detections": 5, "total_alerts": 2, ...}

# Check alert eligibility (cooldown)
can_alert = detector.should_trigger_alert("pattern_name")  # bool

# Format alert for sending
alert = detector.format_alert(threat_message, threat_score, pattern)
```

### Result Dictionary Structure
```python
{
    "alert_triggered": bool,          # True if threat detected
    "threat_type": str,               # e.g., "Fall/Medical Emergency"
    "threat_message": str,            # e.g., "Person has fallen"
    "threat_score": int,              # 0-100 severity
    "pattern": str,                   # Detection pattern name
    "timestamp": int,                 # Unix timestamp (ms)
    "detector": str,                  # Detector class name
    "confidence": float               # 0-1 detection confidence
}
```

---

## 🎬 Model Output Formats

### Mediapipe Pose Output
```python
poses = pose_detector.detect(frame)
# Returns: List[Pose]

pose = poses[0]
pose.keypoints        # List[Dict] with x, y, confidence
pose.bounding_box     # (x, y, w, h)
pose.person_id        # Integer tracking ID
pose.confidence       # 0-1 overall pose confidence

# Keypoint indices:
# 0: Nose, 3-4: Eyes, 9-10: Wrists, 23-24: Hips, etc.
# See: https://google.github.io/mediapipe/solutions/pose.html
```

### YOLO Object Detection Output
```python
objects = yolo_detector.detect(frame)
# Returns: List[Detection]

detection = objects[0]
detection.class_name    # e.g., "person", "knife", "gun"
detection.class_id      # Integer class ID (0=person)
detection.confidence    # 0-1 detection confidence
detection.x1, detection.y1, detection.x2, detection.y2  # Bounding box
detection.area          # Width * height
detection.center_x      # Box center X
detection.center_y      # Box center Y

# Get people count
count = yolo_detector.get_people_count(objects)
```

---

## 📈 Performance Metrics

### Latency Benchmarks (on CPU)
```
Operation             | Latency    | Notes
─────────────────────────────────────────────────────
Mediapipe (lite)      | 15-30 ms   | Model complexity 0
Mediapipe (full)      | 40-80 ms   | Model complexity 1
YOLO nano (320px)     | 10-15 ms   | Small objects ignored
YOLO small (320px)    | 20-30 ms   | Recommended balance
YOLO medium (640px)   | 40-60 ms   | High accuracy
Fall Detection        | <5 ms      | Post-processing only
Shoplifting Detection | <5 ms      | Pose analysis only
Assault Detection     | <5 ms      | Geometry only
Total Pipeline        | 50-100 ms  | 10-20 fps possible
```

### GPU Acceleration
```python
import torch

if torch.cuda.is_available():
    # 5-10x faster for YOLO
    yolo_detector = YOLODetector(model_name="yolov8m.pt")
    yolo_detector.model.to("cuda")
```

---

## 🧪 Testing & Validation

### Quick Test
```python
from ai_detectors import FallDetector
from ai_detectors.utils.pose_utils import get_skeleton_aspect_ratio

detector = FallDetector()
print(f"Detector: {detector.detector_name}")
print(f"Status: READY")

# Test geometry utils
from ai_detectors.utils.pose_utils import calculate_distance
dist = calculate_distance({"x": 0, "y": 0}, {"x": 3, "y": 4})
print(f"Distance test: {dist} == 5.0? {abs(dist - 5.0) < 0.01}")
```

### Run Full Test Suite
```bash
python test_detectors.py
```

### Run Specific Tests
```bash
python -m pytest test_detectors.py::TestDetectors::test_fall_detector_initialization -v
```

---

## 🔐 Security Notes

1. **Frame Privacy**: Input frames are processed locally, not stored
2. **Model Privacy**: No data leaves the host unless explicitly sent
3. **Rate Limiting**: Detectors include cooldown to prevent spam
4. **Validation**: All detectors validate input before processing
5. **Logging**: Comprehensive logging for audit trails

---

## 🐛 Debugging Tips

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

detector = FallDetector()
result = detector.detect(frame, poses, objects)
# Will print detailed detection info
```

### Visualize Detections
```python
from ai_detectors.utils.visualization import SkeletonVisualizer

frame = SkeletonVisualizer.draw_skeleton(frame, poses[0])
frame = SkeletonVisualizer.draw_detection_box(frame, detection)
frame = SkeletonVisualizer.draw_alert_box(
    frame,
    title="Fall Detected",
    message="Person has fallen",
    threat_score=95
)

cv2.imshow("Debug View", frame)
cv2.waitKey(0)
```

### Check Model Status
```python
processor = ThreatSenseProcessor()
status = processor.get_system_status()
print(json.dumps(status, indent=2))
```

---

## 📚 File Cross-Reference

| Need to...          | File to Check     | Key Function          |
|─────────────────────|───────────────────|───────────────────────|
| Add new threat type | base_detector.py  | Inherit from BaseDetector |
| Adjust thresholds   | config.py         | Modify THRESHOLD dicts     |
| Use Mediapipe       | models/mediapipe_pose.py | detect()        |
| Use YOLO            | models/yolo_detector.py | detect()         |
| Draw overlays       | utils/visualization.py | SkeletonVisualizer |
| Math operations     | utils/pose_utils.py | calculate_*() |
| Full integration    | example_integration.py | ThreatSenseProcessor |
| Run tests           | test_detectors.py | unittest suite           |

---

## 🆘 Common Issues

### Issue: "ModuleNotFoundError: No module named 'mediapipe'"
```bash
# Fix: Install dependencies
pip install -r requirements.txt
```

### Issue: "YOLO model not found"
```bash
# Fix: Download model
python -c "from ultralytics import YOLO; YOLO('yolov8m.pt')"
```

### Issue: Low FPS / Slow Detection
```python
# Fix: Use lite models
yolo = YOLODetector(model_name="yolov8n.pt")  # nano = fastest
pose = MediapipePoseDetector(model_complexity=0)  # lite
```

### Issue: Too Many False Alerts
```python
# Fix: Adjust cooldown and thresholds
from ai_detectors.config import FALL_THRESHOLDS
FALL_THRESHOLDS["cooldown_ms"] = 5000  # Increase cooldown
FALL_THRESHOLDS["min_frames_to_confirm"] = 5  # Require more frames
```

---

## 📞 Support & Contributing

- **GitHub Issues**: Report bugs and request features
- **Documentation**: See README.md for full API docs
- **Examples**: Check example_integration.py for patterns
- **Tests**: Run test_detectors.py to validate changes

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
