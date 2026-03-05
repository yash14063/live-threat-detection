"""
Pose Analysis Utilities
=======================
Mathematical and geometric operations on skeleton data.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np


def calculate_distance(point1: Dict, point2: Dict) -> float:
    """
    Calculate Euclidean distance between two keypoints.
    
    Args:
        point1: {"x": float, "y": float, "z": float}
        point2: {"x": float, "y": float, "z": float}
        
    Returns:
        Distance in pixels (2D) or normalized space (3D)
    """
    if not point1 or not point2:
        return float('inf')
    
    dx = point1.get('x', 0) - point2.get('x', 0)
    dy = point1.get('y', 0) - point2.get('y', 0)
    dz = point1.get('z', 0) - point2.get('z', 0)
    
    return (dx**2 + dy**2 + dz**2) ** 0.5


def calculate_angle(point1: Dict, vertex: Dict, point2: Dict) -> float:
    """
    Calculate angle at vertex formed by three points.
    Useful for joint angle analysis (elbow bend, knee bend, etc.)
    
    Args:
        point1: Start point
        vertex: Angle vertex
        point2: End point
        
    Returns:
        Angle in degrees (0-180)
    """
    v1 = np.array([
        point1.get('x', 0) - vertex.get('x', 0),
        point1.get('y', 0) - vertex.get('y', 0)
    ])
    v2 = np.array([
        point2.get('x', 0) - vertex.get('x', 0),
        point2.get('y', 0) - vertex.get('y', 0)
    ])
    
    # Avoid division by zero
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0
    
    cos_angle = np.dot(v1, v2) / (norm_v1 * norm_v2)
    cos_angle = np.clip(cos_angle, -1, 1)  # Handle numerical errors
    angle_rad = np.arccos(cos_angle)
    
    return np.degrees(angle_rad)


def get_skeleton_aspect_ratio(left_shoulder: Dict, right_shoulder: Dict, 
                               left_hip: Dict, right_hip: Dict) -> float:
    """
    Calculate body aspect ratio (width/height).
    Used for fall detection.
    
    High ratio (>0.8) indicates prone/lying down position.
    """
    shoulder_width = abs(left_shoulder.get('x', 0) - right_shoulder.get('x', 0))
    shoulder_y = (left_shoulder.get('y', 0) + right_shoulder.get('y', 0)) / 2
    hip_y = (left_hip.get('y', 0) + right_hip.get('y', 0)) / 2
    body_height = abs(shoulder_y - hip_y)
    
    if body_height <= 0:
        return 0
    
    return shoulder_width / body_height


def get_body_center(keypoints: List[Dict]) -> Tuple[float, float]:
    """Calculate center of mass of skeleton."""
    if not keypoints:
        return (0, 0)
    
    xs = [kp.get('x', 0) for kp in keypoints]
    ys = [kp.get('y', 0) for kp in keypoints]
    
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def is_hand_raised(hand_point: Dict, shoulder_point: Dict, hip_point: Dict) -> bool:
    """Check if hand is raised above shoulder (attack/surrender pose)."""
    hand_y = hand_point.get('y', float('inf'))
    shoulder_y = shoulder_point.get('y', 0)
    
    return hand_y < shoulder_y


def get_hand_to_hip_distance(hand: Dict, left_hip: Dict, right_hip: Dict) -> float:
    """Get minimum distance from hand to either hip."""
    dist_left = calculate_distance(hand, left_hip)
    dist_right = calculate_distance(hand, right_hip)
    return min(dist_left, dist_right)


def smooth_trajectory(trajectory: List[Dict], window_size: int = 3) -> List[Dict]:
    """
    Smooth jerky pose trajectories using moving average.
    Reduces noise from detection jitter.
    
    Args:
        trajectory: List of keypoint positions over time
        window_size: Moving average window (odd number preferred)
        
    Returns:
        Smoothed trajectory
    """
    if len(trajectory) < window_size:
        return trajectory
    
    half_window = window_size // 2
    smoothed = []
    
    for i in range(len(trajectory)):
        start_idx = max(0, i - half_window)
        end_idx = min(len(trajectory), i + half_window + 1)
        
        window = trajectory[start_idx:end_idx]
        avg_x = np.mean([p.get('x', 0) for p in window])
        avg_y = np.mean([p.get('y', 0) for p in window])
        avg_conf = np.mean([p.get('confidence', 0) for p in window])
        
        smoothed.append({
            'x': avg_x,
            'y': avg_y,
            'confidence': avg_conf
        })
    
    return smoothed
