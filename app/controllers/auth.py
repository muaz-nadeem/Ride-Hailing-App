from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.models.user import User, CustomerProfile, RiderProfile
from app.models.vehicle import Vehicle
from app.forms.auth_forms import LoginForm, RegistrationForm, RiderRegistrationForm
from app.utils.decorators import anonymous_required

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            if user.is_admin():
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.is_rider():
                return redirect(next_page or url_for('rider.dashboard'))
            else:
                return redirect(next_page or url_for('customer.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            user_type='customer'
        )
        user.password = form.password.data

        # Create customer profile
        profile = CustomerProfile(user=user)

        db.session.add(user)
        db.session.add(profile)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/register_rider', methods=['GET', 'POST'])
@anonymous_required
def register_rider():
    form = RiderRegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            user_type='rider'
        )
        user.password = form.password.data

        # Create vehicle
        vehicle = Vehicle(
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

        # Create rider profile - requires admin approval
        profile = RiderProfile(
            user=user,
            license_number=form.license_number.data,
            approved=False  # Set to False to require admin approval
        )

        db.session.add(user)
        db.session.add(vehicle)
        db.session.add(profile)
        db.session.flush()  # Get IDs without committing

        # Link vehicle to rider profile
        profile.vehicle_id = vehicle.id
        
        db.session.commit()

        flash('Your driver account has been created! Please wait for admin approval before you can start accepting rides.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_rider.html', title='Register as Rider', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    if current_user.is_admin():
        return redirect(url_for('admin.profile'))
    elif current_user.is_rider():
        return redirect(url_for('rider.profile'))
    else:
        return redirect(url_for('customer.profile'))