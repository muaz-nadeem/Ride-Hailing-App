from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.user import User, CustomerProfile
from app.models.ride import Ride, Review, PaymentMethod
from app.models.vehicle import Vehicle
from app.forms.customer_forms import PaymentMethodForm, RideRequestForm, ReviewForm
from app.utils.decorators import customer_required
from app.utils.helpers import calculate_distance, estimate_time, calculate_fare, apply_surge_pricing
from datetime import datetime

customer = Blueprint('customer', __name__)

@customer.route('/dashboard')
@login_required
@customer_required
def dashboard():
    # Get active and past rides
    active_rides = Ride.query.filter_by(
        customer_id=current_user.id
    ).filter(Ride.status.in_(['requested', 'accepted', 'in_progress'])).order_by(Ride.created_at.desc()).all()

    past_rides = Ride.query.filter_by(
        customer_id=current_user.id
    ).filter(Ride.status.in_(['completed', 'cancelled'])).order_by(Ride.created_at.desc()).limit(5).all()

    return render_template('customer/dashboard.html', title='Customer Dashboard',
                          active_rides=active_rides, past_rides=past_rides)

@customer.route('/profile', methods=['GET', 'POST'])
@login_required
@customer_required
def profile():
    # Get customer profile
    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        # Update profile information
        customer_profile.home_address = request.form.get('home_address')
        customer_profile.work_address = request.form.get('work_address')

        # Update user information
        current_user.phone = request.form.get('phone')

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('customer.profile'))

    return render_template('customer/profile.html', title='Profile', profile=customer_profile)

@customer.route('/rides')
@login_required
@customer_required
def rides():
    # Get all customer rides ordered by most recent first
    all_rides = Ride.query.filter_by(customer_id=current_user.id).order_by(Ride.created_at.desc()).all()

    return render_template('customer/rides.html', title='My Rides', rides=all_rides)

@customer.route('/payment_methods', methods=['GET'])
@login_required
@customer_required
def payment_methods():
    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
    payment_methods = PaymentMethod.query.filter_by(customer_id=customer_profile.id).all()

    return render_template('customer/payment_methods.html', title='Payment Methods',
                          payment_methods=payment_methods)

@customer.route('/add_payment_method', methods=['GET', 'POST'])
@login_required
@customer_required
def add_payment_method():
    form = PaymentMethodForm()
    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()

    if form.validate_on_submit():
        # Check if this should be the default payment method
        if form.is_default.data:
            # Set all other payment methods to not default
            PaymentMethod.query.filter_by(customer_id=customer_profile.id, is_default=True).update({'is_default': False})
            db.session.commit()

        payment_method = PaymentMethod(
            customer_id=customer_profile.id,
            payment_type=form.payment_type.data,
            card_number=form.card_number.data,
            card_expiry=form.card_expiry.data,
            card_holder_name=form.card_holder_name.data,
            is_default=form.is_default.data
        )

        db.session.add(payment_method)
        db.session.commit()

        flash('Payment method added successfully', 'success')
        return redirect(url_for('customer.payment_methods'))

    return render_template('customer/add_payment_method.html', title='Add Payment Method', form=form)

