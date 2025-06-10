from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.forms.main_forms import ContactForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_rider():
            return redirect(url_for('rider.dashboard'))
        else:
            return redirect(url_for('customer.dashboard'))
    return render_template('main/index.html', title='Home')

@main.route('/about')
def about():
    return render_template('main/about.html', title='About')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    if form.validate_on_submit():
        # In a real application, you would send an email here
        # For now, we'll just flash a success message
        
        # Example of how you might send an email:
        # send_email(
        #     recipient="support@fleetapp.com",
        #     subject=f"Contact Form: {form.subject.data}",
        #     template="email/contact",
        #     name=form.name.data,
        #     email=form.email.data,
        #     message=form.message.data
        # )
        
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('main/contact.html', title='Contact', form=form)

@main.route('/terms')
def terms():
    return render_template('main/terms.html', title='Terms of Service')

@main.route('/privacy')
def privacy():
    return render_template('main/privacy.html', title='Privacy Policy') 