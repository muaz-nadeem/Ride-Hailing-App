from datetime import datetime
from app import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100))
    make = db.Column(db.String(100))
    year = db.Column(db.Integer)
    license_plate = db.Column(db.String(20), unique=True)
    vehicle_type = db.Column(db.String(50))  # sedan, suv, luxury, etc.
    capacity = db.Column(db.Integer, default=4)
    color = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    base_fare = db.Column(db.Float)
    per_km_rate = db.Column(db.Float)
    per_minute_rate = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    rider = db.relationship('RiderProfile', backref='vehicle', uselist=False)
    rides = db.relationship('Ride', backref='vehicle', lazy='dynamic')
    
    def __repr__(self):
        return f'<Vehicle {self.license_plate}>'

class VehicleMaintenanceLog(db.Model):
    __tablename__ = 'vehicle_maintenance_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    maintenance_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    cost = db.Column(db.Float)
    service_date = db.Column(db.DateTime)
    next_service_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vehicle = db.relationship('Vehicle', backref='maintenance_logs')
    
    def __repr__(self):
        return f'<Maintenance {self.maintenance_type} for {self.vehicle.license_plate}>' 