"""
OpenAI-based Damage Analyzer for Vehicle Damage Assessment
Replaces Gemini AI with OpenAI API for better availability and performance
"""

import os
import base64
import json
import logging
from typing import Dict, Any, List
import openai
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIDamageAnalyzer:
    def __init__(self, api_key: str = None):
        """Initialize OpenAI damage analyzer"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        self.available = False
        
        if self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                self.available = True
                logger.info("OpenAI damage analyzer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.available = False
        else:
            logger.warning("No OpenAI API key provided")
            self.available = False
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return None
    
    def analyze_damage(self, image_paths: List[str]) -> Dict[str, Any]:
        """Analyze vehicle damage using OpenAI Vision API"""
        if not self.available or not image_paths:
            return self.get_fallback_analysis()
        
        try:
            # Use the first image for analysis
            image_path = image_paths[0]
            base64_image = self.encode_image(image_path)
            
            if not base64_image:
                return self.get_fallback_analysis()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this vehicle damage image and provide a detailed assessment. 
                                
                                Please respond with a JSON object containing:
                                {
                                    "vehicle_type": "Car/SUV/Truck/Motorcycle",
                                    "damage_type": "Scratch/Dent/Paint Damage/Bumper Damage/Broken Part/Major Collision/Structural Damage",
                                    "damage_description": "Detailed description of the damage",
                                    "severity": "Minor/Moderate/Severe",
                                    "affected_areas": ["List of affected body parts"],
                                    "repair_urgency": "Low/Medium/High",
                                    "estimated_repair_complexity": "Simple/Moderate/Complex",
                                    "safety_concerns": "None/Minor/Major",
                                    "confidence": 0.0-1.0
                                }
                                
                                Focus on Indian market context and realistic assessment."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # Fallback parsing
                    result = self.parse_text_response(content)
            except json.JSONDecodeError:
                result = self.parse_text_response(content)
            
            # Ensure all required fields are present
            result = self.validate_response(result)
            
            return {
                'vehicle_type': result.get('vehicle_type', 'Car'),
                'damage_type': result.get('damage_type', 'Unknown'),
                'damage_description': result.get('damage_description', 'Damage detected'),
                'severity': result.get('severity', 'Moderate'),
                'affected_areas': result.get('affected_areas', []),
                'repair_urgency': result.get('repair_urgency', 'Medium'),
                'estimated_repair_complexity': result.get('estimated_repair_complexity', 'Moderate'),
                'safety_concerns': result.get('safety_concerns', 'None'),
                'confidence': float(result.get('confidence', 0.7)),
                'analysis_method': 'openai',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return self.get_fallback_analysis()
    
    def parse_text_response(self, content: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        result = {}
        
        # Simple text parsing
        lines = content.split('\n')
        for line in lines:
            if 'vehicle_type' in line.lower():
                result['vehicle_type'] = self.extract_value(line, 'Car')
            elif 'damage_type' in line.lower():
                result['damage_type'] = self.extract_value(line, 'Unknown')
            elif 'severity' in line.lower():
                result['severity'] = self.extract_value(line, 'Moderate')
            elif 'confidence' in line.lower():
                try:
                    result['confidence'] = float(self.extract_value(line, '0.7'))
                except:
                    result['confidence'] = 0.7
        
        return result
    
    def extract_value(self, line: str, default: str) -> str:
        """Extract value from a line of text"""
        try:
            # Look for colon separator
            if ':' in line:
                return line.split(':', 1)[1].strip().strip('"').strip("'")
            return default
        except:
            return default
    
    def validate_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix the response"""
        # Ensure vehicle_type is valid
        valid_vehicles = ['Car', 'SUV', 'Truck', 'Motorcycle', 'Van', 'Bus']
        if result.get('vehicle_type') not in valid_vehicles:
            result['vehicle_type'] = 'Car'
        
        # Ensure damage_type is valid
        valid_damage_types = [
            'Scratch', 'Dent', 'Paint Damage', 'Bumper Damage', 'Broken Part',
            'Major Collision', 'Structural Damage', 'Minor Dent', 'Surface Damage',
            'Panel Damage', 'Total Loss'
        ]
        if result.get('damage_type') not in valid_damage_types:
            result['damage_type'] = 'Unknown'
        
        # Ensure severity is valid
        valid_severities = ['Minor', 'Moderate', 'Severe']
        if result.get('severity') not in valid_severities:
            result['severity'] = 'Moderate'
        
        # Ensure confidence is between 0 and 1
        confidence = result.get('confidence', 0.7)
        try:
            confidence = float(confidence)
            result['confidence'] = max(0.0, min(1.0, confidence))
        except:
            result['confidence'] = 0.7
        
        return result
    
    def get_fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when OpenAI is not available"""
        return {
            'vehicle_type': 'Car',
            'damage_type': 'Unknown',
            'damage_description': 'Unable to analyze - OpenAI not available',
            'severity': 'Moderate',
            'affected_areas': [],
            'repair_urgency': 'Medium',
            'estimated_repair_complexity': 'Moderate',
            'safety_concerns': 'None',
            'confidence': 0.5,
            'analysis_method': 'fallback',
            'timestamp': datetime.now().isoformat()
        }

# Global instance
openai_analyzer = OpenAIDamageAnalyzer()

def detect_damage_with_openai(image_paths: List[str]) -> Dict[str, Any]:
    """Detect damage using OpenAI API"""
    return openai_analyzer.analyze_damage(image_paths)
