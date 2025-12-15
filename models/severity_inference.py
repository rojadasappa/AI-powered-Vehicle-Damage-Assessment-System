import os
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import joblib
from PIL import Image
import cv2

def extract_advanced_features(image_path: str) -> np.ndarray:
    """Extract advanced features for the improved model - simplified to match training"""
    try:
        # Load image
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img)
        
        # Resize to standard size
        img_resized = cv2.resize(img_array, (224, 224))
        
        features = []
        
        # 1. Basic RGB histograms (reduced to match training)
        for channel in range(3):
            hist, _ = np.histogram(img_resized[:, :, channel], bins=32, range=(0, 255))
            features.extend(hist)
        
        # 2. Convert to grayscale
        gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
        
        # 3. Basic texture features
        features.extend([
            np.mean(gray),
            np.std(gray),
            np.var(gray),
            np.median(gray)
        ])
        
        # 4. Edge features
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        features.append(edge_density)
        
        # 5. Gradient features
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        features.extend([
            np.mean(gradient_magnitude),
            np.std(gradient_magnitude)
        ])
        
        # 6. HSV features
        hsv = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)
        for i in range(3):
            hist, _ = np.histogram(hsv[:, :, i], bins=32, range=(0, 256))
            features.extend(hist)
        
        # Ensure we have exactly 144 features
        features = features[:144]
        while len(features) < 144:
            features.append(0)
        
        return np.array(features)
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return np.zeros(144)  # Match the expected feature count from training

class ImprovedSeverityModel:
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        try:
            # Try to load voting classifier first
            self.model = joblib.load(self.model_dir / 'voting_model.pkl')
            self.scaler = joblib.load(self.model_dir / 'scaler.pkl')
            self.le = joblib.load(self.model_dir / 'label_encoder.pkl')
            print("Loaded improved voting classifier model")
        except FileNotFoundError:
            try:
                # Fallback to single model
                self.model = joblib.load(self.model_dir / 'model.pkl')
                self.scaler = joblib.load(self.model_dir / 'scaler.pkl')
                self.le = joblib.load(self.model_dir / 'label_encoder.pkl')
                print("Loaded improved single model")
            except FileNotFoundError:
                raise FileNotFoundError(f"No model found in {model_dir}")

    def predict_severity(self, image_paths: List[str]) -> Dict[str, Any]:
        feats = []
        ok_paths = []
        for p in image_paths:
            try:
                feat = extract_advanced_features(p)
                if len(feat) > 0:
                    feats.append(feat)
                    ok_paths.append(p)
            except Exception:
                continue
        
        if not feats:
            return {
                'severity': 'Minor',
                'confidence': 0.33,
                'details': []
            }
        
        X = np.vstack(feats)
        Xs = self.scaler.transform(X)
        
        # Get predictions and probabilities
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(Xs)
            idxs = proba.argmax(axis=1)
            confidences = proba.max(axis=1)
        else:
            idxs = self.model.predict(Xs)
            confidences = np.ones(len(idxs)) * 0.5
        
        preds = self.le.inverse_transform(idxs)
        
        # Weighted majority vote based on confidence
        unique_preds = np.unique(preds)
        weighted_votes = {}
        
        for pred in unique_preds:
            mask = preds == pred
            weighted_votes[pred] = np.sum(confidences[mask])
        
        majority = max(weighted_votes, key=weighted_votes.get)
        total_confidence = sum(weighted_votes.values())
        conf = weighted_votes[majority] / total_confidence if total_confidence > 0 else 0.5
        
        return {
            'severity': str(majority),
            'confidence': float(conf),
            'details': [{'path': p, 'pred': str(pr), 'conf': float(cf)} for p, pr, cf in zip(ok_paths, preds, confidences)]
        }
