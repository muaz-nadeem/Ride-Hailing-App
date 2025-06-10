# Fleet Management Application

A full-featured fleet management web application similar to Uber, built with Flask, PostgreSQL, and Leaflet maps.

## Features

### Customer Features
- Book rides from one location to another
- Schedule rides for later
- View ride fare before booking
- Track ongoing rides with real-time map updates
- Pay for rides through multiple payment methods
- Rate and review rides
- View ride history

### Rider Features
- Accept or reject ride requests
- Update availability status
- Update real-time GPS location
- Track earnings
- View rider ratings and reviews
- Navigate to pickup and drop-off locations

### Admin Features
- Manage vehicles and drivers
- View analytics and reports
- Manage and resolve disputes
- Monitor system status
- Approve/reject rider applications
- Add new vehicles to inventory

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Maps**: Leaflet.js
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Database ORM**: SQLAlchemy

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/fleet-management.git
cd fleet-management
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Create a PostgreSQL database:
```
createdb fleet_db
```

5. Configure the environment variables in `.env` file:
```
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/fleet_db
FLASK_APP=app.py
FLASK_ENV=development
```

6. Initialize the database:
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. Run the application:
```
flask run
```

8. Access the application at `http://localhost:5000`

## Database Schema

The application uses the following main models:
- User (Customer, Rider, Admin)
- CustomerProfile
- RiderProfile
- Vehicle
- Ride
- Review
- PaymentMethod

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Leaflet.js for the mapping functionality
- Bootstrap for the UI components
- Flask community for the excellent documentation 