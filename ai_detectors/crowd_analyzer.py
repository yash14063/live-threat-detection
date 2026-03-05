"""
Crowd Analyzer
==============
Real-time crowd density counting, non-human filtering, and crowd behavior analysis.
Uses YOLO object detection + Mediapipe for comprehensive crowd intelligence.

Features:
- Real-time person counting via CNN
- Non-human object filtering (pets, shadows, inanimate objects)
- Crowd density classification (low/medium/high/critical)
- Anomaly detection based on crowd composition
"""

from typing import Dict, List, Optional
import numpy as np
from .base_detector import BaseDetector
from .config import CROWD_ANALYSIS_THRESHOLDS


class CrowdAnalyzer(BaseDetector):
    """
    Crowd Density Analysis and Behavior Monitoring.
    
    Uses CNN-based object detection (YOLO) to:
    - Count real people vs filtering non-humans
    - Classify crowd density levels
    - Generate threat scores based on density and composition
    - Track crowd-related anomalies
    """

    def __init__(self):
        super().__init__(
            detector_name="CROWD_ANALYZER",
            threat_type="CROWD_ANALYSIS"
        )
        self.person_count = 0
        self.filtered_objects = []
        self.current_density_level = "low"
        self.max_density_recorded = 0

    def detect(self, frame: np.ndarray, poses: List[Dict], objects: List[Dict]) -> Dict:
        """
        Analyze crowd composition and generate threat assessment.
        
        Args:
            frame: Video frame
            poses: Pose detections (alternative count method)
            objects: YOLO object detections with classes and confidence
            
        Returns:
            Crowd analysis with density level and threat score
        """
        threat_score = 0
        alert_triggered = False
        pattern = ""

        # Count humans and filter non-humans
        person_count = 0
        filtered_count = 0

        for obj in objects:
            class_name = obj.get("class", "").lower()
            confidence = obj.get("confidence", 0)

            if class_name == "person" and confidence > 0.45:
                person_count += 1
            elif class_name in CROWD_ANALYSIS_THRESHOLDS["non_human_classes"]:
                if confidence > CROWD_ANALYSIS_THRESHOLDS["filtered_confidence"]:
                    filtered_count += 1
                    self.filtered_objects.append(class_name)

        self.person_count = person_count
        old_density = self.current_density_level

        # Classify crowd density
        density_levels = CROWD_ANALYSIS_THRESHOLDS["crowd_density_levels"]
        threat_scores = CROWD_ANALYSIS_THRESHOLDS["threat_scores"]

        for level, (min_count, max_count) in density_levels.items():
            if min_count <= person_count < max_count:
                self.current_density_level = level
                threat_score = threat_scores[level]
                pattern = f"crowd_density_{level}_{person_count}_people"
                break

        # Update max recorded
        if person_count > self.max_density_recorded:
            self.max_density_recorded = person_count

        # Alert if density increased significantly
        if (old_density == "low" and self.current_density_level in ["high", "critical"]) or \
           (old_density in ["low", "medium"] and self.current_density_level == "critical"):
            alert_triggered = True
            alert_message = f"⚠️  CROWD ALERT: Density escalated to {self.current_density_level.upper()} ({person_count} people)"
        else:
            alert_message = f"Crowd Status: {self.current_density_level} ({person_count} people)"

        if alert_triggered and self.should_trigger_alert():
            self.log_detection({
                "threat_score": threat_score,
                "message": alert_message,
                "pattern": pattern,
                "person_count": person_count,
                "density_level": self.current_density_level,
                "filtered_objects": filtered_count
            })
            return self.format_alert(alert_message, threat_score, pattern)

        # Return safe but with crowd info
        return {
            "alert_triggered": False,
            "threat_score": threat_score,
            "threat_message": alert_message,
            "pattern": pattern,
            "detector": self.detector_name,
            "person_count": person_count,
            "density_level": self.current_density_level,
            "non_human_filtered": filtered_count,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }

    def get_crowd_stats(self) -> Dict:
        """Get detailed crowd analysis statistics."""
        stats = self.get_detection_stats()
        stats.update({
            "current_person_count": self.person_count,
            "current_density_level": self.current_density_level,
            "max_density_recorded": self.max_density_recorded,
            "filtered_non_human_objects": len(set(self.filtered_objects)),
            "non_human_distribution": self._get_object_distribution()
        })
        return stats

    def _get_object_distribution(self) -> Dict[str, int]:
        """Get distribution of filtered non-human objects."""
        distribution = {}
        for obj in self.filtered_objects:
            distribution[obj] = distribution.get(obj, 0) + 1
        return distribution
