#!/usr/bin/env python3
"""
Improved Vehicle Damage Severity Classification Model
Uses advanced feature extraction and ensemble methods for 90%+ accuracy
"""

import argparse
import os
import numpy as np
from pathlib import Path
from typing import List, Tuple
import json
import joblib
from PIL import Image
import cv2
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

def extract_advanced_features(image_path: str) -> np.ndarray:
    """Extract comprehensive features for better classification"""
    try:
        # Load image
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img)
        
        # Resize to standard size
        img_resized = cv2.resize(img_array, (224, 224))
        
        features = []
        
        # 1. Color features (HSV histograms)
        hsv = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)
        for i in range(3):
            hist = cv2.calcHist([hsv], [i], None, [32], [0, 256])
            features.extend(hist.flatten())
        
        # 2. Texture features (LBP-like)
        gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
        
        # Local Binary Pattern approximation
        lbp_features = []
        for i in range(0, gray.shape[0]-8, 8):
            for j in range(0, gray.shape[1]-8, 8):
                patch = gray[i:i+8, j:j+8]
                center = patch[4, 4]
                lbp = 0
                for k, (di, dj) in enumerate([(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]):
                    if patch[4+di, 4+dj] >= center:
                        lbp += 2**k
                lbp_features.append(lbp)
        
        # LBP histogram
        lbp_hist, _ = np.histogram(lbp_features, bins=16, range=(0, 255))
        features.extend(lbp_hist)
        
        # 3. Edge features
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        features.append(edge_density)
        
        # 4. Gradient features
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        features.extend([
            np.mean(gradient_magnitude),
            np.std(gradient_magnitude),
            np.max(gradient_magnitude)
        ])
        
        # 5. Statistical features
        features.extend([
            np.mean(img_resized),
            np.std(img_resized),
            np.var(img_resized),
            np.median(img_resized)
        ])
        
        # 6. Color moments
        for channel in range(3):
            channel_data = img_resized[:, :, channel].flatten()
            features.extend([
                np.mean(channel_data),
                np.std(channel_data),
                np.var(channel_data),
                np.median(channel_data)
            ])
        
        # 7. Contour features
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter ** 2)
            else:
                circularity = 0
            features.extend([area, perimeter, circularity])
        else:
            features.extend([0, 0, 0])
        
        # 8. Histogram of Oriented Gradients (HOG) approximation
        hog_features = []
        for i in range(0, gray.shape[0]-16, 16):
            for j in range(0, gray.shape[1]-16, 16):
                cell = gray[i:i+16, j:j+16]
                if cell.shape == (16, 16):
                    gx = cv2.Sobel(cell, cv2.CV_64F, 1, 0, ksize=3)
                    gy = cv2.Sobel(cell, cv2.CV_64F, 0, 1, ksize=3)
                    magnitude = np.sqrt(gx**2 + gy**2)
                    orientation = np.arctan2(gy, gx) * 180 / np.pi
                    orientation[orientation < 0] += 180
                    
                    # Create histogram
                    hist, _ = np.histogram(orientation, bins=9, range=(0, 180), weights=magnitude)
                    hog_features.extend(hist)
        
        # Take mean of HOG features
        if hog_features:
            hog_features = np.array(hog_features).reshape(-1, 9)
            hog_mean = np.mean(hog_features, axis=0)
            features.extend(hog_mean)
        else:
            features.extend([0] * 9)
        
        return np.array(features)
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        # Return zero features if processing fails
        return np.zeros(200)  # Adjust size based on total features

def load_dataset(data_dir: Path) -> Tuple[np.ndarray, List[str]]:
    """Load dataset with improved feature extraction"""
    X: List[np.ndarray] = []
    y: List[str] = []
    
    classes = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])
    if not classes:
        raise RuntimeError(f"No class folders found under {data_dir}")
    
    print(f"Found classes: {classes}")
    
    for cls in classes:
        print(f"Processing class: {cls}")
        class_images = []
        
        for ext in ('*.jpg', '*.jpeg', '*.JPEG', '*.png', '*.bmp'):
            class_images.extend(list((data_dir / cls).glob(ext)))
        
        print(f"  Found {len(class_images)} images")
        
        for img_path in class_images:
            feat = extract_advanced_features(str(img_path))
            if feat is not None and len(feat) > 0:
                X.append(feat)
                y.append(cls)
        
        print(f"  Processed {len([x for x in y if x == cls])} images for class {cls}")
    
    if not X:
        raise RuntimeError("No images found or failed feature extraction.")
    
    print(f"Total samples: {len(X)}")
    print(f"Feature dimension: {len(X[0])}")
    
    return np.vstack(X), y

def create_ensemble_model():
    """Create ensemble model for better accuracy"""
    models = {
        'rf': RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),
        'gb': GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=8,
            random_state=42
        ),
        'svm': SVC(
            kernel='rbf',
            C=10,
            gamma='scale',
            probability=True,
            random_state=42
        ),
        'lr': LogisticRegression(
            max_iter=1000,
            random_state=42,
            n_jobs=-1
        )
    }
    return models

