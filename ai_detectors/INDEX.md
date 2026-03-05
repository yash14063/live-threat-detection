"""
📚 INDEX & NAVIGATION GUIDE
============================
Master guide for navigating the ThreatSense AI Detection System
"""

# ThreatSense AI Detection System - Master Index

## 🗂️ File Navigator

### 📖 Documentation (Read These First)

| File | Purpose | Time | Start Here? |
|------|---------|------|-------------|
| **SUMMARY.md** | Project completion overview | 5 min | ✅ YES |
| **QUICK_REFERENCE.md** | Developer quick guide | 10 min | ✅ YES |
| **README.md** | Complete API documentation | 30 min | After QUICK_REFERENCE |
| **DEPLOYMENT.md** | Production deployment guide | 20 min | Before going live |

### 🔧 Core System Files

| File | Purpose | Lines | When to Read |
|------|---------|-------|--------------|
| **base_detector.py** | Abstract base class | 150+ | Understand architecture |
| **config.py** | Configuration & thresholds | 200+ | Customize behavior |
| **__init__.py** | Package initialization | 20 | Understand imports |

### 🎯 Threat Detectors

| File | Threat Type | Lines | Key Algorithm |
|------|------------|-------|-----------------|
| **shoplifting_detector.py** | Retail theft | 250+ | Hand movement tracking |
| **fall_detector.py** | Medical emergency | 180+ | Aspect ratio analysis |
| **assault_detector.py** | Violence | 220+ | Geometric proximity |
| **crowd_analyzer.py** | Crowd behavior | 200+ | Density counting |

### 🤖 AI/ML Model Wrappers

| File | Model | Purpose | Lines |
|------|-------|---------|-------|
| **models/mediapipe_pose.py** | Mediapipe | Skeleton detection | 200+ |
| **models/yolo_detector.py** | YOLOv8 | Object detection | 250+ |
| **models/cnn_classifier.py** | PyTorch CNN | Threat classification | 200+ |

### 🛠️ Utility Modules

| File | Purpose | Functions | When to Use |
|------|---------|-----------|-------------|
| **utils/pose_utils.py** | Math operations | 10+ | Geometric calculations |
| **utils/visualization.py** | Drawing overlays | 5+ | Visualization |

### 💻 Implementation & Testing

| File | Purpose | Type | Use Case |
|------|---------|------|----------|
| **example_integration.py** | Working example | Implementation | Reference/Template |
| **test_detectors.py** | Test suite | Testing | Validation |
| **requirements.txt** | Dependencies | Configuration | Installation |

---

## 🚀 Usage Scenarios & File Reference

### Scenario 1: "I want to understand the system"
**Read order**:
1. SUMMARY.md (overview)
2. QUICK_REFERENCE.md (concepts)
3. README.md (details)

### Scenario 2: "I want to modify detection thresholds"
**Files to edit**:
1. config.py - Adjust THRESHOLDS dictionaries
2. Reference: QUICK_REFERENCE.md → "Configuration" section

### Scenario 3: "I want to add a new threat detector"
**Files to study**:
1. base_detector.py - Understand BaseDetector abstract class
2. shoplifting_detector.py - Use as template
3. config.py - Add your thresholds
4. __init__.py - Register your detector

### Scenario 4: "I want to integrate with my FastAPI backend"
**Files to read**:
1. example_integration.py - See ThreatSenseProcessor
2. README.md → "Integration with main.py" section
3. DEPLOYMENT.md - For production setup

### Scenario 5: "I want to deploy to production"
**Files to follow**:
1. DEPLOYMENT.md - Step-by-step guide
2. QUICK_REFERENCE.md → "Performance Metrics" section
3. Docker templates in DEPLOYMENT.md

### Scenario 6: "I want to validate the system"
**Files to run**:
1. Test command: `python test_detectors.py`
2. Example command: `python example_integration.py`
3. Reference: README.md → "Testing & Validation"

