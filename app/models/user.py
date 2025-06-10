from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20), default='customer')  # customer, rider, admin
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - fixed to remove lazy='dynamic' from one-to-one relationships
    customer_profile = db.relationship('CustomerProfile', backref='user', uselist=False)
    rider_profile = db.relationship('RiderProfile', backref='user', uselist=False)
    reviews_given = db.relationship('Review', backref='customer', lazy='dynamic', foreign_keys='Review.customer_id')
    reviews_received = db.relationship('Review', backref='rider', lazy='dynamic', foreign_keys='Review.rider_id')
    # Add rides relationship at User level
    customer_rides = db.relationship('Ride', backref='customer', lazy='dynamic', foreign_keys='Ride.customer_id')
    rider_rides = db.relationship('Ride', backref='rider', lazy='dynamic', foreign_keys='Ride.rider_id')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_rider(self):
        return self.user_type == 'rider'
    
    def is_customer(self):
        return self.user_type == 'customer'
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class CustomerProfile(db.Model):
    __tablename__ = 'customer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    home_address = db.Column(db.String(200))
    work_address = db.Column(db.String(200))
    payment_methods = db.relationship('PaymentMethod', backref='customer', lazy='dynamic')
    # Removed rides relationship since it's handled at the User level
    
    def __repr__(self):
        return f'<CustomerProfile of {self.user.username}>'

class RiderProfile(db.Model):
    __tablename__ = 'rider_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    license_number = db.Column(db.String(50), unique=True)
    is_available = db.Column(db.Boolean, default=False)
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    last_location_update = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=5.0)
    total_earnings = db.Column(db.Float, default=0.0)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    # Removed rides relationship since it's handled at the User level
    
    def __repr__(self):
        return f'<RiderProfile of {self.user.username}>' 