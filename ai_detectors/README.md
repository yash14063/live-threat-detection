# ThreatSense AI Detection System
## Modular Threat Detection Architecture

This directory contains the core AI/ML detection modules for ThreatSense, organized using professional software engineering patterns.

---

## 📁 Directory Structure

```
ai_detectors/
├── __init__.py                 # Package initialization
├── config.py                   # Centralized configuration (thresholds, model params)
├── base_detector.py            # Abstract base class for all detectors
│
├── shoplifting_detector.py     # Retail theft detection (Mediapipe)
├── fall_detector.py            # Medical emergency detection (Skeleton AR)
├── assault_detector.py         # Violence & multi-person interaction (Pose estimation)
├── crowd_analyzer.py           # Crowd density & behavior analysis (YOLO CNN)
│
├── models/                     # Deep learning model wrappers
│   ├── __init__.py
│   ├── mediapipe_pose.py       # Mediapipe pose estimation wrapper (33-point skeleton)
│   ├── yolo_detector.py        # Ultralytics YOLOv8 object detection
│   └── cnn_classifier.py       # Custom CNN-based threat classification
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── pose_utils.py           # Geometric calculations (distance, angle, aspect ratio)
│   └── visualization.py        # Drawing functions (skeleton, boxes, alerts)
│
├── example_integration.py       # Complete working example with WebSocket
├── test_detectors.py           # Unit tests & integration tests
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── DEPLOYMENT.md               # Production deployment guide
```

---

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install mediapipe ultralytics opencv-python torch torchvision

# Or install from requirements
pip install -r requirements.txt
```

### Basic Usage

```python
from ai_detectors import ShopliftingDetector, FallDetector, AssaultDetector, CrowdAnalyzer
from ai_detectors.models import MediapipePoseDetector, YOLODetector

# Initialize detectors
shoplifting = ShopliftingDetector()
fall = FallDetector()
assault = AssaultDetector()
crowd = CrowdAnalyzer()

# Initialize models
pose_detector = MediapipePoseDetector()
yolo_detector = YOLODetector(model_name="yolov8m.pt")

# Main detection loop
import cv2

cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Run detections
    poses = pose_detector.detect(frame)
    objects = yolo_detector.detect(frame)
    
    # Analyze threats
    shoplifting_result = shoplifting.detect(frame, poses, objects)
    fall_result = fall.detect(frame, poses, objects)
    assault_result = assault.detect(frame, poses, objects)
    crowd_result = crowd.detect(frame, poses, objects)
    
    # Send to backend if alert
    if shoplifting_result["alert_triggered"]:
        print(f"🚨 ALERT: {shoplifting_result['threat_message']}")
        # Send to WebSocket backend

cap.release()
```

---

## � Complete Integration Example

For a production-ready implementation, use the included `example_integration.py`:

```bash
# Run the full system with a webcam
python example_integration.py

# Or integrate into your FastAPI backend:
from example_integration import ThreatSenseProcessor

processor = ThreatSenseProcessor()

# Get system status
status = processor.get_system_status()

# Process single frame
results = processor.process_frame(frame, websocket=ws_connection)

# Process continuous stream
processor.process_video_stream(video_source=0, websocket=ws_connection)
```

**Key Features of Integration Example:**
- ✅ Loads all models and detectors with proper initialization
- ✅ Runs detectors sequentially on each frame
- ✅ Sends alerts via WebSocket in real-time
- ✅ Draws visualization overlays
- ✅ Logs comprehensive statistics
- ✅ Handles errors gracefully

---

## ✅ Testing & Validation

Run the included test suite to verify system functionality:

```bash
# Run all tests
python test_detectors.py

