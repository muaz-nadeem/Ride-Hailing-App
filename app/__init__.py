from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from config import Config
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()

def create_admin_user(app):
    """Create an admin user if one doesn't exist."""
    with app.app_context():
        from app.models.user import User
        
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

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Register blueprints
    from app.controllers.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.controllers.customer import customer as customer_blueprint
    app.register_blueprint(customer_blueprint, url_prefix='/customer')
    
    from app.controllers.rider import rider as rider_blueprint
    app.register_blueprint(rider_blueprint, url_prefix='/rider')
    
    from app.controllers.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from app.controllers.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Add datetime to all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app

from app.models import user, ride, vehicle 