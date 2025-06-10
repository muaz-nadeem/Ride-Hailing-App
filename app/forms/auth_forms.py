from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class RiderRegistrationForm(RegistrationForm):
    license_number = StringField('Driver License Number', validators=[DataRequired(), Length(min=5, max=50)])
    
    # Vehicle information
    make = StringField('Vehicle Make', validators=[DataRequired(), Length(min=2, max=100)])
    model = StringField('Vehicle Model', validators=[DataRequired(), Length(min=2, max=100)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    license_plate = StringField('License Plate', validators=[DataRequired(), Length(min=3, max=20)])
    vehicle_type = SelectField('Vehicle Type', choices=[
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('luxury', 'Luxury'),
        ('compact', 'Compact'),
        ('van', 'Van')
    ], validators=[DataRequired()])
    capacity = IntegerField('Passenger Capacity', validators=[DataRequired(), NumberRange(min=1, max=10)])
    color = StringField('Vehicle Color', validators=[DataRequired(), Length(min=2, max=50)])
    base_fare = FloatField('Base Fare (PKR)', validators=[DataRequired(), NumberRange(min=0)])
    per_km_rate = FloatField('Per Kilometer Rate (PKR)', validators=[DataRequired(), NumberRange(min=0)])
    per_minute_rate = FloatField('Per Minute Rate (PKR)', validators=[DataRequired(), NumberRange(min=0)])
    
    submit = SubmitField('Sign Up as Driver')

    def validate_license_number(self, license_number):
        from app.models.user import RiderProfile
        rider = RiderProfile.query.filter_by(license_number=license_number.data).first()
        if rider:
            raise ValidationError('This license number is already registered. Please contact support if this is a mistake.')
            
    def validate_license_plate(self, license_plate):
        from app.models.vehicle import Vehicle
        vehicle = Vehicle.query.filter_by(license_plate=license_plate.data).first()
        if vehicle:
            raise ValidationError('This license plate is already registered. Please use a different one.') 