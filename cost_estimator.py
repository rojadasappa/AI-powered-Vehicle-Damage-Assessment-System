"""
Cost Estimation System for Vehicle Damage Assessment
"""

import json
import os
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CostEstimator:
    def __init__(self):
        self.cost_database = self.load_cost_database()
        self.labor_rates = self.load_labor_rates()
        self.part_costs = self.load_part_costs()
    
    def load_cost_database(self) -> Dict[str, Any]:
        """Load repair cost database"""
        try:
            cost_db_path = 'data/cost_database.json'
            if os.path.exists(cost_db_path):
                with open(cost_db_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default cost database
                return self.create_default_cost_database()
        except Exception as e:
            logger.error(f"Error loading cost database: {e}")
            return self.create_default_cost_database()
    
    def create_default_cost_database(self) -> Dict[str, Any]:
        """Create default cost database with sample data"""
        return {
            "vehicle_types": {
                "Car": {
                    "base_labor_rate": 800,
                    "parts_multiplier": 1.0
                },
                "Motorcycle": {
                    "base_labor_rate": 600,
                    "parts_multiplier": 0.8
                },
                "Scooter": {
                    "base_labor_rate": 500,
                    "parts_multiplier": 0.6
                },
                "Bicycle": {
                    "base_labor_rate": 300,
                    "parts_multiplier": 0.4
                },
                "Bus": {
                    "base_labor_rate": 1000,
                    "parts_multiplier": 2.0
                },
                "Truck": {
                    "base_labor_rate": 900,
                    "parts_multiplier": 1.5
                },
                "Van": {
                    "base_labor_rate": 850,
                    "parts_multiplier": 1.2
                },
                "Train": {
                    "base_labor_rate": 1200,
                    "parts_multiplier": 3.0
                }
            },
            "damage_types": {
                "Dent": {
                    "base_cost": 5000,
                    "labor_hours": 3,
                    "complexity_factor": 1.2
                },
                "Scratch": {
                    "base_cost": 3500,
                    "labor_hours": 2,
                    "complexity_factor": 1.0
                },
                "Broken Part": {
                    "base_cost": 8000,
                    "labor_hours": 5,
                    "complexity_factor": 1.8
                },
                "Crack": {
                    "base_cost": 6000,
                    "labor_hours": 3,
                    "complexity_factor": 1.4
                },
                "Rust": {
                    "base_cost": 7000,
                    "labor_hours": 4,
                    "complexity_factor": 1.5
                },
                "Paint Damage": {
                    "base_cost": 4500,
                    "labor_hours": 2.5,
                    "complexity_factor": 1.1
                },
                "Structural Damage": {
                    "base_cost": 20000,
                    "labor_hours": 12,
                    "complexity_factor": 2.5
                },
                "Glass Damage": {
                    "base_cost": 3000,
                    "labor_hours": 1.5,
                    "complexity_factor": 1.0
                },
                "Light Damage": {
                    "base_cost": 2500,
                    "labor_hours": 2,
                    "complexity_factor": 0.9
                },
                "Bumper Damage": {
                    "base_cost": 6500,
                    "labor_hours": 4,
                    "complexity_factor": 1.3
                }
            },
            "severity_multipliers": {
                "Minor": 0.5,
                "Moderate": 1.0,
                "Severe": 1.8,
                "Critical": 2.5
            }
        }
    
    def load_labor_rates(self) -> Dict[str, float]:
        """Load labor rates by region"""
        return {
            "India": 800,
            "US": 75,
            "EU": 65,
            "Asia": 45,
            "Other": 50
        }
    
    def load_part_costs(self) -> Dict[str, Dict[str, float]]:
        """Load part costs by vehicle type"""
        return {
            "Car": {
                "bumper": 5000,
                "door": 8000,
                "headlight": 2500,
                "windshield": 4000,
                "mirror": 1200,
                "fender": 3500
            },
            "Motorcycle": {
                "fairing": 3000,
                "tank": 5000,
                "headlight": 1200,
                "mirror": 800,
                "exhaust": 2500
            },
            "Scooter": {
                "body_panel": 2000,
                "headlight": 1000,
                "mirror": 500,
                "seat": 1200
            },
            "Bicycle": {
                "frame": 3000,
                "wheel": 1200,
                "handlebar": 800,
                "seat": 600
            }
        }
    
    def estimate_cost(self, damage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate repair cost based on damage analysis results"""
        try:
            vehicle_type = damage_results.get('vehicle_type', 'Car')
            damage_type = damage_results.get('damage_type', 'Unknown')
            severity = damage_results.get('severity', 'Moderate')
            confidence = damage_results.get('confidence', 0.5)
            
            # Get base costs
            vehicle_info = self.cost_database['vehicle_types'].get(vehicle_type, 
                                                                 self.cost_database['vehicle_types']['Car'])
            damage_info = self.cost_database['damage_types'].get(damage_type, 
                                                               self.cost_database['damage_types']['Scratch'])
            severity_multiplier = self.cost_database['severity_multipliers'].get(severity, 1.0)
            
            # Calculate base cost
            base_cost = damage_info['base_cost']
            labor_hours = damage_info['labor_hours']
            complexity_factor = damage_info['complexity_factor']
            
            # Apply vehicle type multiplier
            vehicle_multiplier = vehicle_info['parts_multiplier']
            
            # Calculate parts cost
            parts_cost = base_cost * vehicle_multiplier * severity_multiplier
            
            # Calculate labor cost
            labor_rate = vehicle_info['base_labor_rate']
            labor_cost = labor_hours * labor_rate * complexity_factor * severity_multiplier
            
            # Apply confidence adjustment (lower confidence = higher uncertainty = higher cost)
            confidence_factor = 1.0 + (1.0 - confidence) * 0.3  # Up to 30% increase for low confidence
            
            # Calculate total cost
            total_cost = (parts_cost + labor_cost) * confidence_factor
            
            # Add additional costs
            additional_costs = self.calculate_additional_costs(vehicle_type, damage_type, severity)
            
            # Calculate breakdown
            cost_breakdown = {
                'parts_cost': round(parts_cost, 2),
                'labor_cost': round(labor_cost, 2),
                'additional_costs': round(additional_costs, 2),
                'confidence_adjustment': round((confidence_factor - 1) * 100, 1),
                'total_cost': round(total_cost + additional_costs, 2),
                'currency': 'INR'
            }
            
            # Generate repair recommendations
            recommendations = self.generate_repair_recommendations(vehicle_type, damage_type, severity, total_cost)
            
            return {
                'total_cost': round(total_cost + additional_costs, 2),
                'cost_breakdown': cost_breakdown,
                'recommendations': recommendations,
                'estimated_repair_time': self.estimate_repair_time(damage_type, severity),
                'confidence_level': self.get_confidence_level(confidence)
            }
            
        except Exception as e:
            logger.error(f"Error estimating cost: {e}")
            return {
                'total_cost': 0,
                'cost_breakdown': {},
                'recommendations': [],
                'error': str(e)
            }
    
    def calculate_additional_costs(self, vehicle_type: str, damage_type: str, severity: str) -> float:
        """Calculate additional costs like paint, materials, etc."""
        additional_cost = 0
        
        # Paint costs
        if damage_type in ['Paint Damage', 'Scratch']:
            paint_cost = 2000 if vehicle_type == 'Car' else 1000
            additional_cost += paint_cost
        
        # Material costs
        if damage_type in ['Structural Damage', 'Broken Part']:
            material_cost = 3500 if severity in ['Severe', 'Critical'] else 1800
            additional_cost += material_cost
        
        # Specialized equipment costs
        if vehicle_type in ['Bus', 'Truck', 'Train']:
            equipment_cost = 2500 if severity in ['Severe', 'Critical'] else 1200
            additional_cost += equipment_cost
        
        # Labor overhead (shop supplies, insurance, etc.)
        overhead_cost = 1000 if vehicle_type == 'Car' else 600
        additional_cost += overhead_cost
        
        return additional_cost
    
    def generate_repair_recommendations(self, vehicle_type: str, damage_type: str, severity: str, cost: float) -> List[Dict[str, Any]]:
        """Generate repair recommendations based on damage analysis"""
        recommendations = []
        
        # Basic repair recommendation
        recommendations.append({
            'type': 'Basic Repair',
            'description': f'Standard repair for {damage_type.lower()} damage',
            'estimated_cost': round(cost * 0.8, 2),
            'time_estimate': self.estimate_repair_time(damage_type, severity),
            'priority': 'High'
        })
        
        # Premium repair option for severe damage
        if severity in ['Severe', 'Critical']:
            recommendations.append({
                'type': 'Premium Repair',
                'description': 'High-quality repair with warranty',
                'estimated_cost': round(cost * 1.3, 2),
                'time_estimate': self.estimate_repair_time(damage_type, severity) + 2,
                'priority': 'Medium'
            })
        
        # Insurance claim recommendation
        if cost > 1000:
            recommendations.append({
                'type': 'Insurance Claim',
                'description': 'Consider filing an insurance claim',
                'estimated_cost': round(cost * 0.1, 2),  # Deductible
                'time_estimate': 7,  # Days for processing
                'priority': 'High'
            })
        
        # DIY option for minor damage
        if severity == 'Minor' and damage_type in ['Scratch', 'Paint Damage']:
            recommendations.append({
                'type': 'DIY Repair',
                'description': 'Do-it-yourself repair kit',
                'estimated_cost': round(cost * 0.2, 2),
                'time_estimate': 1,
                'priority': 'Low'
            })
        
        return recommendations
    
    def estimate_repair_time(self, damage_type: str, severity: str) -> int:
        """Estimate repair time in days"""
        base_times = {
            'Dent': 1,
            'Scratch': 1,
            'Broken Part': 3,
            'Crack': 2,
            'Rust': 2,
            'Paint Damage': 2,
            'Structural Damage': 5,
            'Glass Damage': 1,
            'Light Damage': 1,
            'Bumper Damage': 2
        }
        
        severity_multipliers = {
            'Minor': 0.5,
            'Moderate': 1.0,
            'Severe': 1.5,
            'Critical': 2.0
        }
        
        base_time = base_times.get(damage_type, 2)
        multiplier = severity_multipliers.get(severity, 1.0)
        
        return max(1, int(base_time * multiplier))
    
    def get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description"""
        if confidence >= 0.9:
            return 'Very High'
        elif confidence >= 0.7:
            return 'High'
        elif confidence >= 0.5:
            return 'Medium'
        elif confidence >= 0.3:
            return 'Low'
        else:
            return 'Very Low'
    
    def save_cost_database(self, path: str = 'data/cost_database.json'):
        """Save cost database to file"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                json.dump(self.cost_database, f, indent=2)
            logger.info(f"Cost database saved to {path}")
        except Exception as e:
            logger.error(f"Error saving cost database: {e}")
    
    def update_cost_database(self, new_costs: Dict[str, Any]):
        """Update cost database with new data"""
        try:
            self.cost_database.update(new_costs)
            self.save_cost_database()
            logger.info("Cost database updated successfully")
        except Exception as e:
            logger.error(f"Error updating cost database: {e}")
