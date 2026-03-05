"""
Fall Detection / Medical Emergency Detector
===========================================
Detects falls and medical emergencies using skeleton aspect ratio analysis.
Uses Mediapipe pose estimation to track body orientation.

Detection Method:
- Analyzes shoulder-to-hip ratio (width/height)
- High ratio (>0.8) indicates person lying down/fallen
- Threat score: 95 (CRITICAL - requires emergency response)
"""

from typing import Dict, List, Optional
import numpy as np
from .base_detector import BaseDetector
from .config import FALL_DETECTION_THRESHOLDS


class FallDetector(BaseDetector):
    """
    Medical Emergency & Fall Detection using skeleton aspect ratio.
    
    Uses simple but effective computer vision technique:
    - When person falls, body becomes wide and short
    - Calculate aspect ratio = shoulder_width / body_height
    - Ratio > 0.8 indicates prone/fallen position
    
    Critical for elderly care, retail safety, public facilities
    """

    def __init__(self):
        super().__init__(
            detector_name="FALL_DETECTOR",
            threat_type="MEDICAL_EMERGENCY"
        )
        self.fall_alert_count = 0
        self.consecutive_frames_fallen = 0
        self.require_consecutive_frames = 3  # Reduce false positives

    def detect(self, frame: np.ndarray, poses: List[Dict], objects: List[Dict]) -> Dict:
        """
        Detect falls and medical emergencies.
        
        Args:
            frame: Video frame for analysis
            poses: List of pose detections from Mediapipe
            objects: Object detections (unused)
            
        Returns:
            Alert with threat score 95 if fall detected, 0 if safe
        """
        alert_triggered = False
        threat_score = 0
        pattern = ""

        for pose in poses:
            keypoints = pose.get("keypoints", [])
            if not keypoints:
                continue

            # Extract shoulder and hip keypoints
            left_shoulder = self._find_keypoint(keypoints, "left_shoulder")
            right_shoulder = self._find_keypoint(keypoints, "right_shoulder")
            left_hip = self._find_keypoint(keypoints, "left_hip")
            right_hip = self._find_keypoint(keypoints, "right_hip")

            # Validate keypoint confidence
            if not self._validate_keypoints([left_shoulder, right_shoulder, left_hip, right_hip]):
                self.consecutive_frames_fallen = 0
                continue

            # Calculate body dimensions
            shoulder_width = abs(left_shoulder["x"] - right_shoulder["x"])
            shoulder_y = (left_shoulder["y"] + right_shoulder["y"]) / 2
            hip_y = (left_hip["y"] + right_hip["y"]) / 2
            body_height = abs(shoulder_y - hip_y)

            if body_height <= 0:
                continue

            # Calculate aspect ratio
            aspect_ratio = shoulder_width / body_height

            # FALL DETECTION LOGIC
            if aspect_ratio > FALL_DETECTION_THRESHOLDS["aspect_ratio_threshold"]:
                # Person appears to be lying down/fallen
                self.consecutive_frames_fallen += 1
                
                if self.consecutive_frames_fallen >= self.require_consecutive_frames:
                    alert_triggered = True
                    threat_score = FALL_DETECTION_THRESHOLDS["threat_score"]  # 95 - CRITICAL
                    pattern = f"fallen_aspect_ratio_{aspect_ratio:.2f}"
            else:
                # Person is upright
                self.consecutive_frames_fallen = 0

        # Generate alert
        if alert_triggered and self.should_trigger_alert():
            self.fall_alert_count += 1
            alert_message = f"🚨 MEDICAL EMERGENCY: FALL DETECTED (Aspect Ratio: {aspect_ratio:.2f})"
            self.log_detection({
                "threat_score": threat_score,
                "message": alert_message,
                "pattern": pattern,
                "aspect_ratio": aspect_ratio
            })
            return self.format_alert(alert_message, threat_score, pattern)

        self.consecutive_frames_fallen = 0
        return self.format_safe()

    def _find_keypoint(self, keypoints: List[Dict], name: str) -> Optional[Dict]:
        """Find keypoint by name."""
        for kp in keypoints:
            if kp.get("name") == name:
                return kp
        return None

    def _validate_keypoints(self, keypoints: List[Optional[Dict]]) -> bool:
        """Check if all required keypoints are detected with sufficient confidence."""
        threshold = FALL_DETECTION_THRESHOLDS["confidence_threshold"]
        return all(
            kp and kp.get("confidence", 0) > threshold
            for kp in keypoints
        )

    def get_fall_stats(self) -> Dict:
        """Get fall detection statistics."""
        stats = self.get_detection_stats()
        stats["total_falls_detected"] = self.fall_alert_count
        stats["currently_tracking_fall"] = self.consecutive_frames_fallen > 0
        stats["frames_fallen"] = self.consecutive_frames_fallen
        return stats