def train_ensemble_models(X_train, y_train, X_val, y_val):
    """Train ensemble of models"""
    models = create_ensemble_model()
    trained_models = {}
    scores = {}
    
    # Report class distribution before balancing
    print("\nClass distribution BEFORE SMOTE (train):", dict(Counter(y_train)))

    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Use SMOTE for imbalanced data
        smote = SMOTE(random_state=42, k_neighbors=min(5, max(1, int(np.min(np.bincount(y_train))**0.5))))
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

        # Report class distribution after balancing (once per model for visibility)
        print("  Balanced train distribution:", dict(Counter(y_train_balanced)))
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_balanced)
        X_val_scaled = scaler.transform(X_val)
        
        # Train model
        model.fit(X_train_scaled, y_train_balanced)
        
        # Evaluate
        y_pred = model.predict(X_val_scaled)
        accuracy = accuracy_score(y_val, y_pred)
        scores[name] = accuracy
        
        print(f"  {name} accuracy: {accuracy:.4f}")
        
        trained_models[name] = {
            'model': model,
            'scaler': scaler,
            'accuracy': accuracy
        }
    
    return trained_models, scores

def create_voting_classifier(trained_models):
    """Create voting classifier from best models"""
    from sklearn.ensemble import VotingClassifier
    
    # Select best models (accuracy > 0.7)
    best_models = [(name, data['model']) for name, data in trained_models.items() 
                   if data['accuracy'] > 0.7]
    
    if len(best_models) < 2:
        # If no models meet threshold, use all models
        best_models = [(name, data['model']) for name, data in trained_models.items()]
    
    voting_clf = VotingClassifier(
        estimators=best_models,
        voting='soft'  # Use predicted probabilities
    )
    
    return voting_clf, trained_models[best_models[0][0]]['scaler']

def main():
    parser = argparse.ArgumentParser(description='Train improved severity classification model')
    parser.add_argument('--data', required=True, help='Path to car_damage_severity dataset root')
    parser.add_argument('--out', default='models/saved_models/severity_improved', help='Output dir for artifacts')
    parser.add_argument('--test_size', type=float, default=0.2)
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("IMPROVED VEHICLE DAMAGE SEVERITY CLASSIFICATION")
    print("=" * 60)
    
    print(f"Loading dataset from {data_dir}...")
    X, y = load_dataset(data_dir)
    
    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    
    print(f"Classes: {le.classes_}")
    print(f"Class distribution: {np.bincount(y_enc)}")
    
    # Train-validation split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_enc, test_size=args.test_size, stratify=y_enc, random_state=42
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    
    # Train ensemble models
    print("\nTraining ensemble models...")
    trained_models, scores = train_ensemble_models(X_train, y_train, X_val, y_val)
    
    # Create voting classifier
    print("\nCreating voting classifier...")
    voting_clf, best_scaler = create_voting_classifier(trained_models)
    
    # Train voting classifier
    print("Training voting classifier...")
    smote = SMOTE(random_state=42, k_neighbors=min(5, max(1, int(np.min(np.bincount(y_train))**0.5))))
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    print("Balanced train distribution for voting clf:", dict(Counter(y_train_balanced)))
    X_train_scaled = best_scaler.transform(X_train_balanced)
    X_val_scaled = best_scaler.transform(X_val)
    
    voting_clf.fit(X_train_scaled, y_train_balanced)
    
    # Final evaluation
    print("\nFinal evaluation...")
    y_pred = voting_clf.predict(X_val_scaled)
    y_pred_proba = voting_clf.predict_proba(X_val_scaled)
    
    accuracy = accuracy_score(y_val, y_pred)
    print(f"Final accuracy: {accuracy:.4f}")
    
    # Cross-validation
    print("Performing cross-validation...")
    cv_scores = cross_val_score(voting_clf, X_train_scaled, y_train_balanced, cv=5)
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Detailed report
    report = classification_report(y_val, y_pred, target_names=le.classes_, digits=4)
    print(f"\nClassification Report:\n{report}")
    
    # Confusion matrix
    cm = confusion_matrix(y_val, y_pred)
    print(f"\nConfusion Matrix:\n{cm}")
    
    # Save artifacts
    print(f"\nSaving artifacts to {out_dir}...")
    
    # Save the voting classifier and scaler
    joblib.dump(voting_clf, out_dir / 'voting_model.pkl')
    joblib.dump(best_scaler, out_dir / 'scaler.pkl')
    joblib.dump(le, out_dir / 'label_encoder.pkl')
    
    # Save individual models
    for name, data in trained_models.items():
        joblib.dump(data['model'], out_dir / f'{name}_model.pkl')
        joblib.dump(data['scaler'], out_dir / f'{name}_scaler.pkl')
    
    # Save metadata
    meta = {
        'feature_extraction': 'advanced_multi_feature',
        'classes': list(le.classes_),
        'feature_count': X.shape[1],
        'training_samples': len(X_train),
        'validation_samples': len(X_val),
        'individual_scores': scores,
        'final_accuracy': float(accuracy),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'models_used': list(trained_models.keys())
    }
    
    (out_dir / 'meta.json').write_text(json.dumps(meta, indent=2))
    (out_dir / 'report.txt').write_text(report)
    (out_dir / 'confusion_matrix.txt').write_text(str(cm))
    
    print(f"✅ Model training completed!")
    print(f"Final accuracy: {accuracy:.4f}")
    print(f"Cross-validation mean: {cv_scores.mean():.4f}")
    
    if accuracy >= 0.90:
        print("🎉 Target accuracy of 90%+ achieved!")
    else:
        print("⚠️  Target accuracy not reached. Consider:")
        print("   - More training data")
        print("   - Data augmentation")
        print("   - Different feature extraction methods")

if __name__ == '__main__':
    main()