# Expected output:
# ✓ Pose utilities working
# ✓ Detector initialization
# ✓ Alert cooldown mechanisms
# ✓ Multi-detector pipeline
# ✓ Model wrappers available
```

**Test Coverage:**
- Geometric calculations (distance, angle, aspect ratio)
- Detector initialization and statistics
- Alert cooldown and spam prevention
- Model loading (Mediapipe, YOLO, CNN)
- Multi-detector pipeline execution
- Alert aggregation and formatting

---

## �📊 Detector Documentation

### 1. **Shoplifting Detector** (Walmart Retail Theft)
**File:** `shoplifting_detector.py`

**Detection Method:** Hand trajectory analysis using Mediapipe pose
- Identifies hand movement from rack level → pocket (THEFT)
- Distinguishes from legitimate shopping (items → cart)
- Tracks hand movement history (15-frame buffer)

**Threat Score:** 75 (HIGH) when suspicious pattern detected

**Configuration:**
```python
SHOPLIFTING_THRESHOLDS = {
    "min_hand_distance_to_hip": 40,      # pixels
    "min_movement_history": 5,           # frames
    "min_vertical_distance": 10,         # pixels (downward)
    "shoulder_height_buffer": -20,       # offset
    "threat_score": 75,
    "cooldown_ms": 3000,
}
```

---

### 2. **Fall Detector** (Medical Emergency)
**File:** `fall_detector.py`

**Detection Method:** Skeleton aspect ratio analysis
- Calculates shoulder_width / body_height
- Ratio > 0.8 indicates prone/lying position
- Requires 3+ consecutive frames (false positive reduction)

**Threat Score:** 95 (CRITICAL) - immediate emergency response

**Configuration:**
```python
FALL_DETECTION_THRESHOLDS = {
    "aspect_ratio_threshold": 0.8,
    "confidence_threshold": 0.3,
    "threat_score": 95,
}
```

---

### 3. **Assault Detector** (Violence & Multi-Person Interaction)
**File:** `assault_detector.py`

**Detection Methods:**
1. **Strangulation/Choking** - Wrist-to-Face distance < 50px
2. **Pickpocketing** - Wrist-to-Hip distance < 45px
3. **Weapon-Assisted** - Object detection during assault (YOLO)

**Threat Scores:**
- Neck contact: 95 (CRITICAL)
- Pickpocketing: 70 (HIGH)

**Configuration:**
```python
ASSAULT_DETECTION_THRESHOLDS = {
    "neck_contact_distance": 50,         # pixels
    "hip_distance": 45,                  # pixels
    "min_poses_required": 2,
    "neck_threat_score": 95,
    "pickpocket_threat_score": 70,
}
```

---

### 4. **Crowd Analyzer** (Density & Behavior)
**File:** `crowd_analyzer.py`

**Features:**
- Real-time person counting (YOLO CNN)
- Non-human filtering (pets, shadows, objects)
- Crowd density classification: low → medium → high → critical
- Anomaly detection when density escalates

**Threat Scores by Density:**
- Low (0-10): 0
- Medium (10-25): 20
- High (25-50): 40
- Critical (50+): 60

**Configuration:**
```python
CROWD_ANALYSIS_THRESHOLDS = {
    "crowd_density_levels": {
        "low": (0, 10),
        "medium": (10, 25),
        "high": (25, 50),
        "critical": (50, float("inf")),
    },
}
```

---

## 🧠 Deep Learning Models

### Mediapipe Pose Estimation
**File:** `models/mediapipe_pose.py`

**Output:** 33-point skeleton per person
- Head & face (8 points)
- Torso (3 points)
- Arms (8 points)
- Hands (10 points)
- Legs (4 points)

Each point includes: x, y, z, confidence_score

**Advantages:**
- Fast (real-time on CPU)
- Multi-person support
- Accurate for retail/public environments
- Zero setup - works out-of-box

---

### YOLO Object Detection
**File:** `models/yolo_detector.py`

**Supported Models:**
- `yolov8n.pt` - Nano (fast, mobile)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (recommended)
- `yolov8l.pt` - Large (accurate)
- `yolov8x.pt` - Extra (maximum precision)

**Detected Classes:** person, weapon, knife, gun, backpack, luggage, etc.

**Output:** [class, confidence, bbox, area, center]

---

### CNN Threat Classifier
**File:** `models/cnn_classifier.py`

**Architectures:**
- ResNet50 (recommended - balanced)
- EfficientNet (mobile-optimized)
- VGG16 (small datasets)
- Custom (user-trained)

**Binary Classification:** Safe (0) vs Threat (1)

**Example:**
```python
from ai_detectors.models import CNNClassifier

