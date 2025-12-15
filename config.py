"""
Configuration file for Vehicle Damage Assessment System
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vehicle_damage.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyA72bvrQlkTv8OYgWutv72w-D3ewc3UKhs')
    
    # Analysis configuration
    ENABLE_GEMINI_ANALYSIS = bool(os.getenv('GEMINI_API_KEY'))
    ANALYSIS_CONFIDENCE_THRESHOLD = 0.6
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration"""
        app.config.from_object(Config)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
