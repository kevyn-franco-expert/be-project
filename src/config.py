import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'vehicle_rental'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'testing123!'),
        'port': int(os.getenv('DB_PORT', 3306))
    }
    
    # Email configuration
    EMAIL_CONFIG = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'email': os.getenv('EMAIL_USER', ''),
        'password': os.getenv('EMAIL_PASSWORD', '')
    }
    
    # Flask configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))