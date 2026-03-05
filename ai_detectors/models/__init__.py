"""
Model Wrappers for ThreatSense AI Detection
============================================
Unified interfaces for:
- Mediapipe (pose estimation, hand tracking)
- Ultralytics YOLO (object detection, segmentation)
- CNN models (custom threat classification)
"""

from .mediapipe_pose import MediapipePoseDetector
from .yolo_detector import YOLODetector
from .cnn_classifier import CNNClassifier

__all__ = [
    "MediapipePoseDetector",
    "YOLODetector",
    "CNNClassifier",
]