classifier = CNNClassifier(model_architecture="resnet50")
result = classifier.classify_patch(image_region)
# Returns: {"threat": bool, "threat_score": 0-1, "confidence": 0-1}
```

---

## 🛠️ Utility Functions

### Pose Utils (`pose_utils.py`)
- `calculate_distance()` - Euclidean distance between keypoints
- `calculate_angle()` - Joint angle (elbow bend, knee bend)
- `get_skeleton_aspect_ratio()` - Body width/height for fall detection
- `get_body_center()` - Center of mass
- `is_hand_raised()` - Hand elevation check
- `smooth_trajectory()` - Reduce detection jitter

### Visualization (`visualization.py`)
- `draw_skeleton()` - Overlay skeleton on frame
- `draw_detection_box()` - Bounding box with label
- `draw_alert_box()` - Prominent threat alert overlay
- `draw_stats()` - Performance/status metrics

---

## ⚙️ Configuration (`config.py`)

All thresholds, model parameters, and constants are centralized in `config.py`:

```python
# Model paths and parameters
MEDIAPIPE_CONFIG = {...}
YOLO_CONFIG = {...}
CNN_CONFIG = {...}

# Detection thresholds
SHOPLIFTING_THRESHOLDS = {...}
FALL_DETECTION_THRESHOLDS = {...}
ASSAULT_DETECTION_THRESHOLDS = {...}
CROWD_ANALYSIS_THRESHOLDS = {...}

# Alert types and severity
ALERT_TYPES = {...}
THREAT_LEVELS = {...}
```

**To modify:**
```python
# In your main application
from ai_detectors import config
config.SHOPLIFTING_THRESHOLDS["threat_score"] = 80  # Increase sensitivity
```

---

## 📈 Performance Metrics

Each tracker maintains statistics:

```python
# Get detection statistics
stats = shoplifting.get_detection_stats()
# Returns: {"total": int, "critical": int, "high": int, "recent_average_score": float}

stats = fall.get_fall_stats()
# Returns: {..., "total_falls_detected": int, "currently_tracking_fall": bool}

stats = crowd.get_crowd_stats()
# Returns: {..., "current_person_count": int, "density_level": str}
```

---

## 🔗 Integration with Backend

All detectors format output for WebSocket transmission:

```python
if detection_result["alert_triggered"]:
    alert_data = {
        "camera_id": "CAM_01",
        "alert_type": detection_result["threat_message"],
        "threat_score": detection_result["threat_score"],
        "pattern": detection_result["pattern"],
        "detector": detection_result["detector"],
        "timestamp": detection_result["timestamp"]
    }
    # Send via WebSocket to main.py backend
    ws.send(json.dumps(alert_data))
```

---

## 🏗️ Integration with main.py FastAPI Backend

The AI detectors are designed to integrate seamlessly with the FastAPI backend:

### Step 1: Import Detectors in main.py

```python
# main.py
from ai_detectors import (
    ShopliftingDetector,
    FallDetector,
    AssaultDetector,
    CrowdAnalyzer
)
from ai_detectors.models import MediapipePoseDetector, YOLODetector
from example_integration import ThreatSenseProcessor

# Initialize processor once at startup
processor = ThreatSenseProcessor()
```

### Step 2: Update WebSocket Handler

```python
@app.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: str):
    await websocket.accept()
    
    while True:
        # Receive frame from client
        frame_data = await websocket.receive_bytes()
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Process through AI detector pipeline
        results = processor.process_frame(frame, websocket)
        
        # Send results back to frontend
        response = {
            "camera_id": camera_id,
            "alerts": results["alerts"],
            "threat_level": max([a["threat_score"] for a in results["alerts"]], default=0),
            "people_detected": results["frame_stats"]["people_detected"],
            "timestamp": int(time.time() * 1000)
        }
        
        await websocket.send_json(response)
