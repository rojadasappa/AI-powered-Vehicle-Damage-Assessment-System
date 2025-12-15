"""
Enhanced Cost Estimation System for Vehicle Damage Assessment
Integrates with Gemini AI for realistic Indian pricing
"""

import json
import os
import logging
from typing import Dict, Any, List
import openai
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCostEstimator:
    def __init__(self, openai_api_key: str = None):
        """Initialize enhanced cost estimator with OpenAI AI integration"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.base_costs = self.load_base_costs()
        self.indian_regions = self.load_indian_regions()
        
        if self.openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                self.openai_available = True
                logger.info("Enhanced cost estimator with OpenAI AI initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI AI: {e}")
                self.openai_available = False
        else:
            self.openai_available = False
            logger.warning("No OpenAI API key provided. Using fallback pricing.")
    
    def load_base_costs(self) -> Dict[str, Any]:
        """Load base cost database with Indian market data"""
        return {
            "vehicle_types": {
                "Car": {
                    "base_labor_rate": 1200,  # INR per hour
                    "parts_multiplier": 1.0,
                    "complexity_factor": 1.0
                },
                "SUV": {
                    "base_labor_rate": 1400,
                    "parts_multiplier": 1.2,
                    "complexity_factor": 1.1
                },
                "Hatchback": {
                    "base_labor_rate": 1000,
                    "parts_multiplier": 0.8,
                    "complexity_factor": 0.9
                },
                "Sedan": {
                    "base_labor_rate": 1200,
                    "parts_multiplier": 1.0,
                    "complexity_factor": 1.0
                },
                "Motorcycle": {
                    "base_labor_rate": 600,
                    "parts_multiplier": 0.4,
                    "complexity_factor": 0.7
                },
                "Scooter": {
                    "base_labor_rate": 500,
                    "parts_multiplier": 0.3,
                    "complexity_factor": 0.6
                },
                "Truck": {
                    "base_labor_rate": 1800,
                    "parts_multiplier": 2.0,
                    "complexity_factor": 1.5
                },
                "Bus": {
                    "base_labor_rate": 2000,
                    "parts_multiplier": 2.5,
                    "complexity_factor": 1.8
                }
            },
            "damage_types": {
                "Scratch": {
                    "base_cost": 2500,
                    "labor_hours": 2,
                    "complexity_factor": 1.0,
                    "parts_cost": 800
                },
                "Dent": {
                    "base_cost": 4000,
                    "labor_hours": 3,
                    "complexity_factor": 1.2,
                    "parts_cost": 1200
                },
                "Paint Damage": {
                    "base_cost": 3500,
                    "labor_hours": 2.5,
                    "complexity_factor": 1.1,
                    "parts_cost": 1500
                },
                "Bumper Damage": {
                    "base_cost": 8000,
                    "labor_hours": 4,
                    "complexity_factor": 1.3,
                    "parts_cost": 3500
                },
                "Broken Part": {
                    "base_cost": 12000,
                    "labor_hours": 6,
                    "complexity_factor": 1.8,
                    "parts_cost": 6000
                },
                "Crack": {
                    "base_cost": 6000,
                    "labor_hours": 3,
                    "complexity_factor": 1.4,
                    "parts_cost": 2500
                },
                "Rust": {
                    "base_cost": 8000,
                    "labor_hours": 4,
                    "complexity_factor": 1.5,
                    "parts_cost": 3000
                },
                "Structural Damage": {
                    "base_cost": 25000,
                    "labor_hours": 12,
                    "complexity_factor": 2.5,
                    "parts_cost": 15000
                },
                "Minor Dent": {
                    "base_cost": 3000,
                    "labor_hours": 2,
                    "complexity_factor": 1.0,
                    "parts_cost": 1000
                },
                "Surface Damage": {
                    "base_cost": 2000,
                    "labor_hours": 1.5,
                    "complexity_factor": 0.9,
                    "parts_cost": 500
                },
                "Panel Damage": {
                    "base_cost": 6000,
                    "labor_hours": 4,
                    "complexity_factor": 1.3,
                    "parts_cost": 2000
                },
                "Major Collision": {
                    "base_cost": 25000,
                    "labor_hours": 12,
                    "complexity_factor": 2.5,
                    "parts_cost": 15000
                },
                "Total Loss": {
                    "base_cost": 100000,
                    "labor_hours": 40,
                    "complexity_factor": 5.0,
                    "parts_cost": 80000
                },
                "Glass Damage": {
                    "base_cost": 4000,
                    "labor_hours": 1.5,
                    "complexity_factor": 1.0,
                    "parts_cost": 2000
                },
                "Headlight Damage": {
                    "base_cost": 5000,
                    "labor_hours": 2,
                    "complexity_factor": 1.1,
                    "parts_cost": 3000
                }
            },
            "severity_multipliers": {
                "Minor": 0.6,
                "Moderate": 1.0,
                "Severe": 1.6,
                "Critical": 2.2
            },
            "indian_market_factors": {
                "metro_cities": 1.3,  # Mumbai, Delhi, Bangalore, Chennai
                "tier1_cities": 1.1,  # Pune, Hyderabad, Ahmedabad, etc.
                "tier2_cities": 0.9,  # Smaller cities
                "rural_areas": 0.7    # Rural areas
            }
        }
    
    def load_indian_regions(self) -> Dict[str, str]:
        """Load Indian regions and their classifications"""
        return {
            "mumbai": "metro_cities",
            "delhi": "metro_cities",
            "bangalore": "metro_cities",
            "chennai": "metro_cities",
            "kolkata": "metro_cities",
            "hyderabad": "tier1_cities",
            "pune": "tier1_cities",
            "ahmedabad": "tier1_cities",
            "jaipur": "tier1_cities",
            "lucknow": "tier1_cities",
            "kanpur": "tier1_cities",
            "nagpur": "tier1_cities",
            "indore": "tier1_cities",
            "thane": "tier1_cities",
            "bhopal": "tier1_cities",
            "visakhapatnam": "tier1_cities",
            "pimpri": "tier1_cities",
            "patna": "tier1_cities",
            "vadodara": "tier1_cities",
            "ghaziabad": "tier1_cities",
            "ludhiana": "tier1_cities",
            "agra": "tier2_cities",
            "nashik": "tier2_cities",
            "faridabad": "tier2_cities",
            "meerut": "tier2_cities",
            "rajkot": "tier2_cities",
            "kalyan": "tier2_cities",
            "vasai": "tier2_cities",
            "varanasi": "tier2_cities",
            "srinagar": "tier2_cities"
        }
    
    def get_openai_cost_estimate(self, damage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get cost estimate using OpenAI AI for realistic Indian pricing"""
        if not self.openai_available:
            return self.get_fallback_cost_estimate(damage_results)
        
        try:
            vehicle_type = damage_results.get('vehicle_type', 'Car')
            damage_type = damage_results.get('damage_type', 'Scratch')
            raw_severity = damage_results.get('severity', 'Moderate')
            severity = self.map_severity(raw_severity)
            confidence = damage_results.get('confidence', 0.5)
            location = damage_results.get('location', 'Mumbai')
            
            prompt = f"""
            As an expert automotive repair cost estimator in India, please provide a detailed cost breakdown for the following vehicle damage:

            Vehicle Type: {vehicle_type}
            Damage Type: {damage_type}
            Severity: {severity}
            Location: {location}
            Confidence Level: {confidence:.2f}

            Please provide a realistic cost estimate in Indian Rupees (INR) considering:
            1. Current Indian market rates (2024)
            2. Regional pricing variations
            3. Labor costs in {location}
            4. Parts availability and costs
            5. GST (18%) and other taxes
            6. Workshop overhead costs

            Respond in the following JSON format:
            {{
                "total_cost": 0,
                "cost_breakdown": {{
                    "parts_cost": 0,
                    "labor_cost": 0,
                    "paint_cost": 0,
                    "taxes_gst": 0,
                    "overhead_cost": 0,
                    "additional_costs": 0
                }},
                "repair_time_days": 0,
                "complexity_level": "Simple/Moderate/Complex/Expert",
                "market_analysis": {{
                    "price_range": "Low/Medium/High/Premium",
                    "availability": "Readily Available/Moderate/Scarce/Rare",
                    "regional_factor": 1.0
                }},
                "recommendations": [
                    "Specific repair recommendations",
                    "Cost-saving tips",
                    "Quality considerations"
                ],
                "confidence_score": 0.0
            }}

            Be realistic and consider Indian market conditions, local availability of parts, and regional labor costs.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse OpenAI response
            try:
                import re
                content = response.choices[0].message.content
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    cost_data = json.loads(json_str)
                    return self.validate_openai_response(cost_data, damage_results)
                else:
                    return self.parse_text_response(content, damage_results)
            except Exception as e:
                logger.error(f"Error parsing OpenAI response: {e}")
                return self.parse_text_response(content, damage_results)
                
        except Exception as e:
            logger.error(f"Error getting OpenAI cost estimate: {e}")
            return self.get_fallback_cost_estimate(damage_results)
    
    def validate_openai_response(self, cost_data: Dict[str, Any], damage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean OpenAI response"""
        try:
            # Ensure all required fields exist
            validated = {
                "total_cost": float(cost_data.get("total_cost", 0)),
                "cost_breakdown": {
                    "parts_cost": float(cost_data.get("cost_breakdown", {}).get("parts_cost", 0)),
                    "labor_cost": float(cost_data.get("cost_breakdown", {}).get("labor_cost", 0)),
                    "paint_cost": float(cost_data.get("cost_breakdown", {}).get("paint_cost", 0)),
                    "taxes_gst": float(cost_data.get("cost_breakdown", {}).get("taxes_gst", 0)),
                    "overhead_cost": float(cost_data.get("cost_breakdown", {}).get("overhead_cost", 0)),
                    "additional_costs": float(cost_data.get("cost_breakdown", {}).get("additional_costs", 0))
                },
                "repair_time_days": int(cost_data.get("repair_time_days", 1)),
                "complexity_level": cost_data.get("complexity_level", "Moderate"),
                "market_analysis": cost_data.get("market_analysis", {}),
                "recommendations": cost_data.get("recommendations", []),
                "confidence_score": float(cost_data.get("confidence_score", 0.7)),
                "source": "Gemini AI",
                "timestamp": datetime.now().isoformat()
            }
            
            # Validate total cost matches breakdown
            breakdown_total = sum(validated["cost_breakdown"].values())
            if abs(validated["total_cost"] - breakdown_total) > 1000:  # Allow 1000 INR difference
                validated["total_cost"] = breakdown_total
            
            return validated
            
        except Exception as e:
            logger.error(f"Error validating Gemini response: {e}")
            return self.get_fallback_cost_estimate(damage_results)
    
    def parse_text_response(self, text: str, damage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        # Extract numbers from text
        import re
        numbers = re.findall(r'\d+', text)
        
        # Estimate costs based on text content
        total_cost = 5000  # Default
        if numbers:
            # Try to find the largest number as total cost
            total_cost = max([int(n) for n in numbers if int(n) > 100])
        
        return {
            "total_cost": total_cost,
            "cost_breakdown": {
                "parts_cost": total_cost * 0.4,
                "labor_cost": total_cost * 0.3,
                "paint_cost": total_cost * 0.1,
                "taxes_gst": total_cost * 0.15,
                "overhead_cost": total_cost * 0.05,
                "additional_costs": 0
            },
            "repair_time_days": 3,
            "complexity_level": "Moderate",
            "market_analysis": {
                "price_range": "Medium",
                "availability": "Moderate",
                "regional_factor": 1.0
            },
            "recommendations": ["Get multiple quotes", "Check warranty", "Verify parts quality"],
            "confidence_score": 0.6,
            "source": "Gemini AI (Text Parse)",
            "timestamp": datetime.now().isoformat()
        }
    
    def map_severity(self, severity: str) -> str:
        """Map model severity format to cost estimator format"""
        severity_mapping = {
            '01-minor': 'Minor',
            '02-moderate': 'Moderate', 
            '03-severe': 'Severe',
            'minor': 'Minor',
            'moderate': 'Moderate',
            'severe': 'Severe',
            'Minor': 'Minor',
            'Moderate': 'Moderate',
            'Severe': 'Severe'
        }
        return severity_mapping.get(severity, 'Moderate')

    def get_fallback_cost_estimate(self, damage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback cost estimate using base pricing"""
        vehicle_type = damage_results.get('vehicle_type', 'Car')
        damage_type = damage_results.get('damage_type', 'Scratch')
        raw_severity = damage_results.get('severity', 'Moderate')
        severity = self.map_severity(raw_severity)
        confidence = damage_results.get('confidence', 0.5)
        location = damage_results.get('location', 'Mumbai')
        
        # Get base costs
        vehicle_info = self.base_costs['vehicle_types'].get(vehicle_type, 
                                                           self.base_costs['vehicle_types']['Car'])
        damage_info = self.base_costs['damage_types'].get(damage_type, 
                                                         self.base_costs['damage_types']['Scratch'])
        severity_multiplier = self.base_costs['severity_multipliers'].get(severity, 1.0)
        
        # Calculate costs
        parts_cost = damage_info['parts_cost'] * vehicle_info['parts_multiplier'] * severity_multiplier
        labor_hours = damage_info['labor_hours'] * severity_multiplier
        labor_cost = labor_hours * vehicle_info['base_labor_rate'] * vehicle_info['complexity_factor']
        
        # Apply regional factor
        region = self.get_region_classification(location)
        regional_factor = self.base_costs['indian_market_factors'].get(region, 1.0)
        
        # Calculate additional costs
        paint_cost = damage_info.get('paint_cost', 0) if 'paint' in damage_type.lower() else 0
        taxes_gst = (parts_cost + labor_cost + paint_cost) * 0.18  # 18% GST
        overhead_cost = (parts_cost + labor_cost) * 0.1  # 10% overhead
        
        # Apply regional factor
        total_before_tax = (parts_cost + labor_cost + paint_cost + overhead_cost) * regional_factor
        total_cost = total_before_tax + taxes_gst
        
        return {
            "total_cost": round(total_cost, 2),
            "cost_breakdown": {
                "parts_cost": round(parts_cost * regional_factor, 2),
                "labor_cost": round(labor_cost * regional_factor, 2),
                "paint_cost": round(paint_cost * regional_factor, 2),
                "taxes_gst": round(taxes_gst, 2),
                "overhead_cost": round(overhead_cost * regional_factor, 2),
                "additional_costs": 0
            },
            "repair_time_days": max(1, int(damage_info['labor_hours'] * severity_multiplier / 8)),
            "complexity_level": self.get_complexity_level(severity, damage_type),
            "market_analysis": {
                "price_range": self.get_price_range(total_cost),
                "availability": "Moderate",
                "regional_factor": regional_factor
            },
            "recommendations": self.generate_recommendations(vehicle_type, damage_type, severity, total_cost),
            "confidence_score": confidence,
            "source": "Base Pricing Model",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_region_classification(self, location: str) -> str:
        """Get region classification for location"""
        location_lower = location.lower()
        for city, region in self.indian_regions.items():
            if city in location_lower:
                return region
        return "tier1_cities"  # Default
    
    def get_complexity_level(self, severity: str, damage_type: str) -> str:
        """Get complexity level based on severity and damage type"""
        if severity == "Critical" or damage_type == "Structural Damage":
            return "Expert"
        elif severity == "Severe" or damage_type in ["Broken Part", "Rust"]:
            return "Complex"
        elif severity == "Moderate":
            return "Moderate"
        else:
            return "Simple"
    
    def get_price_range(self, total_cost: float) -> str:
        """Get price range classification"""
        if total_cost < 5000:
            return "Low"
        elif total_cost < 15000:
            return "Medium"
        elif total_cost < 50000:
            return "High"
        else:
            return "Premium"
    
    def generate_recommendations(self, vehicle_type: str, damage_type: str, severity: str, cost: float) -> List[str]:
        """Generate repair recommendations"""
        recommendations = []
        
        # Basic recommendations
        recommendations.append("Get quotes from at least 3 different workshops")
        recommendations.append("Check for insurance coverage before proceeding")
        
        # Cost-specific recommendations
        if cost > 10000:
            recommendations.append("Consider filing an insurance claim")
            recommendations.append("Verify workshop is insurance-approved")
        
        # Severity-specific recommendations
        if severity in ["Severe", "Critical"]:
            recommendations.append("Get a detailed inspection before repair")
            recommendations.append("Consider OEM parts for better quality")
        
        # Damage-specific recommendations
        if damage_type in ["Paint Damage", "Scratch"]:
            recommendations.append("Ask about paint matching guarantee")
        
        if damage_type == "Structural Damage":
            recommendations.append("Ensure structural integrity is maintained")
            recommendations.append("Get certification from authorized workshop")
        
        # Vehicle-specific recommendations
        if vehicle_type in ["Truck", "Bus"]:
            recommendations.append("Check for commercial vehicle insurance")
        
        return recommendations
    
    def estimate_cost(self, damage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to estimate repair cost"""
        try:
            if self.openai_available:
                return self.get_openai_cost_estimate(damage_results)
            else:
                return self.get_fallback_cost_estimate(damage_results)
        except Exception as e:
            logger.error(f"Error in cost estimation: {e}")
            return self.get_fallback_cost_estimate(damage_results)
    
    def get_market_insights(self, vehicle_type: str, damage_type: str, location: str) -> Dict[str, Any]:
        """Get market insights for specific damage and location"""
        if not self.openai_available:
            return {"insights": "OpenAI AI not available for market insights"}
        
        try:
            prompt = f"""
            Provide current market insights for vehicle repair in India:

            Vehicle Type: {vehicle_type}
            Damage Type: {damage_type}
            Location: {location}

            Include:
            1. Current market trends
            2. Price fluctuations
            3. Parts availability
            4. Popular repair methods
            5. Quality considerations

            Keep it concise and relevant to Indian market.
            """
            
            response = self.model.generate_content(prompt)
            return {
                "insights": response.text,
                "timestamp": datetime.now().isoformat(),
                "location": location
            }
        except Exception as e:
            logger.error(f"Error getting market insights: {e}")
            return {"insights": "Unable to fetch market insights"}

# Global instance
enhanced_cost_estimator = EnhancedCostEstimator()

def estimate_repair_cost(damage_results: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to estimate repair cost using enhanced estimator"""
    try:
        return enhanced_cost_estimator.estimate_cost(damage_results)
    except Exception as e:
        logger.error(f"Error in enhanced cost estimation: {e}")
        return {
            "total_cost": 0,
            "cost_breakdown": {},
            "error": str(e)
        }
