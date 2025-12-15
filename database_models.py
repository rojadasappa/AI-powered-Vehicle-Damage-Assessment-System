"""
Database models for the Vehicle Damage Assessment System
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    damage_reports = db.relationship('DamageReport', backref='user', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password_hash, password)

class DamageReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    damage_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    estimated_cost = db.Column(db.Float)
    confidence_score = db.Column(db.Float)
    image_paths = db.Column(db.Text)  # JSON string of image paths
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Additional fields for detailed reporting
    damage_description = db.Column(db.Text)
    affected_areas = db.Column(db.Text)  # JSON string of affected areas
    repair_urgency = db.Column(db.String(20))
    estimated_repair_complexity = db.Column(db.String(20))
    safety_concerns = db.Column(db.String(20))
    repair_time_days = db.Column(db.Integer)
    cost_breakdown = db.Column(db.Text)  # JSON string of cost breakdown
    recommendations = db.Column(db.Text)  # JSON string of recommendations
    
    # Property to maintain backward compatibility
    @property
    def confidence(self):
        return self.confidence_score or 0.0

class RepairShop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    services = db.Column(db.Text)  # JSON string of services offered
    rating = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
