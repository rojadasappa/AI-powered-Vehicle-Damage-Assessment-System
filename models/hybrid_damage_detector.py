"""
Hybrid Damage Detection System
Combines OpenAI AI analysis with severity-only ML model for optimal accuracy
"""

import os
import logging
from typing import List, Dict, Any
from .openai_damage_analyzer import detect_damage_with_openai
from .severity_inference import ImprovedSeverityModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridDamageDetector:
    def __init__(self):
        self.openai_available = os.getenv('OPENAI_API_KEY') is not None
        self.severity_model = None
        model_dir = os.getenv('SEVERITY_MODEL_DIR', 'models/saved_models/severity_best')
        try:
            if os.path.exists(os.path.join(model_dir, 'voting_model.pkl')):
                self.severity_model = ImprovedSeverityModel(model_dir)
                logger.info(f"Loaded severity model from {model_dir}")
            else:
                logger.warning("Severity model artifacts not found; severity will be estimated via Gemini if available")
        except Exception as e:
            logger.error(f"Failed to load severity model: {e}")

    def analyze_images(self, image_paths: List[str]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        # Severity via local model if available
        if self.severity_model:
            sev = self.severity_model.predict_severity(image_paths)
            result['severity'] = sev['severity']
            result['severity_confidence'] = sev['confidence']
            result['severity_details'] = sev['details']
        # Damage type via OpenAI if available
        if self.openai_available:
            openai_result = detect_damage_with_openai(image_paths)
            result['vehicle_type'] = openai_result.get('vehicle_type', 'Car')
            result['damage_type'] = openai_result.get('damage_type', 'Unknown')
            result['damage_description'] = openai_result.get('damage_description')
            result['confidence'] = float((result.get('severity_confidence', 0.5) + openai_result.get('confidence', 0.5)) / 2)
            result['analysis_method'] = 'openai+severity'
            result['affected_areas'] = openai_result.get('affected_areas', [])
            result['repair_urgency'] = openai_result.get('repair_urgency', 'Low')
            result['estimated_repair_complexity'] = openai_result.get('estimated_repair_complexity', 'Simple')
            result['safety_concerns'] = openai_result.get('safety_concerns', 'None')
        else:
            # Fallback: only severity with basic damage type
            result.setdefault('vehicle_type', 'Car')
            result['damage_type'] = 'Unknown'
            result['confidence'] = float(result.get('severity_confidence', 0.5))
            result['analysis_method'] = 'severity-only'
        result['total_images'] = len(image_paths)
        return result



hybrid_detector = HybridDamageDetector()

def detect_damage_hybrid(image_paths):
    try:
        return hybrid_detector.analyze_images(image_paths)
    except Exception as e:
        logger.error(f"Hybrid detection error: {e}")
        return {
            'vehicle_type': 'Car',
            'damage_type': 'Unknown',
            'severity': 'Minor',
            'confidence': 0.5,
            'total_images': len(image_paths) if image_paths else 0,
            'analysis_method': 'error'
        }

def detect_damage_simple(image_paths):
    """Simple damage detection using only severity model"""
    try:
        if not image_paths:
            return {
                'vehicle_type': 'Car',
                'damage_type': 'Unknown',
                'severity': 'Minor',
                'confidence': 0.5,
                'total_images': 0,
                'analysis_method': 'severity-only'
            }
        
        # Use only severity model for simple detection
        if hybrid_detector.severity_model:
            sev = hybrid_detector.severity_model.predict_severity(image_paths)
            return {
                'vehicle_type': 'Car',
                'damage_type': 'Unknown',
                'severity': sev['severity'],
                'confidence': sev['confidence'],
                'total_images': len(image_paths),
                'analysis_method': 'severity-only',
                'severity_details': sev['details']
            }
        else:
            # Fallback if no model available
            return {
                'vehicle_type': 'Car',
                'damage_type': 'Unknown',
                'severity': 'Minor',
                'confidence': 0.5,
                'total_images': len(image_paths),
                'analysis_method': 'fallback'
            }
    except Exception as e:
        logger.error(f"Simple detection error: {e}")
        return {
            'vehicle_type': 'Car',
            'damage_type': 'Unknown',
            'severity': 'Minor',
            'confidence': 0.5,
            'total_images': len(image_paths) if image_paths else 0,
            'analysis_method': 'error'
        }
