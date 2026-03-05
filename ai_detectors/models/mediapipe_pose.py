"""
Mediapipe Pose Estimation Wrapper
==================================
High-level interface for Mediapipe pose detection.
Handles multi-person skeleton tracking with confidence filtering.

Models:
- LITE: Fast, mobile-optimized
- FULL: Accurate, desktop-class
- HEAVY: Maximum precision for critical applications
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from ..config import MEDIAPIPE_CONFIG


class MediapipePoseDetector:
    """
    Wrapper for Google Mediapipe Pose Detection.
    
    Detects human body pose with 33 landmarks:
    - Head & face (5 points)
    - Torso (3 points)
    - Arms (8 points)
    - Hands (10 points)
    - Legs (8 points)
    
    Supports multi-person tracking with confidence scores.
    """

    def __init__(self, model_complexity: int = 1, enable_tracking: bool = True):
        """
        Initialize Mediapipe pose detector.
        
        Args:
            model_complexity: 0=lite, 1=full, 2=heavy
            enable_tracking: Use tracking for smoother results
        """
        self.model_complexity = model_complexity
        self.enable_tracking = enable_tracking
        self.detector = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize Mediapipe pose model."""
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            base_options = python.BaseOptions(model_asset_path=None)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.LIVE_STREAM,
                num_poses=10,  # Support up to 10 simultaneous people
                min_pose_detection_confidence=MEDIAPIPE_CONFIG["min_detection_confidence"],
                min_pose_presence_confidence=MEDIAPIPE_CONFIG["min_tracking_confidence"]
            )
            self.detector = vision.PoseLandmarker.create_from_options(options)
            print("✓ Mediapipe Pose Detector initialized successfully")
        except ImportError:
            print("⚠️  Mediapipe not installed. Install with: pip install mediapipe")
            self.detector = None

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect poses in frame.
        
        Args:
            frame: BGR/RGB image (numpy array)
            
        Returns:
            List of detected poses, each with:
            {
                "keypoints": [{"name": str, "x": float, "y": float, "z": float, "confidence": float}, ...],
                "bbox": (x1, y1, x2, y2),
                "confidence": float
            }
        """
        if self.detector is None:
            return []

        try:
            import mediapipe as mp
            
            # Convert frame to RGB if needed
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # Assume BGR format from OpenCV
                rgb_frame = frame[:, :, ::-1]
            else:
                rgb_frame = frame

            # Run detection
            results = self.detector.detect_for_video(rgb_frame, timestamp_ms=0)
            
            # Format output
            poses = []
            for pose_landmarks in results.pose_landmarks:
                keypoints = []
                for landmark in pose_landmarks:
                    keypoints.append({
                        "name": self._get_landmark_name(len(keypoints)),
                        "x": landmark.x * frame.shape[1],  # Scale to image coordinates
                        "y": landmark.y * frame.shape[0],
                        "z": landmark.z,
                        "confidence": landmark.visibility
                    })
                
                # Calculate bounding box
                xs = [kp["x"] for kp in keypoints]
                ys = [kp["y"] for kp in keypoints]
                bbox = (min(xs), min(ys), max(xs), max(ys))
                
                poses.append({
                    "keypoints": keypoints,
                    "bbox": bbox,
                    "confidence": sum(kp["confidence"] for kp in keypoints) / len(keypoints)
                })
            
            return poses
        except Exception as e:
            print(f"❌ Pose detection error: {e}")
            return []

    @staticmethod
    def _get_landmark_name(index: int) -> str:
        """Get landmark name by index."""
        landmark_names = [
            "nose", "left_eye_inner", "left_eye", "left_eye_outer",
            "right_eye_inner", "right_eye", "right_eye_outer",
            "left_ear", "right_ear", "mouth_left", "mouth_right",
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_pinky", "right_pinky",
            "left_index", "right_index", "left_thumb", "right_thumb",
            "left_hip", "right_hip", "left_knee", "right_knee",
            "left_ankle", "right_ankle", "left_heel", "right_heel",
            "left_foot_index", "right_foot_index"
        ]
        return landmark_names[index] if index < len(landmark_names) else f"unknown_{index}"
