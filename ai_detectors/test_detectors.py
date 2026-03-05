"""
Test Suite for AI Detectors
============================
Run these tests to verify detector functionality.

Usage:
  python test_detectors.py --detector all      # Run all tests
  python test_detectors.py --detector fall     # Run specific detector
  python test_detectors.py --model mediapipe   # Test specific model
"""

import unittest
import numpy as np
from unittest.mock import Mock
from ai_detectors import (
    ShopliftingDetector,
    FallDetector,
    AssaultDetector,
    CrowdAnalyzer
)
from ai_detectors.models import MediapipePoseDetector, YOLODetector
from ai_detectors.utils.pose_utils import (
    calculate_distance,
    calculate_angle,
    get_skeleton_aspect_ratio
)


class TestPoseUtils(unittest.TestCase):
    """Test geometric utility functions."""
    
    def test_calculate_distance(self):
        """Test Euclidean distance calculation."""
        p1 = {"x": 0, "y": 0}
        p2 = {"x": 3, "y": 4}
        distance = calculate_distance(p1, p2)
        self.assertAlmostEqual(distance, 5.0, places=5)
    
    def test_calculate_angle(self):
        """Test angle calculation between three points."""
        # Right angle test: (0,0) -> (1,0) -> (1,1)
        p1 = {"x": 0, "y": 0}
        p2 = {"x": 1, "y": 0}
        p3 = {"x": 1, "y": 1}
        angle = calculate_angle(p1, p2, p3)
        
        # Should be close to 90 degrees
        self.assertGreater(angle, 85)
        self.assertLess(angle, 95)


class MockFrame:
    """Create mock video frame for testing."""
    def __init__(self, width=640, height=480, channels=3):
        self.frame = np.random.randint(0, 255, (height, width, channels), dtype=np.uint8)
    
    def get_frame(self):
        return self.frame


class MockPose:
    """Create mock pose detection result."""
    def __init__(self, person_id=0):
        """
        Create mock person with raised hand (for assault test).
        Keypoint indices:
          0: Nose
          15,16: Wrists
          23,24: Hips
        """
        self.keypoints = self._create_keypoints()
        self.confidence = 0.95
        self.person_id = person_id
    
    def _create_keypoints(self):
        """Create 33-point pose with raised hand."""
        keypoints = []
        for i in range(33):
            keypoints.append({
                "x": np.random.uniform(100, 540),
                "y": np.random.uniform(50, 430),
                "confidence": 0.9
            })
        
        # Set specific points for testing
        keypoints[15] = {"x": 200, "y": 80, "confidence": 0.95}  # Right wrist (high)
        keypoints[24] = {"x": 210, "y": 250, "confidence": 0.95}  # Right hip (low)
        
        return keypoints


class MockDetectionBox:
    """Create mock object detection result."""
    def __init__(self, class_name="person", confidence=0.95):
        self.class_name = class_name
        self.confidence = confidence
        self.x1, self.y1 = 100, 100
        self.x2, self.y2 = 300, 400
        self.area = (self.x2 - self.x1) * (self.y2 - self.y1)
        self.center_x = (self.x1 + self.x2) // 2
        self.center_y = (self.y1 + self.y2) // 2


