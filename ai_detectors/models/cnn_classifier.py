"""
CNN Threat Classifier
=====================
Deep learning-based threat classification using Convolutional Neural Networks.
Classifies image regions as threat/safe for advanced threat assessment.

Architectures supported:
- ResNet50: Balanced accuracy/speed
- EfficientNet: Mobile-optimized
- VGG16: Small datasets
- Custom: User-trained models
"""

from typing import Dict, Tuple, Optional, List
import numpy as np
from ..config import CNN_CONFIG


class CNNClassifier:
    """
    CNN-based binary threat classifier.
    
    Classifies image patches as:
    0 = SAFE (normal behavior)
    1 = THREAT (suspicious/dangerous behavior)
    
    Uses transfer learning on standard architectures.
    """

    def __init__(self, model_architecture: str = "resnet50", weights_path: Optional[str] = None):
        """
        Initialize CNN classifier.
        
        Args:
            model_architecture: resnet50, efficientnet_b0, vgg16, etc.
            weights_path: Path to pre-trained weights (optional)
        """
        self.architecture = model_architecture
        self.weights_path = weights_path
        self.model = None
        self.preprocessor = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize CNN model using PyTorch or TensorFlow."""
        try:
            import torch
            import torchvision.models as models
            import torchvision.transforms as transforms
            
            # Load pre-trained model
            if self.architecture.lower() == "resnet50":
                self.model = models.resnet50(pretrained=CNN_CONFIG["pretrained"])
                # Modify final layer for binary classification
                in_features = self.model.fc.in_features
                self.model.fc = torch.nn.Linear(in_features, 2)
            elif self.architecture.lower() == "vgg16":
                self.model = models.vgg16(pretrained=CNN_CONFIG["pretrained"])
                self.model.classifier[-1] = torch.nn.Linear(4096, 2)
            else:
                print(f"⚠️  Architecture {self.architecture} not supported")
                return

            # Load custom weights if provided
            if self.weights_path:
                try:
                    checkpoint = torch.load(self.weights_path)
                    self.model.load_state_dict(checkpoint)
                    print(f"✓ Loaded weights from {self.weights_path}")
                except Exception as e:
                    print(f"⚠️  Could not load weights: {e}")

            # Set to eval mode
            self.model.eval()

            # Standard preprocessing pipeline
            self.preprocessor = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(CNN_CONFIG["input_size"]),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])

            print(f"✓ CNN Classifier ({self.architecture}) initialized successfully")
        except ImportError:
            print("⚠️  PyTorch not installed. Install with: pip install torch torchvision")
            self.model = None

    def classify_patch(self, patch: np.ndarray) -> Dict:
        """
        Classify a single image patch as threat/safe.
        
        Args:
            patch: Image patch (numpy array)
            
        Returns:
            {
                "threat": bool,
                "threat_score": float (0-1),
                "confidence": float (0-1),
                "class": str ("safe" or "threat")
            }
        """
        if self.model is None or self.preprocessor is None:
            return {"threat": False, "threat_score": 0.0, "confidence": 0.0, "class": "unknown"}

        try:
            import torch
            
            # Preprocess patch
            tensor = self.preprocessor(patch)
            tensor = tensor.unsqueeze(0)  # Add batch dimension

            # Inference
            with torch.no_grad():
                output = self.model(tensor)
                probabilities = torch.softmax(output, dim=1)
                threat_prob = probabilities[0, 1].item()
                safe_prob = probabilities[0, 0].item()

            return {
                "threat": threat_prob > 0.5,
                "threat_score": threat_prob,
                "confidence": max(threat_prob, safe_prob),
                "class": "threat" if threat_prob > 0.5 else "safe"
            }
        except Exception as e:
            print(f"❌ Classification error: {e}")
            return {"threat": False, "threat_score": 0.0, "confidence": 0.0, "class": "error"}

    def classify_patches(self, patches: List[np.ndarray]) -> List[Dict]:
        """Classify multiple patches in batch."""
        return [self.classify_patch(patch) for patch in patches]

    def extract_threat_score(self, classification: Dict) -> float:
        """Extract numerical threat score from classification result."""
        return classification.get("threat_score", 0.0) * 100
