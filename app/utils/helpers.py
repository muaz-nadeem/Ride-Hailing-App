import math
from datetime import datetime
from app.models.vehicle import Vehicle

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the Haversine distance between two points in kilometers."""
    # Radius of the Earth in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def estimate_time(distance, avg_speed=30):
    """Estimate travel time in minutes based on distance and average speed."""
    # Average speed in km/h
    # Return time in minutes
    return (distance / avg_speed) * 60

def calculate_fare(vehicle_id, distance, estimated_time):
    """Calculate fare based on vehicle type, distance and estimated time."""
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        # Default values if vehicle not found
        base_fare = 5.0
        per_km_rate = 1.5
        per_minute_rate = 0.2
    else:
        base_fare = vehicle.base_fare
        per_km_rate = vehicle.per_km_rate
        per_minute_rate = vehicle.per_minute_rate
    
    # Calculate fare components
    distance_fare = distance * per_km_rate
    time_fare = estimated_time * per_minute_rate
    
    # Calculate total fare
    total_fare = base_fare + distance_fare + time_fare
    
    # Round to 2 decimal places
    return round(total_fare, 2)

def is_peak_hour():
    """Check if current time is during peak hours."""
    now = datetime.now()
    hour = now.hour
    
    # Define peak hours (7-9 AM and 5-7 PM on weekdays)
    is_weekday = now.weekday() < 5  # Monday-Friday
    is_morning_peak = 7 <= hour < 9
    is_evening_peak = 17 <= hour < 19
    
    return is_weekday and (is_morning_peak or is_evening_peak)

def apply_surge_pricing(fare):
    """Apply surge pricing during peak hours."""
    if is_peak_hour():
        surge_factor = 1.25  # 25% increase during peak hours
        return round(fare * surge_factor, 2)
    return fare 