@customer.route('/book_ride', methods=['GET', 'POST'])
@login_required
@customer_required
def book_ride():
    form = RideRequestForm()

    # Populate vehicle types with detailed information
    vehicles = Vehicle.query.filter_by(is_active=True).all()
    # Add an empty default option
    vehicle_choices = [('', 'Select a vehicle type')] + [(v.id, f"{v.make} {v.model} ({v.vehicle_type} - {v.color})") for v in vehicles]
    form.vehicle_type.choices = vehicle_choices

    if request.method == 'POST':
        # Debug information
        print(f"Form data: {request.form}")
        print(f"Vehicle type: {request.form.get('vehicle_type')}")

        # Get all values from the form for each field (some fields appear multiple times)
        pickup_lat_values = request.form.getlist('pickup_latitude')
        pickup_lng_values = request.form.getlist('pickup_longitude')
        dest_lat_values = request.form.getlist('destination_latitude')
        dest_lng_values = request.form.getlist('destination_longitude')

        # Use the last non-empty value for each coordinate
        pickup_lat = next((val for val in reversed(pickup_lat_values) if val), None)
        pickup_lng = next((val for val in reversed(pickup_lng_values) if val), None)
        dest_lat = next((val for val in reversed(dest_lat_values) if val), None)
        dest_lng = next((val for val in reversed(dest_lng_values) if val), None)

        print(f"Extracted pickup coordinates: {pickup_lat}, {pickup_lng}")
        print(f"Extracted destination coordinates: {dest_lat}, {dest_lng}")

        # Manually validate the form to handle the coordinates properly
        is_valid = True
        errors = {}

        # Validate pickup coordinates
        if not pickup_lat or not pickup_lng or pickup_lat == 'None' or pickup_lng == 'None':
            is_valid = False
            errors['pickup_coordinates'] = 'Please set pickup location on the map'

        # Validate destination coordinates
        if not dest_lat or not dest_lng or dest_lat == 'None' or dest_lng == 'None':
            is_valid = False
            errors['destination_coordinates'] = 'Please set destination location on the map'

        # Validate vehicle type
        vehicle_type = request.form.get('vehicle_type')
        if not vehicle_type:
            is_valid = False
            errors['vehicle_type'] = 'Please select a vehicle type'

        # If scheduled, validate time
        if request.form.get('is_scheduled') == 'y' and not request.form.get('scheduled_time'):
            is_valid = False
            errors['scheduled_time'] = 'Please set a scheduled time for your ride'

        if is_valid:
            # Calculate distance and estimated time
            distance = calculate_distance(float(pickup_lat), float(pickup_lng), float(dest_lat), float(dest_lng))
            estimated_time = estimate_time(distance)

            # Calculate fare
            vehicle_id = int(vehicle_type)  # We already validated that vehicle_type exists
            estimated_fare = calculate_fare(vehicle_id, distance, estimated_time)
            # Apply surge pricing if applicable
            estimated_fare = apply_surge_pricing(estimated_fare)

            # Create new ride
            ride = Ride(
                customer_id=current_user.id,
                vehicle_id=vehicle_id,
                pickup_address=request.form.get('pickup_address'),
                destination_address=request.form.get('destination_address'),
                pickup_latitude=float(pickup_lat),
                pickup_longitude=float(pickup_lng),
                destination_latitude=float(dest_lat),
                destination_longitude=float(dest_lng),
                estimated_fare=estimated_fare,
                status='requested',
                is_scheduled=request.form.get('is_scheduled') == 'y',
                scheduled_time=form.scheduled_time.data if request.form.get('is_scheduled') == 'y' else None
            )

            db.session.add(ride)
            db.session.commit()

            flash('Ride requested successfully', 'success')
            return redirect(url_for('customer.dashboard'))
        else:
            # Flash errors
            for error in errors.values():
                flash(error, 'danger')

    return render_template('customer/book_ride.html', title='Book a Ride', form=form)

@customer.route('/calculate_fare', methods=['POST'])
@login_required
@customer_required
def calculate_fare_api():
    data = request.get_json()

    pickup_lat = data.get('pickup_latitude')
    pickup_lng = data.get('pickup_longitude')
    dest_lat = data.get('destination_latitude')
    dest_lng = data.get('destination_longitude')
    vehicle_id = data.get('vehicle_type')

    # Calculate distance and estimated time
    distance = calculate_distance(pickup_lat, pickup_lng, dest_lat, dest_lng)
    estimated_time = estimate_time(distance)

    # Calculate fare
    estimated_fare = calculate_fare(vehicle_id, distance, estimated_time)
    # Apply surge pricing if applicable
    estimated_fare = apply_surge_pricing(estimated_fare)

    return jsonify({
        'distance': round(distance, 2),
        'estimated_time': round(estimated_time, 2),
        'estimated_fare': estimated_fare
    })

