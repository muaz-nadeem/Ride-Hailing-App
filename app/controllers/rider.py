from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.user import User, RiderProfile
from app.models.ride import Ride, Review
from app.models.vehicle import Vehicle
from app.forms.rider_forms import VehicleForm
from app.utils.decorators import rider_required
from datetime import datetime

rider = Blueprint('rider', __name__)

@rider.route('/manage_vehicle', methods=['GET', 'POST'])
@login_required
@rider_required
def manage_vehicle():
    """Allow riders to add or edit their vehicle"""
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()
    
    # Check if rider is approved
    if not rider_profile.approved:
        # Redirect to pending approval page
        return render_template('rider/pending_approval.html', title='Approval Pending')

    # Get current vehicle if exists
    current_vehicle = None
    if rider_profile.vehicle_id:
        current_vehicle = Vehicle.query.get(rider_profile.vehicle_id)

    form = VehicleForm()

    # If form is submitted and valid
    if form.validate_on_submit():
        if current_vehicle:
            # Update existing vehicle
            current_vehicle.make = form.make.data
            current_vehicle.model = form.model.data
            current_vehicle.year = form.year.data
            current_vehicle.license_plate = form.license_plate.data
            current_vehicle.vehicle_type = form.vehicle_type.data
            current_vehicle.capacity = form.capacity.data
            current_vehicle.color = form.color.data
            current_vehicle.base_fare = form.base_fare.data
            current_vehicle.per_km_rate = form.per_km_rate.data
            current_vehicle.per_minute_rate = form.per_minute_rate.data
        else:
            # Create new vehicle
            new_vehicle = Vehicle(
                make=form.make.data,
                model=form.model.data,
                year=form.year.data,
                license_plate=form.license_plate.data,
                vehicle_type=form.vehicle_type.data,
                capacity=form.capacity.data,
                color=form.color.data,
                base_fare=form.base_fare.data,
                per_km_rate=form.per_km_rate.data,
                per_minute_rate=form.per_minute_rate.data,
                is_active=True
            )
            db.session.add(new_vehicle)
            db.session.flush()  # Get the ID without committing

            # Assign vehicle to rider
            rider_profile.vehicle_id = new_vehicle.id

        db.session.commit()
        flash('Vehicle information saved successfully', 'success')
        return redirect(url_for('rider.dashboard'))

    # Pre-populate form with existing vehicle data
    if current_vehicle and request.method == 'GET':
        form.make.data = current_vehicle.make
        form.model.data = current_vehicle.model
        form.year.data = current_vehicle.year
        form.license_plate.data = current_vehicle.license_plate
        form.vehicle_type.data = current_vehicle.vehicle_type
        form.capacity.data = current_vehicle.capacity
        form.color.data = current_vehicle.color
        form.base_fare.data = current_vehicle.base_fare
        form.per_km_rate.data = current_vehicle.per_km_rate
        form.per_minute_rate.data = current_vehicle.per_minute_rate

    return render_template('rider/manage_vehicle.html', title='Manage Vehicle', form=form, vehicle=current_vehicle)

@rider.route('/dashboard')
@login_required
@rider_required
def dashboard():
    # Get rider profile
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()

    # Check if rider is approved
    if not rider_profile.approved:
        # Redirect to pending approval page
        return render_template('rider/pending_approval.html', title='Approval Pending')

    # Get current/active ride
    active_ride = Ride.query.filter_by(
        rider_id=current_user.id
    ).filter(Ride.status.in_(['accepted', 'in_progress'])).first()

    # Get pending ride requests
    pending_rides = Ride.query.filter_by(
        status='requested'
    ).order_by(Ride.created_at).all()

    # Get recent completed rides
    recent_rides = Ride.query.filter_by(
        rider_id=current_user.id,
        status='completed'
    ).order_by(Ride.completed_at.desc()).limit(5).all()

    return render_template('rider/dashboard.html', title='Rider Dashboard',
                          rider_profile=rider_profile, active_ride=active_ride,
                          pending_rides=pending_rides, recent_rides=recent_rides)

