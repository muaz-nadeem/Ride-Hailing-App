from datetime import datetime
from app import db

class Ride(db.Model):
    __tablename__ = 'rides'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    
    # Ride details
    pickup_address = db.Column(db.String(200))
    destination_address = db.Column(db.String(200))
    pickup_latitude = db.Column(db.Float)
    pickup_longitude = db.Column(db.Float)
    destination_latitude = db.Column(db.Float)
    destination_longitude = db.Column(db.Float)
    
    # Status and timestamps
    status = db.Column(db.String(20), default='requested')  # requested, accepted, in_progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Fare details
    estimated_fare = db.Column(db.Float)
    final_fare = db.Column(db.Float, nullable=True)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=True)
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    
    # Scheduled ride
    is_scheduled = db.Column(db.Boolean, default=False)
    scheduled_time = db.Column(db.DateTime, nullable=True)
    
    # Reviews
    review = db.relationship('Review', backref='ride', uselist=False)
    
    def __repr__(self):
        return f'<Ride {self.id}>'

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rider_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}>'

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_profiles.id'))
    payment_type = db.Column(db.String(20))  # credit_card, paypal, etc.
    card_number = db.Column(db.String(20), nullable=True)
    card_expiry = db.Column(db.String(7), nullable=True)  # MM/YYYY
    card_holder_name = db.Column(db.String(100), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    rides = db.relationship('Ride', backref='payment_method', lazy='dynamic')
    
    def __repr__(self):
        return f'<PaymentMethod {self.payment_type}>'