@customer.route('/ride/<int:ride_id>')
@login_required
@customer_required
def ride_details(ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Make sure this ride belongs to the current user
    if ride.customer_id != current_user.id:
        flash('You do not have permission to view this ride', 'danger')
        return redirect(url_for('customer.rides'))

    # If ride is completed and payment is pending, show a notification
    if ride.status == 'completed' and ride.payment_status == 'pending':
        flash('This ride requires payment. Please complete the payment to support your driver.', 'warning')

    # Check if auto_pay parameter is set to redirect to payment page
    if request.args.get('auto_pay') == 'true' and ride.status == 'completed' and ride.payment_status == 'pending':
        return redirect(url_for('customer.make_payment', ride_id=ride_id))

    return render_template('customer/ride_details.html', title='Ride Details', ride=ride)

@customer.route('/cancel_ride/<int:ride_id>', methods=['POST'])
@login_required
@customer_required
def cancel_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Make sure this ride belongs to the current user
    if ride.customer_id != current_user.id:
        flash('You do not have permission to cancel this ride', 'danger')
        return redirect(url_for('customer.dashboard'))

    # Can only cancel if ride is in requested or accepted status
    if ride.status not in ['requested', 'accepted']:
        flash('Cannot cancel a ride that is already in progress or completed', 'danger')
        return redirect(url_for('customer.ride_details', ride_id=ride_id))

    ride.status = 'cancelled'
    db.session.commit()

    flash('Ride cancelled successfully', 'success')
    return redirect(url_for('customer.dashboard'))

@customer.route('/ride/<int:ride_id>/review', methods=['GET', 'POST'])
@login_required
@customer_required
def add_review(ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Make sure this ride belongs to the current user
    if ride.customer_id != current_user.id:
        flash('You do not have permission to review this ride', 'danger')
        return redirect(url_for('customer.rides'))

    # Make sure the ride is completed and not already reviewed
    if ride.status != 'completed':
        flash('You can only review completed rides', 'warning')
        return redirect(url_for('customer.ride_details', ride_id=ride_id))

    if ride.review:
        flash('You have already reviewed this ride', 'info')
        return redirect(url_for('customer.ride_details', ride_id=ride_id))

    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(
            ride_id=ride_id,
            customer_id=current_user.id,
            rider_id=ride.rider_id,
            rating=form.rating.data,
            comment=form.comment.data
        )

        # Update rider's average rating
        rider_profile = ride.rider.rider_profile

        # Calculate new average rating
        reviews = Review.query.filter_by(rider_id=ride.rider_id).all()
        total_ratings = sum([r.rating for r in reviews]) + form.rating.data
        new_avg_rating = total_ratings / (len(reviews) + 1)

        rider_profile.rating = new_avg_rating

        db.session.add(review)
        db.session.commit()

        flash('Thank you for your review!', 'success')
        return redirect(url_for('customer.ride_details', ride_id=ride_id))

    return render_template('customer/add_review.html', title='Add Review', ride=ride, form=form)

@customer.route('/make_payment/<int:ride_id>', methods=['GET', 'POST'])
@login_required
@customer_required
def make_payment(ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Make sure this ride belongs to the current user
    if ride.customer_id != current_user.id:
        flash('You do not have permission to make payment for this ride', 'danger')
        return redirect(url_for('customer.dashboard'))

    # Can only make payment for completed rides
    if ride.status != 'completed':
        flash('Can only make payment for completed rides', 'danger')
        return redirect(url_for('customer.ride_details', ride_id=ride_id))

    # Check if payment already made
    if ride.payment_status == 'completed':
        flash('Payment has already been made for this ride', 'info')
        return redirect(url_for('customer.ride_details', ride_id=ride_id))

    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
    payment_methods = PaymentMethod.query.filter_by(customer_id=customer_profile.id).all()

    # Calculate distance and duration for the ride
    distance = calculate_distance(
        ride.pickup_latitude,
        ride.pickup_longitude,
        ride.destination_latitude,
        ride.destination_longitude
    )
    duration = estimate_time(distance)

    if request.method == 'POST':
        payment_method_id = request.form.get('payment_method_id')

        # In a real application, you would process the payment here
        ride.payment_method_id = payment_method_id
        ride.payment_status = 'completed'
        ride.final_fare = ride.estimated_fare  # In a real app, this might be adjusted based on actual ride

        # Update rider's earnings
        rider_profile = ride.rider.rider_profile
        if rider_profile:
            rider_profile.total_earnings += ride.final_fare

        db.session.commit()

        # In a real app, this would send a notification to the driver
        # For now, we'll just flash a success message
        flash('Payment completed successfully! The driver has been notified.', 'success')

        # Redirect to ride details with a success parameter
        return redirect(url_for('customer.ride_details', ride_id=ride_id, payment_success=True))

    return render_template('customer/make_payment.html', title='Make Payment',
                          ride=ride, payment_methods=payment_methods,
                          distance=distance, duration=duration)

@customer.route('/delete_payment_method/<int:payment_id>', methods=['POST'])
@login_required
@customer_required
def delete_payment_method(payment_id):
    payment_method = PaymentMethod.query.get_or_404(payment_id)
    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()

    # Make sure this payment method belongs to the current user
    if payment_method.customer_id != customer_profile.id:
        flash('You do not have permission to delete this payment method', 'danger')
        return redirect(url_for('customer.payment_methods'))

    # If this is the default payment method and there are other methods,
    # set another one as default
    if payment_method.is_default:
        other_method = PaymentMethod.query.filter(
            PaymentMethod.customer_id == customer_profile.id,
            PaymentMethod.id != payment_id
        ).first()

        if other_method:
            other_method.is_default = True

    db.session.delete(payment_method)
    db.session.commit()

    flash('Payment method deleted successfully', 'success')
    return redirect(url_for('customer.payment_methods'))