"""
YOLO Object Detector Wrapper
============================
High-level interface for Ultralytics YOLOv8 object detection.
Detects people, weapons, contraband, vehicles, and more.

Models:
- YOLOv8n (nano): Fastest, mobile
- YOLOv8s (small): Balanced
- YOLOv8m (medium): Accurate, recommended
- YOLOv8l (large): Maximum accuracy
- YOLOv8x (extra): Highest precision for critical systems
"""

from typing import Dict, List, Optional
import numpy as np
from ..config import YOLO_CONFIG


class YOLODetector:
    """
    Wrapper for Ultralytics YOLOv8 object detection.
    
    Detects and classifies objects in real-time:
    - People (for crowd counting)
    - Weapons & contraband (for threat detection)
    - Vehicles (for parking, traffic)
    - Animals (for non-human filtering)
    - Luggage & bags (contextual analysis)
    """

    def __init__(self, model_name: str = "yolov8m.pt"):
        """
        Initialize YOLO detector.
        
        Args:
            model_name: Model variant (n/s/m/l/x)
        """
        self.model_name = model_name
        self.model = None
        self.confidence_threshold = YOLO_CONFIG["confidence_threshold"]
        self.iou_threshold = YOLO_CONFIG["iou_threshold"]
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize YOLO model from Ultralytics."""
        try:
            from ultralytics import YOLO
            
            self.model = YOLO(self.model_name)
            print(f"✓ YOLO ({self.model_name}) loaded successfully")
        except ImportError:
            print("⚠️  Ultralytics YOLO not installed. Install with: pip install ultralytics")
            self.model = None

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in frame using YOLO.
        
        Args:
            frame: BGR image (numpy array)
            
        Returns:
            List of detections:
            [
                {
                    "class": str (class name),
                    "class_id": int,
                    "confidence": float (0-1),
                    "bbox": (x1, y1, x2, y2),
                    "area": float (pixels²)
                },
                ...
            ]
        """
        if self.model is None:
            return []

        try:
            # Run YOLO inference
            results = self.model.predict(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                device=YOLO_CONFIG["device"],
                verbose=False
            )

            detections = []
            for result in results:
                if result.boxes is None:
                    continue

                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]

                    # Calculate bounding box area
                    area = (x2 - x1) * (y2 - y1)

                    detections.append({
                        "class": class_name,
                        "class_id": class_id,
                        "confidence": confidence,
                        "bbox": (int(x1), int(y1), int(x2), int(y2)),
                        "area": area,
                        "center_x": int((x1 + x2) / 2),
                        "center_y": int((y1 + y2) / 2)
                    })

            return detections
        except Exception as e:
            print(f"❌ YOLO detection error: {e}")
            return []

    def get_people_count(self, detections: List[Dict]) -> int:
        """Count number of detected people."""
        return sum(1 for det in detections if det["class"].lower() == "person")

    def get_weapons_detected(self, detections: List[Dict]) -> List[Dict]:
        """Get all weapon/threat detections."""
        weapon_classes = ["knife", "gun", "rifle", "handgun", "sword", "axe"]
        return [det for det in detections if det["class"].lower() in weapon_classes]

    def get_by_class(self, detections: List[Dict], class_name: str) -> List[Dict]:
        """Filter detections by class name."""
        return [det for det in detections if det["class"].lower() == class_name.lower()]
