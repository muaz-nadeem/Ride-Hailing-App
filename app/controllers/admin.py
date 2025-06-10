from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.models.user import User, RiderProfile, CustomerProfile
from app.models.ride import Ride, Review
from app.models.vehicle import Vehicle, VehicleMaintenanceLog
from app.forms.admin_forms import VehicleForm, VehicleMaintenanceForm
from app.utils.decorators import admin_required
from datetime import datetime, timedelta
from sqlalchemy import func

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get counts for dashboard
    total_customers = User.query.filter_by(user_type='customer').count()
    total_riders = User.query.filter_by(user_type='rider').count()
    total_vehicles = Vehicle.query.count()
    
    # Get active riders (available and approved)
    active_riders = RiderProfile.query.filter_by(is_available=True, approved=True).count()
    
    # Get pending rider applications
    pending_applications = RiderProfile.query.filter_by(approved=False).count()
    
    # Get rides statistics
    total_rides = Ride.query.count()
    completed_rides = Ride.query.filter_by(status='completed').count()
    
    # Get today's rides
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(tomorrow, datetime.min.time())
    
    todays_rides = Ride.query.filter(Ride.created_at >= today_start, Ride.created_at < today_end).count()
    
    # Get today's revenue
    todays_revenue = db.session.query(func.sum(Ride.final_fare)).filter(
        Ride.completed_at >= today_start,
        Ride.completed_at < today_end,
        Ride.payment_status == 'completed'
    ).scalar() or 0
    
    # Get recent rides for quick view
    recent_rides = Ride.query.order_by(Ride.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                          total_customers=total_customers,
                          total_riders=total_riders,
                          total_vehicles=total_vehicles,
                          active_riders=active_riders,
                          pending_applications=pending_applications,
                          total_rides=total_rides,
                          completed_rides=completed_rides,
                          todays_rides=todays_rides,
                          todays_revenue=todays_revenue,
                          recent_rides=recent_rides)

@admin.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    if request.method == 'POST':
        # Update user information
        current_user.phone = request.form.get('phone')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('admin.profile'))
        
    return render_template('admin/profile.html', title='Admin Profile')

@admin.route('/vehicles')
@login_required
@admin_required
def vehicles():
    vehicles = Vehicle.query.all()
    return render_template('admin/vehicles/index.html', title='Vehicles', vehicles=vehicles)

