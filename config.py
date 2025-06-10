import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/fleet_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    LEAFLET_API_KEY = os.environ.get('LEAFLET_API_KEY') or 'your-leaflet-api-key'
    
    # Admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@fleetapp.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin_password' 