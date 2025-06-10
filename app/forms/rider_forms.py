from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

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
    base_fare = FloatField('Base Fare', validators=[DataRequired(), NumberRange(min=0)])
    per_km_rate = FloatField('Per Kilometer Rate', validators=[DataRequired(), NumberRange(min=0)])
    per_minute_rate = FloatField('Per Minute Rate', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Vehicle')
