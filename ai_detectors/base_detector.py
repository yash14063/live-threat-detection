"""
Base Detector Class
===================
Abstract base class for all threat detection models.
Provides common interface and shared functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from datetime import datetime


class BaseDetector(ABC):
    """
    Abstract base class for all AI threat detectors.
    
    All specific detectors (Shoplifting, Fall, Assault, etc.) inherit from this class
    and implement the `detect()` method with their specific logic.
    """

    def __init__(self, detector_name: str, threat_type: str):
        """
        Initialize base detector.
        
        Args:
            detector_name: Name identifier for the detector
            threat_type: Type of threat being detected
        """
        self.detector_name = detector_name
        self.threat_type = threat_type
        self.last_alert_time = 0
        self.alert_cooldown_ms = 850
        self.detection_history = []

    @abstractmethod
    def detect(self, frame: np.ndarray, poses: List[Dict], objects: List[Dict]) -> Dict:
        """
        Main detection method - must be implemented by subclasses.
        
        Args:
            frame: Input video frame (numpy array)
            poses: List of pose detections from mediapipe/yolo
            objects: List of object detections from YOLO
            
        Returns:
            Dict with keys:
                - alert_triggered (bool): Whether threat detected
                - threat_message (str): Alert message
                - threat_score (float): 0-100 confidence
                - pattern (str): Detection pattern description
        """
        pass

    def calculate_distance(self, point1: Dict, point2: Dict) -> float:
        """Calculate Euclidean distance between two keypoints."""
        if not (point1 and point2):
            return float('inf')
        dx = point1.get('x', 0) - point2.get('x', 0)
        dy = point1.get('y', 0) - point2.get('y', 0)
        return (dx**2 + dy**2) ** 0.5

    def should_trigger_alert(self, force: bool = False) -> bool:
        """Check if enough time has passed since last alert (cooldown)."""
        now = datetime.now().timestamp() * 1000
        if force or (now - self.last_alert_time) > self.alert_cooldown_ms:
            self.last_alert_time = now
            return True
        return False

    def log_detection(self, alert_data: Dict) -> None:
        """Store detection in history for analysis."""
        self.detection_history.append({
            "timestamp": datetime.now().isoformat(),
            **alert_data
        })
        # Keep only last 100 detections in memory
        if len(self.detection_history) > 100:
            self.detection_history.pop(0)

    def get_detection_stats(self) -> Dict:
        """Get statistics about recent detections."""
        if not self.detection_history:
            return {"total": 0, "critical": 0, "high": 0}
        
        total = len(self.detection_history)
        critical = sum(1 for d in self.detection_history if d.get("threat_score", 0) >= 90)
        high = sum(1 for d in self.detection_history if d.get("threat_score", 0) >= 70)
        
        return {
            "total": total,
            "critical": critical,
            "high": high,
            "recent_average_score": np.mean([d.get("threat_score", 0) for d in self.detection_history[-10:]])
        }

    def format_alert(self, message: str, threat_score: float, pattern: Optional[str] = None) -> Dict:
        """Format alert data for WebSocket transmission."""
        return {
            "alert_triggered": True,
            "threat_message": message,
            "threat_score": threat_score,
            "pattern": pattern,
            "detector": self.detector_name,
            "threat_type": self.threat_type,
            "timestamp": datetime.now().isoformat()
        }

    def format_safe(self) -> Dict:
        """Format safe/no-threat response."""
        return {
            "alert_triggered": False,
            "threat_message": f"{self.detector_name}: CLEAR",
            "threat_score": 0,
            "pattern": None,
            "detector": self.detector_name,
            "timestamp": datetime.now().isoformat()
        }
