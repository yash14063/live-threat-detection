"""
Shoplifting Detector (Walmart Retail Theft Detection)
=====================================================
Detects retail theft by analyzing hand-to-hip movement patterns.
Distinguishes between legitimate shopping (items to cart) and theft (items to pocket).

Detection Pattern:
- Rack level → Pocket concealment (THREAT)
- Rack level → Shopping cart (SAFE)
"""

from typing import Dict, List, Optional
import numpy as np
from .base_detector import BaseDetector
from .config import SHOPLIFTING_THRESHOLDS, MOVEMENT_HISTORY


class ShopliftingDetector(BaseDetector):
    """
    Walmart Shoplifting Detection using Mediapipe Pose Estimation.
    
    Analyzes hand movement trajectories to identify suspicious patterns:
    - Items placed into pocket/body = THEFT (threat_score: 75)
    - Items placed into cart = LEGITIMATE (safe)
    """

    def __init__(self):
        super().__init__(
            detector_name="WALMART_THEFT_DETECTOR",
            threat_type="RETAIL_SHOPLIFTING"
        )
        self.hand_movement_history = {"left": [], "right": []}
        self.max_history = MOVEMENT_HISTORY["max_history"]
        self.concealment_count = 0

    def detect(self, frame: np.ndarray, poses: List[Dict], objects: List[Dict]) -> Dict:
        """
        Detect shoplifting patterns in retail environments.
        
        Args:
            frame: Video frame for analysis
            poses: List of pose detections [{"keypoints": [...], "bbox": ...}, ...]
            objects: List of object detections (unused for this detector)
            
        Returns:
            Detection result with alert status and threat score
        """
        alert_triggered = False
        alert_message = ""
        threat_score = 0
        pattern = ""

        for pose in poses:
            keypoints = pose.get("keypoints", [])
            if not keypoints:
                continue

            # Extract key joints
            left_wrist = self._find_keypoint(keypoints, "left_wrist")
            right_wrist = self._find_keypoint(keypoints, "right_wrist")
            left_shoulder = self._find_keypoint(keypoints, "left_shoulder")
            right_shoulder = self._find_keypoint(keypoints, "right_shoulder")
            left_hip = self._find_keypoint(keypoints, "left_hip")
            right_hip = self._find_keypoint(keypoints, "right_hip")

            if not (left_hip and right_hip and left_shoulder and right_shoulder):
                continue

            # Calculate reference points
            shoulder_y = (left_shoulder["y"] + right_shoulder["y"]) / 2
            hip_y = (left_hip["y"] + right_hip["y"]) / 2
            cart_level_y = hip_y + 30  # Below hips where carts are

            # Analyze LEFT HAND
            if left_wrist and left_wrist.get("confidence", 0) > 0.3:
                self._track_hand_movement(left_wrist, "left")
                hip_distance = min(
                    self.calculate_distance(left_wrist, left_hip),
                    self.calculate_distance(left_wrist, right_hip)
                )

                # Check for pocket concealment pattern
                if hip_distance < SHOPLIFTING_THRESHOLDS["min_hand_distance_to_hip"]:
                    if self._check_rack_to_pocket_pattern("left", shoulder_y):
                        alert_triggered = True
                        threat_score = SHOPLIFTING_THRESHOLDS["threat_score"]
                        alert_message = "🛒 WALMART ALERT: POCKET CONCEALMENT DETECTED"
                        pattern = "rack_to_pocket_left"
                        self.concealment_count += 1

                # Check for legitimate cart placement
                elif abs(left_wrist["y"] - cart_level_y) < 50:
                    pattern = "cart_placement_left"

            # Analyze RIGHT HAND
            if right_wrist and right_wrist.get("confidence", 0) > 0.3:
                self._track_hand_movement(right_wrist, "right")
                hip_distance = min(
                    self.calculate_distance(right_wrist, left_hip),
                    self.calculate_distance(right_wrist, right_hip)
                )

                if hip_distance < SHOPLIFTING_THRESHOLDS["min_hand_distance_to_hip"]:
                    if self._check_rack_to_pocket_pattern("right", shoulder_y):
                        alert_triggered = True
                        threat_score = SHOPLIFTING_THRESHOLDS["threat_score"]
                        alert_message = "🛒 WALMART ALERT: POCKET CONCEALMENT DETECTED"
                        pattern = "rack_to_pocket_right"
                        self.concealment_count += 1

                elif abs(right_wrist["y"] - cart_level_y) < 50:
                    pattern = "cart_placement_right"

        # Return formatted result
        if alert_triggered and self.should_trigger_alert():
            self.log_detection({
                "threat_score": threat_score,
                "message": alert_message,
                "pattern": pattern
            })
            return self.format_alert(alert_message, threat_score, pattern)
        
        return self.format_safe()

    def _find_keypoint(self, keypoints: List[Dict], name: str) -> Optional[Dict]:
        """Find a specific keypoint by name."""
        for kp in keypoints:
            if kp.get("name") == name:
                return kp
        return None

    def _track_hand_movement(self, hand_point: Dict, hand_side: str) -> None:
        """Track hand movement history for pattern analysis."""
        history = self.hand_movement_history[hand_side]
        history.append({
            "x": hand_point.get("x"),
            "y": hand_point.get("y"),
            "confidence": hand_point.get("confidence")
        })
        # Maintain max history size
        if len(history) > self.max_history:
            history.pop(0)

    def _check_rack_to_pocket_pattern(self, hand_side: str, shoulder_y: float) -> bool:
        """
        Check if hand movement matches rack-to-pocket theft pattern.
        
        Pattern characteristics:
        - Movement originates from rack level (above shoulder)
        - Moves downward toward hip/pocket area
        - Sustained proximity to pocket
        """
        history = self.hand_movement_history[hand_side]
        
        # Need minimum history to detect pattern
        if len(history) < SHOPLIFTING_THRESHOLDS["min_movement_history"]:
            return False

        # Get recent movement trajectory
        recent = history[-SHOPLIFTING_THRESHOLDS["min_movement_history"]:]
        start_y = recent[0]["y"]
        end_y = recent[-1]["y"]
        
        # Check for downward motion
        downward_motion = end_y > start_y + SHOPLIFTING_THRESHOLDS["min_vertical_distance"]
        
        # Check if started from rack level
        came_from_rack = start_y < shoulder_y + SHOPLIFTING_THRESHOLDS["shoulder_height_buffer"]
        
        return downward_motion and came_from_rack

    def get_concealment_stats(self) -> Dict:
        """Get shoplifting detection statistics."""
        stats = self.get_detection_stats()
        stats["total_concealments_detected"] = self.concealment_count
        return stats
