"""
Configuration for ThreatSense AI Detection System
==================================================
Centralized settings for all detectors and models.
"""

# === MODEL CONFIGURATION ===
MEDIAPIPE_CONFIG = {
    "static_image_mode": False,
    "model_complexity": 1,
    "smooth_landmarks": True,
    "enable_segmentation": False,
    "smooth_segmentation": True,
    "min_detection_confidence": 0.5,
    "min_tracking_confidence": 0.5,
}

YOLO_CONFIG = {
    "model_name": "yolov8m.pt",  # Medium YOLOv8 model
    "confidence_threshold": 0.45,
    "iou_threshold": 0.5,
    "imgsz": 640,
    "device": "cuda" if __import__("torch").cuda.is_available() else "cpu",
}

CNN_CONFIG = {
    "model_architecture": "resnet50",
    "num_classes": 2,  # Binary: threat/no-threat
    "pretrained": True,
    "input_size": (224, 224),
}

# === DETECTION THRESHOLDS ===
SHOPLIFTING_THRESHOLDS = {
    "min_hand_distance_to_hip": 40,  # pixels
    "min_movement_history": 5,  # frames
    "min_vertical_distance": 10,  # pixels (downward motion)
    "shoulder_height_buffer": -20,  # offset from shoulder
    "threat_score": 75,  # when detected
    "cooldown_ms": 3000,  # prevent duplicate detections
}

FALL_DETECTION_THRESHOLDS = {
    "aspect_ratio_threshold": 0.8,  # width/height ratio for lying down
    "confidence_threshold": 0.3,  # keypoint confidence
    "threat_score": 95,  # critical for falls
}

ASSAULT_DETECTION_THRESHOLDS = {
    "neck_contact_distance": 50,  # pixels (hand to face)
    "hip_distance": 45,  # pixels (pickpocket detection)
    "min_poses_required": 2,  # multi-person interaction
    "neck_threat_score": 95,  # critical
    "pickpocket_threat_score": 70,  # high
}

CROWD_ANALYSIS_THRESHOLDS = {
    "crowd_density_levels": {
        "low": (0, 10),
        "medium": (10, 25),
        "high": (25, 50),
        "critical": (50, float("inf")),
    },
    "threat_scores": {
        "low": 0,
        "medium": 20,
        "high": 40,
        "critical": 60,
    },
    "non_human_classes": ["dog", "cat", "cell phone", "book", "bicycle", "car"],
    "filtered_confidence": 0.3,
}

# === MOVEMENT TRACKING ===
MOVEMENT_HISTORY = {
    "max_history": 15,  # frames (~0.5 seconds at 30fps)
    "fps": 30,
}

# === DATABASE ===
DATABASE_CONFIG = {
    "db_name": "threatsense.db",
    "alerts_table": "security_alerts",
}

# === LOGGING ===
LOGGING_CONFIG = {
    "alert_cooldown": 850,  # milliseconds between log entries
    "log_levels": {
        "critical": "CRITICAL",
        "high": "HIGH",
        "moderate": "MODERATE",
        "low": "LOW",
    },
}

# === VISUALIZATION ===
VISUALIZATION_CONFIG = {
    "canvas_colors": {
        "safe": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#06b6d4",
    },
    "text_font": "Rajdhani",
    "skeleton_point_radius": 5,
    "skeleton_line_width": 2,
    "bounding_box_width": 3,
}

# === CAMERA PARAMETERS ===
CAMERA_CONFIG = {
    "resolution": (800, 600),
    "fps": 30,
    "auto_flip": True,  # mirror for selfie cameras
}

# === ALERT TYPES ===
ALERT_TYPES = {
    "WALMART_SHOPLIFTING": "Retail theft - pocket concealment pattern",
    "FALL_EMERGENCY": "Medical emergency - fall detected",
    "ASSAULT_NECK": "Critical assault - neck/face contact",
    "PICKPOCKET": "Theft - pickpocketing/tampering",
    "GEOFENCE_BREACH": "Intrusion - geofence boundary crossed",
    "WEAPON_DETECTED": "Threat - weapon/contraband identified",
    "FIRE_SMOKE": "Emergency - fire or smoke detected",
}

# === THREAT LEVELS ===
THREAT_LEVELS = {
    "CRITICAL": (90, 100),
    "HIGH": (70, 90),
    "MODERATE": (40, 70),
    "LOW": (0, 40),
}
