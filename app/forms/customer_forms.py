from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, DateTimeField, HiddenField, FloatField, TextAreaField, IntegerField, RadioField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class PaymentMethodForm(FlaskForm):
    payment_type = SelectField('Payment Type', choices=[
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal')
    ], validators=[DataRequired()])
    card_number = StringField('Card Number', validators=[Optional(), Length(min=13, max=19)])
    card_expiry = StringField('Expiry Date (MM/YYYY)', validators=[Optional(), Length(min=7, max=7)])
    card_holder_name = StringField('Card Holder Name', validators=[Optional(), Length(max=100)])
    is_default = BooleanField('Set as Default Payment Method')
    submit = SubmitField('Add Payment Method')

    def validate(self):
        if not super(PaymentMethodForm, self).validate():
            return False
        
        # If payment type is credit or debit card, card details are required
        if self.payment_type.data in ['credit_card', 'debit_card']:
            if not self.card_number.data:
                self.card_number.errors = ["Card number is required for credit/debit card payments."]
                return False
            if not self.card_expiry.data:
                self.card_expiry.errors = ["Expiry date is required for credit/debit card payments."]
                return False
            if not self.card_holder_name.data:
                self.card_holder_name.errors = ["Card holder name is required for credit/debit card payments."]
                return False
                
        return True

class RideRequestForm(FlaskForm):
    pickup_address = StringField('Pickup Address', validators=[DataRequired()])
    destination_address = StringField('Destination Address', validators=[DataRequired()])

    # Hidden fields for coordinates - these are set via JavaScript
    # We don't include validators here since we'll handle validation manually
    pickup_latitude = HiddenField()
    pickup_longitude = HiddenField()
    destination_latitude = HiddenField()
    destination_longitude = HiddenField()

    # Custom coerce function to handle empty values
    def coerce_vehicle_type(value):
        if value == '':
            return None
        return int(value)

    vehicle_type = SelectField('Vehicle Type', coerce=coerce_vehicle_type, validators=[DataRequired()])

    is_scheduled = BooleanField('Schedule for Later')
    scheduled_time = DateTimeField('Scheduled Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])

    submit = SubmitField('Request Ride')

class ReviewForm(FlaskForm):
    rating = RadioField(
        'Rating (1-5)',
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[DataRequired()],
        coerce=int
    )
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Review')