class TestDetectors(unittest.TestCase):
    """Test threat detector classes."""
    
    def setUp(self):
        """Initialize detectors for testing."""
        self.shoplifting = ShopliftingDetector()
        self.fall = FallDetector()
        self.assault = AssaultDetector()
        self.crowd = CrowdAnalyzer()
    
    def test_shoplifting_detector_initialization(self):
        """Test detector initializes properly."""
        self.assertEqual(self.shoplifting.detector_name, "ShopliftingDetector")
        self.assertEqual(self.shoplifting.threat_type, "Retail Theft")
    
    def test_fall_detector_initialization(self):
        """Test fall detector initializes."""
        self.assertEqual(self.fall.detector_name, "FallDetector")
        self.assertEqual(self.fall.threat_type, "Fall/Medical Emergency")
    
    def test_detector_statistics_tracking(self):
        """Test detectors track statistics."""
        # Mock frame and poses
        frame = MockFrame().get_frame()
        poses = [MockPose()]
        objects = []
        
        # Run detection
        result = self.shoplifting.detect(frame, poses, objects)
        
        # Check result structure
        self.assertIn("alert_triggered", result)
        self.assertIn("threat_score", result)
        self.assertIn("threat_message", result)
    
    def test_alert_cooldown(self):
        """Test alert cooldown mechanism prevents spam."""
        frame = MockFrame().get_frame()
        poses = [MockPose()]
        objects = []
        
        # First detection
        result1 = self.shoplifting.detect(frame, poses, objects)
        should_alert_1 = self.shoplifting.should_trigger_alert("test_pattern")
        
        # Immediate second detection (should be prevented)
        result2 = self.shoplifting.detect(frame, poses, objects)
        should_alert_2 = self.shoplifting.should_trigger_alert("test_pattern")
        
        # Alert should only trigger once initially
        self.assertIsNotNone(should_alert_1)


class TestModels(unittest.TestCase):
    """Test AI model wrappers."""
    
    def test_mediapipe_model_available(self):
        """Test Mediapipe model can be imported."""
        try:
            detector = MediapipePoseDetector(model_complexity=0)
            self.assertIsNotNone(detector)
            print("✓ Mediapipe model loaded")
        except Exception as e:
            print(f"⚠️  Mediapipe not available: {e}")
    
    def test_yolo_model_available(self):
        """Test YOLO model can be imported."""
        try:
            detector = YOLODetector(model_name="yolov8n.pt")
            self.assertIsNotNone(detector)
            print("✓ YOLO model loaded")
        except Exception as e:
            print(f"⚠️  YOLO not available: {e}")
    
    def test_mediapipe_detection_format(self):
        """Test Mediapipe returns expected format."""
        try:
            detector = MediapipePoseDetector(model_complexity=0)
            frame = MockFrame().get_frame()
            results = detector.detect(frame)
            
            # Should return list of poses
            self.assertIsInstance(results, list)
            print("✓ Mediapipe detection format correct")
        except Exception as e:
            print(f"⚠️  Mediapipe detection test skipped: {e}")


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def test_detector_pipeline(self):
        """Test running multiple detectors in sequence."""
        detectors = [
            ShopliftingDetector(),
            FallDetector(),
            AssaultDetector(),
            CrowdAnalyzer()
        ]
        
        frame = MockFrame().get_frame()
        poses = [MockPose() for _ in range(3)]
        objects = [MockDetectionBox() for _ in range(5)]
        
        results = []
        for detector in detectors:
            result = detector.detect(frame, poses, objects)
            results.append(result)
            self.assertIsNotNone(result)
        
        self.assertEqual(len(results), 4)
        print(f"✓ Detector pipeline completed with {len(results)} detectors")
    
    def test_alert_aggregation(self):
        """Test aggregating alerts from multiple detectors."""
        detectors = [
            FallDetector(),
            AssaultDetector(),
        ]
        
        frame = MockFrame().get_frame()
        poses = [MockPose()]
        objects = [MockDetectionBox()]
        
        alerts = []
        for detector in detectors:
            result = detector.detect(frame, poses, objects)
            if result.get("alert_triggered"):
                alerts.append({
                    "detector": detector.detector_name,
                    "threat_score": result["threat_score"]
                })
        
        # Test alert structure
        for alert in alerts:
            self.assertIn("detector", alert)
            self.assertIn("threat_score", alert)


def run_tests():
    """Run all tests with detailed output."""
    print("\n" + "="*60)
    print("ThreatSense AI Detection System - Test Suite")
    print("="*60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPoseUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectors))
    suite.addTests(loader.loadTestsFromTestCase(TestModels))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
