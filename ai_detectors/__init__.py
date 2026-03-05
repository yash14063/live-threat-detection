"""
ThreatSense AI Detection Module
================================
Comprehensive detection system for retail security, public safety, and emergency response.

Sub-modules:
- shoplifting_detector: Walmart retail theft detection (rack-to-pocket patterns)
- fall_detector: Medical emergency & fall detection using skeleton tracking
- assault_detector: Biomechanical violence & multi-person interaction analysis
- crowd_analyzer: Crowd density, non-human filtering, and behavior analysis
- models: Deep learning model wrappers (YOLO, CNN, Mediapipe)
- utils: Utility functions for pose analysis and visualization
"""

from .shoplifting_detector import ShopliftingDetector
from .fall_detector import FallDetector
from .assault_detector import AssaultDetector
from .crowd_analyzer import CrowdAnalyzer

__version__ = "1.0.0"
__all__ = [
    "ShopliftingDetector",
    "FallDetector",
    "AssaultDetector",
    "CrowdAnalyzer",
]
