from app import create_app, db
from app.models.user import User

def create_admin():
    """Create an admin user if one doesn't exist."""
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(user_type='admin').first()
        if admin is None:
            admin = User(
                username=app.config['ADMIN_USERNAME'],
                email=app.config['ADMIN_EMAIL'],
                user_type='admin'
            )
            admin.password = app.config['ADMIN_PASSWORD']
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    create_admin() 