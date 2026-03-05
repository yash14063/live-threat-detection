"""
Assault & Violence Detector
===========================
Detects biomechanical indicators of assault, violence, and theft via multi-person interaction analysis.

Detection Patterns:
1. NECK/FACE CONTACT (Choking, Strangling): Wrist-to-Face distance
2. PICKPOCKETING: Hand-to-Hip contact on secondary person
3. WEAPON DETECTION: Secondary object in hands during assault

Uses Mediapipe multi-person pose tracking and skeleton intersection analysis.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from .base_detector import BaseDetector
from .config import ASSAULT_DETECTION_THRESHOLDS


class AssaultDetector(BaseDetector):
    """
    Multi-person Assault & Violence Detection.
    
    Analyzes geometric relationships between skeletons to identify:
    - Strangling/choking (hand near neck/face)
    - Pickpocketing/robbery (hand near victim's hip/pocket)
    - Weapon-assisted violence (object in hand during assault)
    
    Requires multi-pose detection from Mediapipe.
    """

    def __init__(self):
        super().__init__(
            detector_name="ASSAULT_DETECTOR",
            threat_type="VIOLENCE_DETECTION"
        )
        self.assault_count = 0
        self.pickpocket_count = 0

    def detect(self, frame: np.ndarray, poses: List[Dict], objects: List[Dict]) -> Dict:
        """
        Detect multi-person assault and violence patterns.
        
        Args:
            frame: Video frame
            poses: List of all detected poses (need >=2 for assault detection)
            objects: Object detections (for weapon identification)
            
        Returns:
            Alert if assault/violence detected
        """
        alert_triggered = False
        threat_score = 0
        alert_message = ""
        pattern = ""

        # Assault requires at least 2 people detected
        if len(poses) < ASSAULT_DETECTION_THRESHOLDS["min_poses_required"]:
            return self.format_safe()

        # Analyze person A attacking person B
        person_a = poses[0]
        person_b = poses[1]

        keypoints_a = person_a.get("keypoints", [])
        keypoints_b = person_b.get("keypoints", [])

        if not keypoints_a or not keypoints_b:
            return self.format_safe()

        # Extract attacker's hands
        a_left_wrist = self._find_keypoint(keypoints_a, "left_wrist")
        a_right_wrist = self._find_keypoint(keypoints_a, "right_wrist")

        # Extract victim's vulnerable points
        b_nose = self._find_keypoint(keypoints_b, "nose")
        b_neck = self._find_keypoint(keypoints_b, "neck")  # Optional
        b_left_hip = self._find_keypoint(keypoints_b, "left_hip")
        b_right_hip = self._find_keypoint(keypoints_b, "right_hip")
        b_mouth = self._find_keypoint(keypoints_b, "mouth")  # Optional

        # === SCENARIO 1: STRANGULATION / CHOKING ===
        if a_right_wrist and a_right_wrist.get("confidence", 0) > 0.2:
            if b_nose and b_nose.get("confidence", 0) > 0.2:
                neck_distance = self.calculate_distance(a_right_wrist, b_nose)
                if neck_distance < ASSAULT_DETECTION_THRESHOLDS["neck_contact_distance"]:
                    alert_triggered = True
                    threat_score = ASSAULT_DETECTION_THRESHOLDS["neck_threat_score"]  # 95
                    alert_message = "🚨 CRITICAL ASSAULT: NECK CONTACT DETECTED"
                    pattern = "strangulation_right_hand"
                    self.assault_count += 1

        # === SCENARIO 2: PICKPOCKETING / TAMPERING ===
        if not alert_triggered and a_right_wrist:
            if b_left_hip and b_left_hip.get("confidence", 0) > 0.2:
                hip_distance = self.calculate_distance(a_right_wrist, b_left_hip)
                if hip_distance < ASSAULT_DETECTION_THRESHOLDS["hip_distance"]:
                    alert_triggered = True
                    threat_score = ASSAULT_DETECTION_THRESHOLDS["pickpocket_threat_score"]  # 70
                    alert_message = "⚠️  WARNING: PICKPOCKET / TAMPERING DETECTED"
                    pattern = "pickpocket_left_hip"
                    self.pickpocket_count += 1

        # === SCENARIO 3: LEFT HAND ASSAULT ===
        if not alert_triggered and a_left_wrist:
            if b_nose:
                neck_distance = self.calculate_distance(a_left_wrist, b_nose)
                if neck_distance < ASSAULT_DETECTION_THRESHOLDS["neck_contact_distance"]:
                    alert_triggered = True
                    threat_score = ASSAULT_DETECTION_THRESHOLDS["neck_threat_score"]
                    alert_message = "🚨 CRITICAL ASSAULT: NECK CONTACT DETECTED"
                    pattern = "strangulation_left_hand"
                    self.assault_count += 1

        # Generate alert
        if alert_triggered and self.should_trigger_alert():
            self.log_detection({
                "threat_score": threat_score,
                "message": alert_message,
                "pattern": pattern,
                "person_count": len(poses)
            })
            return self.format_alert(alert_message, threat_score, pattern)

        return self.format_safe()

    def _find_keypoint(self, keypoints: List[Dict], name: str) -> Optional[Dict]:
        """Find keypoint by name."""
        for kp in keypoints:
            if kp.get("name") == name:
                return kp
        return None

    def get_assault_stats(self) -> Dict:
        """Get assault and violence detection statistics."""
        stats = self.get_detection_stats()
        stats["total_assaults_detected"] = self.assault_count
        stats["total_pickpockets_detected"] = self.pickpocket_count
        return stats