---

## 🎯 Quick Command Reference

```bash
# Installation
pip install -r ai_detectors/requirements.txt

# Run tests (validate installation)
python ai_detectors/test_detectors.py

# Run working example (test with webcam)
python ai_detectors/example_integration.py

# Run specific test
python -m pytest ai_detectors/test_detectors.py::TestDetectors -v

# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Download YOLO model
python -c "from ultralytics import YOLO; YOLO('yolov8m.pt')"
```

---

## 📊 System Architecture Quick View

```
┌─────────────────────────────────────┐
│     Video Input (Camera/File)       │
└──────────────┬──────────────────────┘
               │
      ┌────────▼────────┐
      │   AI Models     │
      ├─────────────────┤
      │ • Mediapipe     │
      │ • YOLO          │
      │ • CNN           │
      └────────┬────────┘
               │
      ┌────────▼──────────────┐
      │  Threat Detectors     │
      ├───────────────────────┤
      │ • Shoplifting (75%)   │
      │ • Fall (95% threat)   │
      │ • Assault (70-95%)    │
      │ • Crowd (0-60%)       │
      └────────┬──────────────┘
               │
      ┌────────▼──────────┐
      │   Outputs         │
      ├───────────────────┤
      │ • Alerts (JSON)   │
      │ • Stats           │
      │ • Visualization   │
      └───────────────────┘
```

---

## 🔍 Finding Things in the Codebase

### "How do I..."

**...configure detection thresholds?**
- File: `config.py`
- Read: QUICK_REFERENCE.md → "Configuration"

**...detect a specific threat?**
- For Fall: `fall_detector.py`
- For Shoplifting: `shoplifting_detector.py`
- For Assault: `assault_detector.py`
- For Crowds: `crowd_analyzer.py`

**...understand what each detector does?**
- File: `README.md` → "Detector Documentation" section

**...use the models directly?**
- Pose: `models/mediapipe_pose.py`
- Objects: `models/yolo_detector.py`
- Classification: `models/cnn_classifier.py`

**...do math with skeleton data?**
- File: `utils/pose_utils.py`

**...draw visualizations?**
- File: `utils/visualization.py`

**...see a working example?**
- File: `example_integration.py`

**...test the system?**
- File: `test_detectors.py`

**...deploy to production?**
- File: `DEPLOYMENT.md`

**...troubleshoot issues?**
- Files: QUICK_REFERENCE.md → "Debugging Tips"
- Files: DEPLOYMENT.md → "Pre-Deployment Checklist"

---

## 📚 Reading Roadmap

### For Quick Setup (15 min)
1. SUMMARY.md (5 min) - see what was built
2. QUICK_REFERENCE.md - common patterns (10 min)

### For Understanding (1 hour)
1. SUMMARY.md (5 min)
2. README.md (30 min) - all detectors
3. QUICK_REFERENCE.md (25 min) - API reference

### For Implementation (2 hours)
1. SUMMARY.md
2. example_integration.py - read the code
3. README.md → "Integration with main.py"
4. QUICK_REFERENCE.md → "Testing" section

### For Production (4 hours)
1. All above files
2. DEPLOYMENT.md - complete guide
3. test_detectors.py - run tests
4. example_integration.py - verify locally

---

## 🎓 Learning Path by Role

### For Architect
1. SUMMARY.md - overview
2. README.md → "Architecture" section
3. base_detector.py - design pattern
4. DEPLOYMENT.md - scalability

### For Developer
1. QUICK_REFERENCE.md - APIs
2. example_integration.py - working code
3. Each detector module - implementation
4. test_detectors.py - patterns

### For DevOps
1. DEPLOYMENT.md - production setup
2. Docker section - containerization
3. Monitoring section - observability
4. requirements.txt - dependencies

