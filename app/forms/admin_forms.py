from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from datetime import datetime

class VehicleForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired(), Length(min=2, max=100)])
    model = StringField('Model', validators=[DataRequired(), Length(min=2, max=100)])
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
    color = StringField('Color', validators=[DataRequired(), Length(min=2, max=50)])
    is_active = BooleanField('Active', default=True)
    base_fare = FloatField('Base Fare', validators=[DataRequired(), NumberRange(min=0)])
    per_km_rate = FloatField('Per Kilometer Rate', validators=[DataRequired(), NumberRange(min=0)])
    per_minute_rate = FloatField('Per Minute Rate', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Vehicle')

class VehicleMaintenanceForm(FlaskForm):
    maintenance_type = SelectField('Maintenance Type', choices=[
        ('oil_change', 'Oil Change'),
        ('tire_replacement', 'Tire Replacement'),
        ('brake_service', 'Brake Service'),
        ('inspection', 'Inspection'),
        ('repair', 'Repair'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    cost = FloatField('Cost', validators=[DataRequired(), NumberRange(min=0)])
    service_date = DateField('Service Date', validators=[DataRequired()], default=datetime.utcnow)
    next_service_date = DateField('Next Service Date (if applicable)', validators=[Optional()])
    submit = SubmitField('Add Maintenance Log') 