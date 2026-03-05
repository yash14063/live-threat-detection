"""
Integration Example
===================
Example of how to integrate the AI detection system with the main ThreatSense application.

This shows the proper workflow for:
1. Loading models
2. Processing video frames
3. Running detectors
4. Sending alerts via WebSocket
5. Logging results
"""

import cv2
import json
from typing import Dict, List
from ai_detectors import (
    ShopliftingDetector, 
    FallDetector, 
    AssaultDetector, 
    CrowdAnalyzer
)
from ai_detectors.models import MediapipePoseDetector, YOLODetector
from ai_detectors.utils.visualization import SkeletonVisualizer


class ThreatSenseProcessor:
    """Main threat detection processor for video streams."""
    
    def __init__(self):
        """Initialize all detectors and models."""
        print("[*] Initializing ThreatSense AI Detection System...")
        
        # Load deep learning models
        print("[1] Loading Mediapipe pose detector...")
        self.pose_detector = MediapipePoseDetector(model_complexity=1)
        
        print("[2] Loading YOLO object detector...")
        self.yolo_detector = YOLODetector(model_name="yolov8m.pt")
        
        # Initialize threat detectors
        print("[3] Initializing threat detectors...")
        self.shoplifting_detector = ShopliftingDetector()
        self.fall_detector = FallDetector()
        self.assault_detector = AssaultDetector()
        self.crowd_analyzer = CrowdAnalyzer()
        
        self.detectors = [
            self.shoplifting_detector,
            self.fall_detector,
            self.assault_detector,
            self.crowd_analyzer,
        ]
        
        print("✓ System ready!\n")
    
    def process_frame(self, frame: Dict, websocket=None) -> Dict:
        """
        Process single video frame through all detectors.
        
        Args:
            frame: Video frame (numpy array)
            websocket: WebSocket connection for alerts (optional)
            
        Returns:
            Detection results from all detectors
        """
        results = {
            "frame_processed": True,
            "detections": [],
            "alerts": [],
            "frame_stats": {}
        }
        
        # === STEP 1: Run deep learning models ===
        print("\n[>>] Running Mediapipe pose detection...", end="")
        poses = self.pose_detector.detect(frame)
        print(f" → {len(poses)} poses detected")
        
        print("[>>] Running YOLO object detection...", end="")
        objects = self.yolo_detector.detect(frame)
        print(f" → {len(objects)} objects detected")
        
        # Count people from YOLO
        people_count = self.yolo_detector.get_people_count(objects)
        results["frame_stats"]["people_detected"] = people_count
        
        # === STEP 2: Run all threat detectors ===
        for detector in self.detectors:
            detector_result = detector.detect(frame, poses, objects)
            results["detections"].append(detector_result)
            
            # If alert triggered, add to alerts and send via WebSocket
            if detector_result.get("alert_triggered"):
                alert = {
                    "detector": detector.detector_name,
                    "threat_type": detector.threat_type,
                    "message": detector_result.get("threat_message"),
                    "threat_score": detector_result.get("threat_score"),
                    "pattern": detector_result.get("pattern"),
                }
                results["alerts"].append(alert)
                
                # Send to WebSocket backend
                if websocket:
                    try:
                        websocket.send_text(json.dumps({
                            "camera_id": "CAM_01",
                            **alert
                        }))
                        print(f"   [ALERT SENT] {detector.detector_name}: {alert['message']}")
                    except Exception as e:
                        print(f"   ⚠️  WebSocket send error: {e}")
        
        return results
    
    def process_video_stream(self, video_source: str = 0, websocket=None):
        """
        Process continuous video stream (camera or file).
        
        Args:
            video_source: 0 for webcam, or path to video file
            websocket: WebSocket connection for alerts
        """
        cap = cv2.VideoCapture(video_source)
        frame_count = 0
        
        if not cap.isOpened():
            print(f"❌ Failed to open video source: {video_source}")
            return
        
        print(f"\n[*] Starting video processing from source: {video_source}")
        print("[*] Press 'q' to exit\n")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process frame
            results = self.process_frame(frame, websocket)
            
            # === Optional: Draw visualizations ===
            if frame_count % 5 == 0:  # Every 5 frames to reduce overhead
                visualized_frame = self._draw_detections(frame, results)
                cv2.imshow("ThreatSense Detection", visualized_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n[*] Exiting...")
                break
            
            # Print summary every 30 frames
            if frame_count % 30 == 0:
                print(f"[{frame_count}] Processed {frame_count} frames, alerts: {len(results['alerts'])}")
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Print final statistics
        self._print_statistics()
    
    def _draw_detections(self, frame, results: Dict):
        """Draw detection overlays on frame."""
        # Draw alerts
        for alert in results["alerts"]:
            frame = SkeletonVisualizer.draw_alert_box(
                frame,
                title=alert["detector"],
                message=alert["message"],
                threat_score=alert["threat_score"]
            )
        
        # Draw stats
        stats = {
            "People": results["frame_stats"].get("people_detected", 0),
            "Alerts": len(results["alerts"]),
        }
        frame = SkeletonVisualizer.draw_stats(frame, stats)
        
        return frame
    
    def _print_statistics(self):
        """Print final statistics from all detectors."""
        print("\n" + "="*60)
        print("FINAL STATISTICS")
        print("="*60)
        
        for detector in self.detectors:
            stats = detector.get_detection_stats()
            print(f"\n{detector.detector_name}:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
    
    def get_system_status(self) -> Dict:
        """Get current system status and statistics."""
        return {
            "system": "ONLINE",
            "detectors": [d.detector_name for d in self.detectors],
            "statistics": {
                d.detector_name: d.get_detection_stats() 
                for d in self.detectors
            }
        }


# === EXAMPLE USAGE ===
if __name__ == "__main__":
    # Initialize processor
    processor = ThreatSenseProcessor()
    
    # Option 1: Process webcam stream
    print("\n[*] Processing webcam stream...")
    processor.process_video_stream(video_source=0)
    
    # Option 2: Process video file
    # processor.process_video_stream(video_source="test_video.mp4")
    
    # Option 3: Process single frame
    # import cv2
    # frame = cv2.imread("test_frame.jpg")
    # results = processor.process_frame(frame)
    # print(json.dumps(results, indent=2))
    
    # Option 4: Get system status
    # status = processor.get_system_status()
    # print(json.dumps(status, indent=2))