@admin.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_vehicle():
    form = VehicleForm()
    
    if form.validate_on_submit():
        vehicle = Vehicle(
            make=form.make.data,
            model=form.model.data,
            year=form.year.data,
            license_plate=form.license_plate.data,
            vehicle_type=form.vehicle_type.data,
            capacity=form.capacity.data,
            color=form.color.data,
            is_active=form.is_active.data,
            base_fare=form.base_fare.data,
            per_km_rate=form.per_km_rate.data,
            per_minute_rate=form.per_minute_rate.data
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        flash('Vehicle added successfully', 'success')
        return redirect(url_for('admin.vehicles'))
    
    return render_template('admin/vehicles/add.html', title='Add Vehicle', form=form)

@admin.route('/vehicles/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = VehicleForm(obj=vehicle)
    
    if form.validate_on_submit():
        vehicle.make = form.make.data
        vehicle.model = form.model.data
        vehicle.year = form.year.data
        vehicle.license_plate = form.license_plate.data
        vehicle.vehicle_type = form.vehicle_type.data
        vehicle.capacity = form.capacity.data
        vehicle.color = form.color.data
        vehicle.is_active = form.is_active.data
        vehicle.base_fare = form.base_fare.data
        vehicle.per_km_rate = form.per_km_rate.data
        vehicle.per_minute_rate = form.per_minute_rate.data
        
        db.session.commit()
        
        flash('Vehicle updated successfully', 'success')
        return redirect(url_for('admin.vehicles'))
    
    return render_template('admin/vehicles/edit.html', title='Edit Vehicle', form=form, vehicle=vehicle)

@admin.route('/vehicle_maintenance/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def vehicle_maintenance(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = VehicleMaintenanceForm()
    
    if form.validate_on_submit():
        maintenance = VehicleMaintenanceLog(
            vehicle_id=vehicle_id,
            maintenance_type=form.maintenance_type.data,
            description=form.description.data,
            cost=form.cost.data,
            service_date=form.service_date.data,
            next_service_date=form.next_service_date.data
        )
        
        db.session.add(maintenance)
        db.session.commit()
        
        flash('Maintenance log added successfully', 'success')
        return redirect(url_for('admin.vehicle_details', vehicle_id=vehicle_id))
    
    maintenance_logs = VehicleMaintenanceLog.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleMaintenanceLog.service_date.desc()).all()
    
    return render_template('admin/vehicles/maintenance.html', title='Vehicle Maintenance', 
                          vehicle=vehicle, form=form, maintenance_logs=maintenance_logs)

@admin.route('/vehicle_details/<int:vehicle_id>')
@login_required
@admin_required
def vehicle_details(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    maintenance_logs = VehicleMaintenanceLog.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleMaintenanceLog.service_date.desc()).all()
    
    # Get rider assigned to this vehicle
    rider = vehicle.rider
    
    # Get recent rides with this vehicle
    recent_rides = Ride.query.filter_by(vehicle_id=vehicle_id).order_by(Ride.created_at.desc()).limit(5).all()
    
    return render_template('admin/vehicles/details.html', title='Vehicle Details', 
                          vehicle=vehicle, maintenance_logs=maintenance_logs, 
                          rider=rider, recent_rides=recent_rides)

@admin.route('/riders')
@login_required
@admin_required
def riders():
    riders = User.query.filter_by(user_type='rider').all()
    
    # Get all available vehicles for assignment
    available_vehicles = Vehicle.query.filter_by(is_active=True).all()
    
    return render_template('admin/riders/index.html', title='Riders', riders=riders, vehicles=available_vehicles)

@admin.route('/approve_rider_form/<int:rider_id>')
@login_required
@admin_required
def approve_rider_form(rider_id):
    """Show a dedicated page for approving a rider instead of using modals"""
    rider = User.query.get_or_404(rider_id)
    
    if rider.user_type != 'rider':
        flash('User is not a rider', 'danger')
        return redirect(url_for('admin.riders'))
    
    rider_profile = RiderProfile.query.filter_by(user_id=rider_id).first()
    
    if rider_profile.approved:
        flash('Rider is already approved', 'info')
        return redirect(url_for('admin.rider_details', rider_id=rider_id))
    
    # Get all available vehicles for assignment (excluding any already assigned to this rider)
    available_vehicles = Vehicle.query.filter_by(is_active=True).all()
    
    # Ensure rider's vehicle (if exists) is also included in the options
    # This is important because the vehicle might be technically assigned but rider isn't approved yet
    
    return render_template('admin/riders/approve_form.html', title='Approve Driver', 
                          rider=rider, profile=rider_profile, vehicles=available_vehicles)

@admin.route('/rider_details/<int:rider_id>')
@login_required
@admin_required
def rider_details(rider_id):
    rider = User.query.get_or_404(rider_id)
    
    if rider.user_type != 'rider':
        flash('User is not a rider', 'danger')
        return redirect(url_for('admin.riders'))
    
    rider_profile = RiderProfile.query.filter_by(user_id=rider_id).first()
    
    # Get vehicle assigned to this rider
    vehicle = rider_profile.vehicle if rider_profile else None
    
    # Get recent rides by this rider
    recent_rides = Ride.query.filter_by(rider_id=rider_id).order_by(Ride.created_at.desc()).limit(5).all()
    
    # Get reviews for this rider
    reviews = Review.query.filter_by(rider_id=rider_id).order_by(Review.created_at.desc()).all()
    
    # Get all available vehicles for assignment
    vehicles = Vehicle.query.filter_by(is_active=True).all()
    
    return render_template('admin/riders/details.html', title='Rider Details', 
                          rider=rider, profile=rider_profile, vehicle=vehicle,
                          recent_rides=recent_rides, reviews=reviews, vehicles=vehicles)

@admin.route('/approve_rider/<int:rider_id>', methods=['POST'])
@login_required
@admin_required
def approve_rider(rider_id):
    rider_profile = RiderProfile.query.filter_by(user_id=rider_id).first_or_404()
    
    if rider_profile.approved:
        flash('Rider is already approved', 'info')
        return redirect(url_for('admin.rider_details', rider_id=rider_id))
    
    vehicle_id = request.form.get('vehicle_id')
    
    if not vehicle_id:
        flash('Please select a vehicle to assign to this rider', 'danger')
        return redirect(url_for('admin.rider_details', rider_id=rider_id))
    
    # Update rider profile
    rider_profile.approved = True
    rider_profile.vehicle_id = vehicle_id
    
    db.session.commit()
    
    flash('Rider approved successfully', 'success')
    return redirect(url_for('admin.rider_details', rider_id=rider_id))

@admin.route('/reject_rider/<int:rider_id>', methods=['POST'])
@login_required
@admin_required
def reject_rider(rider_id):
    rider = User.query.get_or_404(rider_id)
    rider_profile = RiderProfile.query.filter_by(user_id=rider_id).first_or_404()
    
    # In a real application, you might want to send an email notification
    # or keep a record of rejected applications
    
    # Delete rider account
    db.session.delete(rider_profile)
    db.session.delete(rider)
    db.session.commit()
    
    flash('Rider application rejected', 'success')
    return redirect(url_for('admin.riders'))

@admin.route('/customers')
@login_required
@admin_required
def customers():
    customers = User.query.filter_by(user_type='customer').all()
    return render_template('admin/customers/index.html', title='Customers', customers=customers)

@admin.route('/customer_details/<int:customer_id>')
@login_required
@admin_required
def customer_details(customer_id):
    customer = User.query.get_or_404(customer_id)
    
    if customer.user_type != 'customer':
        flash('User is not a customer', 'danger')
        return redirect(url_for('admin.customers'))
    
    customer_profile = CustomerProfile.query.filter_by(user_id=customer_id).first()
    
    # Get recent rides by this customer
    recent_rides = Ride.query.filter_by(customer_id=customer_id).order_by(Ride.created_at.desc()).limit(10).all()
    
    # Get payment methods
    payment_methods = customer_profile.payment_methods.all() if customer_profile else []
    
    # Get reviews given by this customer
    reviews = Review.query.filter_by(customer_id=customer_id).order_by(Review.created_at.desc()).all()
    
    return render_template('admin/customers/details.html', title='Customer Details', 
                          customer=customer, profile=customer_profile, 
                          recent_rides=recent_rides, payment_methods=payment_methods,
                          reviews=reviews)

@admin.route('/rides')
@login_required
@admin_required
def rides():
    # Filter by status if provided
    status = request.args.get('status', 'all')
    
    if status != 'all':
        rides = Ride.query.filter_by(status=status).order_by(Ride.created_at.desc()).all()
    else:
        rides = Ride.query.order_by(Ride.created_at.desc()).all()
    
    return render_template('admin/rides/index.html', title='Rides', rides=rides, current_status=status)

@admin.route('/ride_details/<int:ride_id>')
@login_required
@admin_required
def ride_details(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    
    return render_template('admin/rides/details.html', title='Ride Details', ride=ride)

@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    # Revenue statistics
    total_revenue = db.session.query(func.sum(Ride.final_fare)).filter(
        Ride.payment_status == 'completed'
    ).scalar() or 0
    
    # Get revenue by day for the last 30 days
    today = datetime.utcnow().date()
    thirty_days_ago = today - timedelta(days=30)
    
    daily_revenue = db.session.query(
        func.date(Ride.completed_at).label('date'),
        func.sum(Ride.final_fare).label('revenue')
    ).filter(
        Ride.completed_at >= thirty_days_ago,
        Ride.payment_status == 'completed'
    ).group_by(func.date(Ride.completed_at)).all()
    
    # Format for chart display
    revenue_dates = [str(day.date) for day in daily_revenue]
    revenue_values = [float(day.revenue) for day in daily_revenue]
    
    # Ride statistics
    ride_stats = db.session.query(
        Ride.status,
        func.count(Ride.id).label('count')
    ).group_by(Ride.status).all()
    
    status_labels = [stat.status for stat in ride_stats]
    status_values = [stat.count for stat in ride_stats]
    
    # Top performing riders
    top_riders = db.session.query(
        User.id,
        User.username,
        func.count(Ride.id).label('ride_count'),
        func.sum(Ride.final_fare).label('earnings')
    ).join(
        Ride, Ride.rider_id == User.id
    ).filter(
        Ride.status == 'completed',
        Ride.payment_status == 'completed'
    ).group_by(User.id).order_by(func.sum(Ride.final_fare).desc()).limit(5).all()
    
    return render_template('admin/analytics.html', title='Analytics',
                          total_revenue=total_revenue,
                          revenue_dates=revenue_dates,
                          revenue_values=revenue_values,
                          status_labels=status_labels,
                          status_values=status_values,
                          top_riders=top_riders)

@admin.route('/disputes')
@login_required
@admin_required
def disputes():
    # In a real application, this might be implemented as a separate model
    # For simplicity, we'll show rides with low ratings as potential disputes
    potential_disputes = db.session.query(
        Ride, Review
    ).join(
        Review, Review.ride_id == Ride.id
    ).filter(
        Review.rating <= 2
    ).order_by(Review.created_at.desc()).all()
    
    return render_template('admin/disputes.html', title='Disputes', disputes=potential_disputes) 