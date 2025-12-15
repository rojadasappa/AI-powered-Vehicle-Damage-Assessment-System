from datetime import datetime

# Import db from the main app when this module is imported
def init_db(database):
    global db
    db = database

class RepairShop:
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    
    # Location coordinates
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Business details
    rating = db.Column(db.Float, default=0.0)
    price_range = db.Column(db.String(20))  # $, $$, $$$, $$$$
    specialties = db.Column(db.Text)  # JSON string of specialties
    working_hours = db.Column(db.Text)  # JSON string of working hours
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<RepairShop {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'rating': self.rating,
            'price_range': self.price_range,
            'specialties': self.specialties,
            'working_hours': self.working_hours,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    @classmethod
    def find_nearby_shops(cls, user_lat, user_lon, radius_km=10, limit=20):
        """Find repair shops within specified radius"""
        shops = cls.query.filter_by(is_active=True).all()
        nearby_shops = []
        
        for shop in shops:
            distance = cls.calculate_distance(user_lat, user_lon, shop.latitude, shop.longitude)
            if distance <= radius_km:
                shop_data = shop.to_dict()
                shop_data['distance'] = round(distance, 2)
                nearby_shops.append(shop_data)
        
        # Sort by distance
        nearby_shops.sort(key=lambda x: x['distance'])
        return nearby_shops[:limit]
