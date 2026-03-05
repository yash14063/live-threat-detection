"""
Visualization Utilities
=======================
Drawing functions for skeleton, detections, and alerts on video frames.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np


class SkeletonVisualizer:
    """Draw skeleton overlays on video frames."""

    # Standard skeleton connections (Mediapipe format)
    SKELETON_CONNECTIONS = [
        # Face
        (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
        # Body
        (9, 10), (11, 12), (11, 13), (13, 15),
        (12, 14), (14, 16), (11, 23), (12, 24),
        # Legs
        (23, 24), (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30),
        (29, 31), (30, 32),
    ]

    COLOR_SAFE = (16, 185, 129)      # Green
    COLOR_WARNING = (245, 158, 11)   # Yellow
    COLOR_DANGER = (239, 68, 68)     # Red
    COLOR_INFO = (6, 182, 212)       # Cyan

    @staticmethod
    def draw_skeleton(frame: np.ndarray, keypoints: List[Dict], 
                     color: Tuple[int, int, int] = (6, 182, 212), 
                     thickness: int = 2) -> np.ndarray:
        """
        Draw skeleton on frame.
        
        Args:
            frame: Video frame (BGR numpy array)
            keypoints: List of scored keypoints
            color: RGB tuple
            thickness: Line thickness
            
        Returns:
            Frame with skeleton drawn
        """
        try:
            import cv2
            
            frame_h, frame_w = frame.shape[:2]
            
            # Draw connections
            for start_idx, end_idx in SkeletonVisualizer.SKELETON_CONNECTIONS:
                if start_idx >= len(keypoints) or end_idx >= len(keypoints):
                    continue
                
                start = keypoints[start_idx]
                end = keypoints[end_idx]
                
                if start and end:
                    start_conf = start.get('confidence', 0)
                    end_conf = end.get('confidence', 0)
                    
                    if start_conf > 0.2 and end_conf > 0.2:
                        pt1 = (int(start.get('x', 0)), int(start.get('y', 0)))
                        pt2 = (int(end.get('x', 0)), int(end.get('y', 0)))
                        cv2.line(frame, pt1, pt2, color, thickness)
            
            # Draw keypoints
            for kp in keypoints:
                if kp and kp.get('confidence', 0) > 0.2:
                    x = int(kp.get('x', 0))
                    y = int(kp.get('y', 0))
                    cv2.circle(frame, (x, y), 3, color, -1)
            
            return frame
        except ImportError:
            print("⚠️  OpenCV not installed")
            return frame

    @staticmethod
    def draw_detection_box(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                          label: str, color: Tuple[int, int, int] = (6, 182, 212),
                          thickness: int = 2) -> np.ndarray:
        """
        Draw bounding box for detection.
        
        Args:
            frame: Video frame
            bbox: (x1, y1, x2, y2)
            label: Detection label
            color: RGB tuple
            thickness: Line thickness
            
        Returns:
            Frame with box drawn
        """
        try:
            import cv2
            
            x1, y1, x2, y2 = bbox
            
            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Draw label background
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 5),
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            return frame
        except ImportError:
            return frame

    @staticmethod
    def draw_alert_box(frame: np.ndarray, title: str, message: str,
                      threat_score: float = 75) -> np.ndarray:
        """
        Draw prominent alert box on frame.
        
        Args:
            frame: Video frame
            title: Alert title
            message: Alert message
            threat_score: Numerical threat score (0-100)
            
        Returns:
            Frame with alert box
        """
        try:
            import cv2
            
            frame_h, frame_w = frame.shape[:2]
            box_height = 80
            y_start = 20
            
            # Background
            cv2.rectangle(frame, (10, y_start), (frame_w - 10, y_start + box_height),
                         (239, 68, 68), -1)  # Red
            
            # Border
            cv2.rectangle(frame, (10, y_start), (frame_w - 10, y_start + box_height),
                         (0, 0, 255), 3)
            
            # Title
            cv2.putText(frame, title, (20, y_start + 25),
                       cv2.FONT_HERSHEY_BOLD, 0.8, (255, 255, 255), 2)
            
            # Message
            cv2.putText(frame, message, (20, y_start + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Threat score bar
            score_width = int((frame_w - 20) * (threat_score / 100.0))
            cv2.rectangle(frame, (10, y_start + box_height + 5),
                         (10 + score_width, y_start + box_height + 15),
                         (239, 68, 68), -1)
            
            cv2.putText(frame, f"Threat: {threat_score:.0f}/100", 
                       (frame_w - 180, y_start + box_height + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (239, 68, 68), 2)
            
            return frame
        except ImportError:
            return frame

    @staticmethod
    def draw_stats(frame: np.ndarray, stats: Dict, position: Tuple[int, int] = (10, 30)) -> np.ndarray:
        """Draw statistics overlay on frame."""
        try:
            import cv2
            
            x, y = position
            line_height = 25
            
            for key, value in stats.items():
                text = f"{key}: {value}"
                cv2.putText(frame, text, (x, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (6, 182, 212), 2)
                y += line_height
            
            return frame
        except ImportError:
            return frame
