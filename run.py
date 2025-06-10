#!/usr/bin/env python
from flask import Flask
from app import create_app, db

app = create_app()

# Initialize the database
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 