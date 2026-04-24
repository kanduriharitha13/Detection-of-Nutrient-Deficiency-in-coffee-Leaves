import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

class ModelLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
            cls._instance.class_indices = {}
            cls._instance.idx_to_class = {}
        return cls._instance

    def load_model(self, model_path, class_indices_path):
        if self.model is not None:
            return

        print(f"Loading model from {model_path}...")
        
        # Load class indices
        if os.path.exists(class_indices_path):
            with open(class_indices_path, 'r') as f:
                self.class_indices = json.load(f)
                self.idx_to_class = {v: k for k, v in self.class_indices.items()}
        else:
            print("Warning: class_indices.json not found!")

        num_classes = len(self.class_indices) if self.class_indices else 10 # Default fallback
        
        # Reconstruct Model Architecture
        self.model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        self.model.classifier[1] = nn.Linear(self.model.last_channel, num_classes)
        
        # Load Weights
        if os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
        else:
            print(f"Error: Model file {model_path} not found.")
            return

        self.model.to(self.device)
        self.model.eval()
        print("Model loaded successfully.")

    def predict(self, image_bytes):
        if self.model is None:
            raise Exception("Model not loaded")
        
        # Preprocess
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        image = Image.open(image_bytes).convert('RGB')
        image_tensor = transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
            
            predicted_idx = predicted_idx.item()
            confidence_score = confidence.item() * 100
            
            class_name = self.idx_to_class.get(predicted_idx, "Unknown")
            
            return {
                "class": class_name,
                "confidence": f"{confidence_score:.2f}%",
                "confidence_val": confidence_score
            }

model_loader = ModelLoader()