### For Operations
1. DEPLOYMENT.md → "Post-Deployment Checklist"
2. QUICK_REFERENCE.md → "Common Issues"
3. DEPLOYMENT.md → "Monitoring & Logging"
4. Backup procedures - disaster recovery

### For QA/Testing
1. test_detectors.py - test suite
2. README.md → "Testing & Validation"
3. QUICK_REFERENCE.md → "Debugging Tips"
4. example_integration.py - test scenarios

---

## 🔗 Cross-References

### Understanding Alert Flow
1. See BaseDetector.format_alert() in base_detector.py
2. See example_integration.py how alerts are sent
3. See README.md "Integration with main.py" for receiver code

### Understanding Configuration
1. config.py contains all thresholds
2. QUICK_REFERENCE.md shows how to modify
3. Each detector reads from config.py

### Understanding Models
1. models/mediapipe_pose.py - returns poses
2. models/yolo_detector.py - returns objects
3. Each detector uses these in detect() method

### Understanding Data Flow
1. Start: example_integration.py process_frame()
2. Middle: each detector.detect()
3. End: results formatted as JSON

---

## 📋 File Checklist

Essential files to copy/maintain:

```
Required for Runtime:
☑ base_detector.py
☑ config.py
☑ shoplifting_detector.py
☑ fall_detector.py
☑ assault_detector.py
☑ crowd_analyzer.py
☑ models/mediapipe_pose.py
☑ models/yolo_detector.py
☑ models/cnn_classifier.py
☑ utils/pose_utils.py
☑ utils/visualization.py
☑ __init__.py (main and in subdirs)
☑ requirements.txt

Recommended for Development:
☑ example_integration.py
☑ test_detectors.py

Essential for Reference:
☑ README.md
☑ QUICK_REFERENCE.md
☑ DEPLOYMENT.md
☑ SUMMARY.md (this file)
```

---

## 🚨 Critical Files Don't Delete

These files are core to system functionality:
- ❌ base_detector.py - All detectors inherit from this
- ❌ config.py - All thresholds defined here
- ❌ models/*.py - Required for AI/ML operations
- ❌ utils/*.py - Required for calculations

---

## 📞 Support Decision Tree

```
Problem?
│
├─ "System not working" → SUMMARY.md
│                      → test_detectors.py
│
├─ "Wrong detections" → QUICK_REFERENCE.md (Configuration)
│                     → Adjust config.py thresholds
│
├─ "Slow performance" → QUICK_REFERENCE.md (Performance Metrics)
│                     → Use lighter models (yolov8n)
│
├─ "Integration issue" → example_integration.py
│                      → README.md (Integration section)
│
├─ "Deployment help" → DEPLOYMENT.md
│                   → docker-compose.yml template
│
└─ "How do I..." → QUICK_REFERENCE.md (FAQ section)
```

---

## 🎯 Success Criteria

✅ All files in correct location  
✅ All imports working (test_detectors.py passes)  
✅ Example runs without errors  
✅ Configuration adjustable  
✅ Ready for integration with main.py  

---

## 📝 Quick Reference Card

```
QUICK COMMANDS:
  Installation:    pip install -r requirements.txt
  Test:           python test_detectors.py
  Example:        python example_integration.py
  
CORE CLASSES:
  BaseDetector    - Abstract base for all detectors
  FallDetector    - Medical emergency detection
  Config          - All thresholds and parameters
  
KEY METHODS:
  detect()        - Run detection on frame
  get_detection_stats() - Get detector statistics
  
MODELS:
  MediapipePoseDetector  - Skeleton (33 points)
  YOLODetector          - Objects (people, weapons)
  CNNClassifier         - Threat classification
  
ALERT STRUCTURE:
  {
    "alert_triggered": bool,
    "threat_type": str,
    "threat_score": int (0-100),
    "detector": str,
    "timestamp": int
  }
```

---

**Navigation Guide Version**: 1.0  
**Last Updated**: 2024  
**Status**: Complete ✅
