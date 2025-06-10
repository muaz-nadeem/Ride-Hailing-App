from app import db, create_app
from app.models.user import User

def reset_admin():
    """Reset the admin user or create if it doesn't exist."""
    app = create_app()
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(user_type='admin').first()
        
        if admin:
            print(f"Found existing admin user: {admin.email}")
            # Reset password
            admin.password = 'admin123'
            db.session.commit()
            print(f"Admin password reset to: admin123")
        else:
            # Create new admin
            admin = User(
                username='admin',
                email='admin@fleetapp.com',
                user_type='admin'
            )
            admin.password = 'admin123'
            db.session.add(admin)
            db.session.commit()
            print("New admin user created with password: admin123")
        
        print("\nAdmin Login Details:")
        print(f"Email: {admin.email}")
        print(f"Password: admin123")

if __name__ == '__main__':
    reset_admin() 