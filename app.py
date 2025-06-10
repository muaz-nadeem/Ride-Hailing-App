from app import create_app, db
from app.models.user import User
from app.models.ride import Ride, Review, PaymentMethod
from app.models.vehicle import Vehicle, VehicleMaintenanceLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Ride': Ride, 
        'Review': Review,
        'Vehicle': Vehicle,
        'PaymentMethod': PaymentMethod,
        'VehicleMaintenanceLog': VehicleMaintenanceLog
    }

if __name__ == '__main__':
    app.run(debug=True) 