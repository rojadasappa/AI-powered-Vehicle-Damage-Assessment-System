"""
Repair Shop Finder with Location Services
Finds nearby repair shops and provides booking functionality
"""

import json
import math
from typing import List, Dict, Any, Optional
import logging
import requests
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepairShopFinder:
    def __init__(self, google_maps_api_key: str = None):
        self.google_maps_api_key = google_maps_api_key
        self.repair_shops = self.load_repair_shops()
        self.booking_slots = self.initialize_booking_slots()
    
    def load_repair_shops(self) -> List[Dict[str, Any]]:
        """Load repair shops from database or API"""
        # Sample repair shops data
        return [
            {
                "id": 1,
                "name": "AutoFix Pro",
                "address": "123 Main St, City, State 12345",
                "phone": "+1234567890",
                "email": "info@autofixpro.com",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "rating": 4.5,
                "services": ["Body Repair", "Paint", "Glass", "Mechanical"],
                "hours": {
                    "monday": "8:00 AM - 6:00 PM",
                    "tuesday": "8:00 AM - 6:00 PM",
                    "wednesday": "8:00 AM - 6:00 PM",
                    "thursday": "8:00 AM - 6:00 PM",
                    "friday": "8:00 AM - 6:00 PM",
                    "saturday": "9:00 AM - 4:00 PM",
                    "sunday": "Closed"
                },
                "specialties": ["Luxury Cars", "Classic Cars"],
                "certifications": ["ASE Certified", "I-CAR Certified"],
                "price_range": "$$$"
            },
            {
                "id": 2,
                "name": "Quick Repair Center",
                "address": "456 Oak Ave, City, State 12345",
                "phone": "+1234567891",
                "email": "contact@quickrepair.com",
                "latitude": 40.7589,
                "longitude": -73.9851,
                "rating": 4.2,
                "services": ["Collision Repair", "Paint", "Detailing"],
                "hours": {
                    "monday": "7:00 AM - 7:00 PM",
                    "tuesday": "7:00 AM - 7:00 PM",
                    "wednesday": "7:00 AM - 7:00 PM",
                    "thursday": "7:00 AM - 7:00 PM",
                    "friday": "7:00 AM - 7:00 PM",
                    "saturday": "8:00 AM - 5:00 PM",
                    "sunday": "10:00 AM - 3:00 PM"
                },
                "specialties": ["Quick Repairs", "Insurance Claims"],
                "certifications": ["ASE Certified"],
                "price_range": "$$"
            },
            {
                "id": 3,
                "name": "Elite Auto Body",
                "address": "789 Pine St, City, State 12345",
                "phone": "+1234567892",
                "email": "service@eliteautobody.com",
                "latitude": 40.7505,
                "longitude": -73.9934,
                "rating": 4.8,
                "services": ["Luxury Vehicle Repair", "Paint", "Restoration"],
                "hours": {
                    "monday": "9:00 AM - 5:00 PM",
                    "tuesday": "9:00 AM - 5:00 PM",
                    "wednesday": "9:00 AM - 5:00 PM",
                    "thursday": "9:00 AM - 5:00 PM",
                    "friday": "9:00 AM - 5:00 PM",
                    "saturday": "10:00 AM - 2:00 PM",
                    "sunday": "Closed"
                },
                "specialties": ["Luxury Vehicles", "Classic Cars", "Exotic Cars"],
                "certifications": ["I-CAR Certified", "ASE Master Certified"],
                "price_range": "$$$$"
            },
            {
                "id": 4,
                "name": "Budget Auto Repair",
                "address": "321 Elm St, City, State 12345",
                "phone": "+1234567893",
                "email": "info@budgetauto.com",
                "latitude": 40.7282,
                "longitude": -73.7949,
                "rating": 3.9,
                "services": ["Basic Repairs", "Paint", "Maintenance"],
                "hours": {
                    "monday": "8:00 AM - 5:00 PM",
                    "tuesday": "8:00 AM - 5:00 PM",
                    "wednesday": "8:00 AM - 5:00 PM",
                    "thursday": "8:00 AM - 5:00 PM",
                    "friday": "8:00 AM - 5:00 PM",
                    "saturday": "9:00 AM - 3:00 PM",
                    "sunday": "Closed"
                },
                "specialties": ["Budget Repairs", "Used Parts"],
                "certifications": ["ASE Certified"],
                "price_range": "$"
            },
            {
                "id": 5,
                "name": "Motorcycle Masters",
                "address": "654 Bike Ln, City, State 12345",
                "phone": "+1234567894",
                "email": "service@motorcyclemasters.com",
                "latitude": 40.6892,
                "longitude": -74.0445,
                "rating": 4.6,
                "services": ["Motorcycle Repair", "Custom Work", "Parts"],
                "hours": {
                    "monday": "9:00 AM - 6:00 PM",
                    "tuesday": "9:00 AM - 6:00 PM",
                    "wednesday": "9:00 AM - 6:00 PM",
                    "thursday": "9:00 AM - 6:00 PM",
                    "friday": "9:00 AM - 6:00 PM",
                    "saturday": "10:00 AM - 4:00 PM",
                    "sunday": "Closed"
                },
                "specialties": ["Motorcycles", "Scooters", "ATVs"],
                "certifications": ["Motorcycle Mechanic Certified"],
                "price_range": "$$"
            }
        ]
    
    def initialize_booking_slots(self) -> Dict[int, List[Dict]]:
        """Initialize booking slots for repair shops"""
        slots = {}
        for shop in self.repair_shops:
            slots[shop["id"]] = self.generate_booking_slots(shop["id"])
        return slots
    
    def generate_booking_slots(self, shop_id: int) -> List[Dict]:
        """Generate available booking slots for a repair shop"""
        slots = []
        start_date = datetime.now().date()
        
        for days_ahead in range(30):  # Next 30 days
            date = start_date + timedelta(days=days_ahead)
            day_name = date.strftime("%A").lower()
            
            # Get shop hours for this day
            shop = next((s for s in self.repair_shops if s["id"] == shop_id), None)
            if not shop or shop["hours"][day_name] == "Closed":
                continue
            
            # Generate time slots (every hour from 9 AM to 5 PM)
            for hour in range(9, 17):
                slot_time = datetime.combine(date, datetime.min.time().replace(hour=hour))
                slots.append({
                    "shop_id": shop_id,
                    "date": date.isoformat(),
                    "time": slot_time.strftime("%H:%M"),
                    "datetime": slot_time.isoformat(),
                    "available": True,
                    "duration": 60  # 1 hour slots
                })
        
        return slots
    
    def find_nearby_shops(self, latitude: float, longitude: float, radius_km: float = 10.0, 
                         vehicle_type: str = None, damage_type: str = None) -> List[Dict[str, Any]]:
        """Find repair shops near the given location"""
        try:
            nearby_shops = []
            
            for shop in self.repair_shops:
                # Calculate distance
                distance = self.calculate_distance(latitude, longitude, 
                                                shop["latitude"], shop["longitude"])
                
                if distance <= radius_km:
                    # Filter by vehicle type if specified
                    if vehicle_type and not self.shop_supports_vehicle_type(shop, vehicle_type):
                        continue
                    
                    # Filter by damage type if specified
                    if damage_type and not self.shop_supports_damage_type(shop, damage_type):
                        continue
                    
                    shop_info = shop.copy()
                    shop_info["distance_km"] = round(distance, 2)
                    shop_info["distance_miles"] = round(distance * 0.621371, 2)
                    nearby_shops.append(shop_info)
            
            # Sort by distance
            nearby_shops.sort(key=lambda x: x["distance_km"])
            
            return nearby_shops
            
        except Exception as e:
            logger.error(f"Error finding nearby shops: {e}")
            return []
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        try:
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Radius of earth in kilometers
            r = 6371
            return c * r
            
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return float('inf')
    
    def shop_supports_vehicle_type(self, shop: Dict, vehicle_type: str) -> bool:
        """Check if shop supports the given vehicle type - only supports cars"""
        # Only support cars, so check for car-related services
        required_services = ["Body Repair", "Paint", "Glass", "Mechanical"]
        shop_services = [service.lower() for service in shop.get("services", [])]
        return any(service.lower() in shop_services for service in required_services)
    
    def shop_supports_damage_type(self, shop: Dict, damage_type: str) -> bool:
        """Check if shop supports the given damage type"""
        damage_mapping = {
            "Dent": ["Body Repair", "Paint"],
            "Scratch": ["Paint", "Detailing"],
            "Broken Part": ["Body Repair", "Mechanical"],
            "Crack": ["Body Repair", "Paint", "Glass"],
            "Rust": ["Body Repair", "Paint"],
            "Paint Damage": ["Paint", "Detailing"],
            "Structural Damage": ["Body Repair", "Mechanical"],
            "Glass Damage": ["Glass"],
            "Light Damage": ["Body Repair", "Mechanical"],
            "Bumper Damage": ["Body Repair", "Paint"]
        }
        
        required_services = damage_mapping.get(damage_type, [])
        if not required_services:
            return True  # Assume support if no specific requirements
        
        shop_services = [service.lower() for service in shop.get("services", [])]
        return any(service.lower() in shop_services for service in required_services)
    
    def get_shop_details(self, shop_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific repair shop"""
        try:
            shop = next((s for s in self.repair_shops if s["id"] == shop_id), None)
            if not shop:
                return None
            
            # Add additional details
            shop_details = shop.copy()
            shop_details["available_slots"] = self.get_available_slots(shop_id)
            shop_details["reviews"] = self.get_shop_reviews(shop_id)
            shop_details["estimated_wait_time"] = self.get_estimated_wait_time(shop_id)
            
            return shop_details
            
        except Exception as e:
            logger.error(f"Error getting shop details: {e}")
            return None
    
    def get_available_slots(self, shop_id: int, date: str = None) -> List[Dict]:
        """Get available booking slots for a repair shop"""
        try:
            if date:
                # Filter slots for specific date
                return [slot for slot in self.booking_slots.get(shop_id, []) 
                       if slot["date"] == date and slot["available"]]
            else:
                # Return all available slots
                return [slot for slot in self.booking_slots.get(shop_id, []) 
                       if slot["available"]]
                
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []
    
    def book_appointment(self, shop_id: int, user_id: int, slot_datetime: str, 
                        vehicle_info: Dict, damage_info: Dict) -> Dict[str, Any]:
        """Book an appointment with a repair shop"""
        try:
            # Find the slot
            slot = next((s for s in self.booking_slots.get(shop_id, []) 
                        if s["datetime"] == slot_datetime and s["available"]), None)
            
            if not slot:
                return {
                    "success": False,
                    "message": "Selected time slot is no longer available"
                }
            
            # Mark slot as booked
            slot["available"] = False
            slot["booked_by"] = user_id
            slot["vehicle_info"] = vehicle_info
            slot["damage_info"] = damage_info
            slot["booking_time"] = datetime.now().isoformat()
            
            # Generate booking confirmation
            booking_id = f"BK{shop_id:03d}{int(datetime.now().timestamp())}"
            
            return {
                "success": True,
                "booking_id": booking_id,
                "message": "Appointment booked successfully",
                "appointment_details": {
                    "shop_id": shop_id,
                    "date": slot["date"],
                    "time": slot["time"],
                    "booking_id": booking_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {
                "success": False,
                "message": "Failed to book appointment. Please try again."
            }
    
    def get_shop_reviews(self, shop_id: int) -> List[Dict]:
        """Get reviews for a repair shop"""
        # Sample reviews data
        sample_reviews = [
            {
                "id": 1,
                "shop_id": shop_id,
                "user_name": "John D.",
                "rating": 5,
                "comment": "Excellent service! Fixed my car quickly and professionally.",
                "date": "2024-01-15"
            },
            {
                "id": 2,
                "shop_id": shop_id,
                "user_name": "Sarah M.",
                "rating": 4,
                "comment": "Good work, but took longer than expected.",
                "date": "2024-01-10"
            },
            {
                "id": 3,
                "shop_id": shop_id,
                "user_name": "Mike R.",
                "rating": 5,
                "comment": "Highly recommend! Fair prices and great quality work.",
                "date": "2024-01-05"
            }
        ]
        
        return sample_reviews
    
    def get_estimated_wait_time(self, shop_id: int) -> str:
        """Get estimated wait time for a repair shop"""
        # This would typically be calculated based on current bookings
        # For now, return sample data
        wait_times = ["1-2 days", "3-5 days", "1 week", "2 weeks"]
        return wait_times[shop_id % len(wait_times)]
    
    def search_shops(self, query: str, filters: Dict = None) -> List[Dict[str, Any]]:
        """Search repair shops by name, services, or location"""
        try:
            results = []
            query_lower = query.lower()
            
            for shop in self.repair_shops:
                # Search in name, services, and specialties
                if (query_lower in shop["name"].lower() or
                    any(query_lower in service.lower() for service in shop["services"]) or
                    any(query_lower in specialty.lower() for specialty in shop["specialties"])):
                    
                    # Apply filters if provided
                    if filters:
                        if "rating_min" in filters and shop["rating"] < filters["rating_min"]:
                            continue
                        if "price_range" in filters and shop["price_range"] != filters["price_range"]:
                            continue
                        if "services" in filters:
                            required_services = filters["services"]
                            shop_services = [s.lower() for s in shop["services"]]
                            if not any(service.lower() in shop_services for service in required_services):
                                continue
                    
                    results.append(shop)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching shops: {e}")
            return []
    
    def get_directions(self, shop_id: int, user_latitude: float, user_longitude: float) -> Dict[str, Any]:
        """Get directions to a repair shop"""
        try:
            shop = next((s for s in self.repair_shops if s["id"] == shop_id), None)
            if not shop:
                return {"error": "Shop not found"}
            
            if self.google_maps_api_key:
                # Use Google Maps API for directions
                return self.get_google_directions(
                    user_latitude, user_longitude,
                    shop["latitude"], shop["longitude"]
                )
            else:
                # Return basic directions info
                return {
                    "shop_address": shop["address"],
                    "distance_km": self.calculate_distance(
                        user_latitude, user_longitude,
                        shop["latitude"], shop["longitude"]
                    ),
                    "estimated_drive_time": "15-30 minutes"  # Rough estimate
                }
                
        except Exception as e:
            logger.error(f"Error getting directions: {e}")
            return {"error": "Failed to get directions"}
    
    def get_google_directions(self, origin_lat: float, origin_lng: float, 
                            dest_lat: float, dest_lng: float) -> Dict[str, Any]:
        """Get directions using Google Maps API"""
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": f"{origin_lat},{origin_lng}",
                "destination": f"{dest_lat},{dest_lng}",
                "key": self.google_maps_api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "OK":
                route = data["routes"][0]
                leg = route["legs"][0]
                
                return {
                    "distance": leg["distance"]["text"],
                    "duration": leg["duration"]["text"],
                    "steps": [step["html_instructions"] for step in leg["steps"]],
                    "polyline": route["overview_polyline"]["points"]
                }
            else:
                return {"error": f"Google Maps API error: {data['status']}"}
                
        except Exception as e:
            logger.error(f"Error getting Google directions: {e}")
            return {"error": "Failed to get directions from Google Maps"}
