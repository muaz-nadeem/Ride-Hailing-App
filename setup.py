import os
import sys
import random
import string
from getpass import getpass

def generate_secret_key(length=24):
    """Generate a random secret key."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(random.choice(chars) for _ in range(length))

def setup_env_file():
    """Create or update the .env file with required configurations."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Check if .env already exists
    if os.path.exists(env_path):
        overwrite = input(".env file already exists. Overwrite? (y/n): ").lower() == 'y'
        if not overwrite:
            print("Setup cancelled.")
            return False
    
    # Get database credentials
    db_user = input("PostgreSQL username [postgres]: ") or "postgres"
    db_password = getpass("PostgreSQL password: ")
    db_host = input("PostgreSQL host [localhost]: ") or "localhost"
    db_port = input("PostgreSQL port [5432]: ") or "5432"
    db_name = input("Database name [fleet_db]: ") or "fleet_db"
    
    # Generate a secret key
    secret_key = generate_secret_key()
    
    # Create the .env file
    env_content = f"""SECRET_KEY={secret_key}
DATABASE_URL=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}
FLASK_APP=app.py
FLASK_ENV=development
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f".env file created at {env_path}")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def create_database():
    """Attempt to create the PostgreSQL database."""
    try:
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv()
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("DATABASE_URL not found in .env file.")
            return False
        
        # Extract database name and connection info
        db_name = db_url.split('/')[-1]
        conn_url = '/'.join(db_url.split('/')[:-1]) + '/postgres'  # Connect to postgres db to create new db
        
        # Connect to postgres
        conn = psycopg2.connect(conn_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def initialize_app():
    """Initialize the Flask application."""
    try:
        from flask.cli import FlaskGroup
        from app import app
        
        cli = FlaskGroup(app)
        
        # Run Flask db init, migrate, and upgrade
        import subprocess
        
        print("Initializing database...")
        subprocess.check_call([sys.executable, "-m", "flask", "db", "init"])
        subprocess.check_call([sys.executable, "-m", "flask", "db", "migrate", "-m", "Initial migration"])
        subprocess.check_call([sys.executable, "-m", "flask", "db", "upgrade"])
        
        print("Database initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing application: {e}")
        return False

def main():
    print("=== Fleet Management Application Setup ===")
    
    # Setup environment variables
    print("\nSetting up environment variables...")
    if not setup_env_file():
        return
    
    # Create database
    print("\nCreating database...")
    if not create_database():
        print("Warning: Could not create database. You may need to create it manually.")
    
    # Initialize application
    print("\nInitializing application...")
    if initialize_app():
        print("\n=== Setup Complete! ===")
        print("You can now run the application with 'flask run'")
    else:
        print("\nSetup incomplete. Please check the error messages above.")

if __name__ == "__main__":
    main() 