@rider.route('/profile', methods=['GET', 'POST'])
@login_required
@rider_required
def profile():
    # Get rider profile
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        # Update profile information
        current_user.phone = request.form.get('phone')

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('rider.profile'))

    return render_template('rider/profile.html', title='Profile', profile=rider_profile)

@rider.route('/toggle_availability', methods=['POST'])
@login_required
@rider_required
def toggle_availability():
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()

    # Check if rider is approved
    if not rider_profile.approved:
        flash('Your account is not approved yet', 'danger')
        return redirect(url_for('rider.dashboard'))

    rider_profile.is_available = not rider_profile.is_available
    db.session.commit()

    availability = "available" if rider_profile.is_available else "unavailable"
    flash(f'You are now {availability} for new rides', 'success')
    return redirect(url_for('rider.dashboard'))

@rider.route('/update_location', methods=['POST'])
@login_required
@rider_required
def update_location():
    data = request.get_json()

    latitude = data.get('latitude')
    longitude = data.get('longitude')

    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()
    rider_profile.current_latitude = latitude
    rider_profile.current_longitude = longitude
    rider_profile.last_location_update = datetime.utcnow()

    db.session.commit()

    return jsonify({'success': True})

@rider.route('/ride/<int:ride_id>')
@login_required
@rider_required
def ride_details(ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Make sure this ride belongs to the current rider or is a pending request
    if ride.rider_id != current_user.id and ride.status != 'requested':
        flash('You do not have permission to view this ride', 'danger')
        return redirect(url_for('rider.dashboard'))

    # Get rider profile for location data
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()

    return render_template('rider/ride_details.html', title='Ride Details', ride=ride, rider_profile=rider_profile)

@rider.route('/accept_ride/<int:ride_id>', methods=['POST'])
@login_required
@rider_required
def accept_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()

    # Check if rider is approved
    if not rider_profile.approved:
        flash('You cannot accept rides until your account is approved by an administrator', 'danger')
        return redirect(url_for('rider.dashboard'))

    if not rider_profile.is_available:
        flash('You need to set your status to available before accepting rides', 'danger')
        return redirect(url_for('rider.dashboard'))

    # Check if ride is still in requested status
    if ride.status != 'requested':
        flash('This ride is no longer available', 'danger')
        return redirect(url_for('rider.dashboard'))

    # Check if rider already has an active ride
    active_ride = Ride.query.filter_by(
        rider_id=current_user.id
    ).filter(Ride.status.in_(['accepted', 'in_progress'])).first()

    if active_ride:
        flash('You already have an active ride', 'danger')
        return redirect(url_for('rider.dashboard'))

    # Accept the ride
    ride.rider_id = current_user.id
    ride.status = 'accepted'
    ride.accepted_at = datetime.utcnow()

    db.session.commit()

    flash('Ride accepted successfully', 'success')
    return redirect(url_for('rider.ride_details', ride_id=ride_id))

@rider.route('/start_ride/<int:ride_id>', methods=['POST'])
@login_required
@rider_required
def start_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Make sure this ride belongs to the current rider
    if ride.rider_id != current_user.id:
        flash('You do not have permission to update this ride', 'danger')
        return redirect(url_for('rider.dashboard'))

    # Check if ride is in accepted status
    if ride.status != 'accepted':
        flash('Ride can only be started if it has been accepted', 'danger')
        return redirect(url_for('rider.ride_details', ride_id=ride_id))

    # Start the ride
    ride.status = 'in_progress'
    ride.started_at = datetime.utcnow()

    db.session.commit()

    flash('Ride started successfully', 'success')
    return redirect(url_for('rider.ride_details', ride_id=ride_id))

@rider.route('/complete_ride/<int:ride_id>', methods=['POST'])
@login_required
@rider_required
def complete_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Make sure this ride belongs to the current rider
    if ride.rider_id != current_user.id:
        flash('You do not have permission to update this ride', 'danger')
        return redirect(url_for('rider.dashboard'))

    # Check if ride is in in_progress status
    if ride.status != 'in_progress':
        flash('Ride can only be completed if it is in progress', 'danger')
        return redirect(url_for('rider.ride_details', ride_id=ride_id))

    # Complete the ride
    ride.status = 'completed'
    ride.completed_at = datetime.utcnow()

    # Set final fare (in a real app, this might be adjusted based on actual distance/time)
    ride.final_fare = ride.estimated_fare

    db.session.commit()

    # Send notification to customer about payment (in a real app, this would be an email or push notification)
    # For now, we'll just flash a message to the driver
    flash('Ride completed successfully. The customer has been notified to make payment.', 'success')

    return redirect(url_for('rider.dashboard'))

@rider.route('/earnings')
@login_required
@rider_required
def earnings():
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()

    # Get all completed rides
    completed_rides = Ride.query.filter_by(
        rider_id=current_user.id,
        status='completed'
    ).order_by(Ride.completed_at.desc()).all()

    # Calculate statistics
    total_earnings = rider_profile.total_earnings
    completed_count = len(completed_rides)
    avg_rating = rider_profile.rating

    # Count pending payments
    pending_payments_count = sum(1 for ride in completed_rides if ride.payment_status == 'pending')

    # Calculate earnings by period (last 7 days, last 30 days)
    from datetime import timedelta
    today = datetime.utcnow()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)

    earnings_7_days = sum([ride.final_fare or ride.estimated_fare for ride in completed_rides
                          if ride.completed_at and ride.completed_at > last_7_days and ride.payment_status == 'completed'])

    earnings_30_days = sum([ride.final_fare or ride.estimated_fare for ride in completed_rides
                           if ride.completed_at and ride.completed_at > last_30_days and ride.payment_status == 'completed'])

    return render_template('rider/earnings.html', title='Earnings',
                          total_earnings=total_earnings,
                          completed_count=completed_count,
                          avg_rating=avg_rating,
                          earnings_7_days=earnings_7_days,
                          earnings_30_days=earnings_30_days,
                          completed_rides=completed_rides,
                          pending_payments_count=pending_payments_count)