```

### Step 3: Update Database Schema

```python
# Ensure your threat_events table has these columns:
CREATE TABLE IF NOT EXISTS threat_events (
    id INTEGER PRIMARY KEY,
    camera_id TEXT,
    threat_score INTEGER,
    threat_type TEXT,
    pattern TEXT,
    detector_name TEXT,
    location TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Step 4: Update Frontend (index.html)

```javascript
// Connect to detector WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/CAM_01');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Update threat score display
    updateThreatScore(data.threat_level);
    
    // Add alerts to log
    for (const alert of data.alerts) {
        addAlert({
            type: alert.threat_type,
            message: alert.message,
            score: alert.threat_score,
            detector: alert.detector
        });
    }
    
    // Update people count
    document.getElementById('people-count').textContent = data.people_detected;
};
```

---

## 🚀 Deployment Checklist

- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Download YOLO model: `pip install ultralytics && python -c "from ultralytics import YOLO; YOLO('yolov8m.pt')"`
- [ ] Run tests: `python test_detectors.py`
- [ ] Configure thresholds in `config.py` for your environment
- [ ] Integrate with `main.py` using example above
- [ ] Test end-to-end with `python example_integration.py`
- [ ] Monitor Mediapipe/YOLO latency: aim for <100ms per frame
- [ ] Scale with `torch.cuda.is_available()` for GPU acceleration
- [ ] Set up proper logging and alerting to your monitoring system

---

## 🎛️ Performance Tuning

### For Real-Time Performance:

```python
# Use yolov8n (nano) for speed, yolov8m (medium) for balance
processor.yolo_detector = YOLODetector(model_name="yolov8n.pt")

# Use Mediapipe lite for speed
processor.pose_detector = MediapipePoseDetector(model_complexity=0)

# Enable GPU if available
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
```

### Expected Latencies:
- Mediapipe Pose (lite): 15-30 ms
- YOLO-nano: 10-20 ms
- YOLO-medium: 30-50 ms
- Fall Detection: <5 ms
- Shoplifting Detection: <5 ms
- Assault Detection: <5 ms
- Total Frame Processing: 50-100 ms (real-time at 10 fps)

---

## 📚 Dependencies

```
mediapipe>=0.10.0              # Pose estimation
ultralytics>=8.0.0              # YOLO object detection
opencv-python>=4.8.0            # Image processing
torch>=2.0.0                    # Deep learning framework
torchvision>=0.15.0             # Vision models
numpy>=1.24.0                   # Numerical computing
```

---

## 🧪 Testing

```python
# Unit test for shoplifting detector
from ai_detectors import ShopliftingDetector
import numpy as np

detector = ShopliftingDetector()

# Simulate frame and poses
frame = np.zeros((600, 800, 3), dtype=np.uint8)
poses = [...]  # Mock pose data
objects = [...]  # Mock object data

result = detector.detect(frame, poses, objects)
assert isinstance(result, dict)
assert "alert_triggered" in result
assert "threat_score" in result
```

---

## 📝 License & Credits

ThreatSense AI Detection System
- Google Mediapipe for pose estimation
- Ultralytics for YOLOv8
- PyTorch/TensorFlow for deep learning

---

## 🤝 Contributing

To add a new detector:

1. Create `new_detector.py` inheriting from `BaseDetector`
2. Implement `detect()` method
3. Add configuration to `config.py`
4. Export in `__init__.py`
5. Add tests and documentation

```python
from .base_detector import BaseDetector

class NewDetector(BaseDetector):
    def __init__(self):
        super().__init__(detector_name="NEW_DETECTOR", threat_type="CUSTOM")
    
    def detect(self, frame, poses, objects) -> Dict:
        # Your detection logic here
        return self.format_alert(message, threat_score, pattern)
```

---

**Last Updated:** March 6, 2026
**Version:** 1.0.0