@rider.route('/reviews')
@login_required
@rider_required
def reviews():
    # Get all reviews for this rider
    reviews = Review.query.filter_by(rider_id=current_user.id).order_by(Review.created_at.desc()).all()

    return render_template('rider/reviews.html', title='My Reviews', reviews=reviews)

@rider.route('/check_new_rides', methods=['GET'])
@login_required
@rider_required
def check_new_rides():
    """API endpoint to check for new ride requests"""
    # Only check for rides if rider is approved and available
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()

    if not rider_profile or not rider_profile.approved or not rider_profile.is_available:
        return jsonify({
            'has_new_rides': False,
            'count': 0
        })

    # Check if rider already has an active ride
    active_ride = Ride.query.filter_by(
        rider_id=current_user.id
    ).filter(Ride.status.in_(['accepted', 'in_progress'])).first()

    if active_ride:
        return jsonify({
            'has_new_rides': False,
            'count': 0
        })

    # Count pending ride requests
    count = Ride.query.filter_by(status='requested').count()

    return jsonify({
        'has_new_rides': count > 0,
        'count': count
    })

@rider.route('/pending_rides', methods=['GET'])
@login_required
@rider_required
def pending_rides():
    """API endpoint to get pending ride requests HTML"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('rider.dashboard'))

    # Get rider profile
    rider_profile = RiderProfile.query.filter_by(user_id=current_user.id).first()

    # If rider not available (approval check removed)
    if not rider_profile or not rider_profile.is_available:
        return jsonify({
            'success': False,
            'message': 'Rider not available'
        })

    # Check if rider already has an active ride
    active_ride = Ride.query.filter_by(
        rider_id=current_user.id
    ).filter(Ride.status.in_(['accepted', 'in_progress'])).first()

    if active_ride:
        return jsonify({
            'success': False,
            'message': 'You already have an active ride'
        })

    # Get pending ride requests
    pending_rides = Ride.query.filter_by(
        status='requested'
    ).order_by(Ride.created_at).all()

    # Render partial template
    html = render_template('rider/partials/pending_rides.html', pending_rides=pending_rides)

    return jsonify({
        'success': True,
        'html': html
    })