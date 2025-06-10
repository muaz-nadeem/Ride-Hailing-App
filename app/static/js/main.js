document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Map related functions
function initMap(elementId, center = [51.505, -0.09], zoom = 13) {
    const map = L.map(elementId).setView(center, zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    return map;
}

function addMarker(map, latlng, title = '', icon = null) {
    let markerOptions = {};

    if (icon) {
        markerOptions.icon = icon;
    }

    const marker = L.marker(latlng, markerOptions).addTo(map);

    if (title) {
        marker.bindPopup(title);
    }

    return marker;
}

function drawRoute(map, startLatLng, endLatLng) {
    // Use OSRM to get road routing instead of a straight line
    const startPoint = startLatLng[1] + ',' + startLatLng[0]; // lon,lat format for OSRM
    const endPoint = endLatLng[1] + ',' + endLatLng[0]; // lon,lat format for OSRM
    
    // Create a placeholder polyline while waiting for the route
    let polyline = L.polyline([startLatLng, endLatLng], {
        color: 'blue',
        weight: 5,
        opacity: 0.7,
        dashArray: '10, 10'
    }).addTo(map);
    
    // Zoom to the placeholder route
    map.fitBounds(polyline.getBounds());
    
    // OSRM API to get the road route
    const url = `https://router.project-osrm.org/route/v1/driving/${startPoint};${endPoint}?overview=full&geometries=polyline`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.routes && data.routes.length > 0) {
                // Remove the placeholder polyline
                map.removeLayer(polyline);
                
                // Decode the polyline
                const routeGeometry = data.routes[0].geometry;
                const routePoints = L.Polyline.fromEncoded(routeGeometry).getLatLngs();
                
                // Create the route polyline
                polyline = L.polyline(routePoints, {
                    color: 'blue',
                    weight: 5,
                    opacity: 0.7
                }).addTo(map);
                
                // Update the map bounds
                map.fitBounds(polyline.getBounds());
            }
        })
        .catch(error => {
            console.error('Error fetching route:', error);
            // Keep the straight line if route fetching fails
        });
    
    return polyline;
}

// Custom marker icons
try {
    var riderIcon = L.icon({
        iconUrl: '/static/img/car-icon.png',
        iconSize: [40, 40],
        iconAnchor: [20, 40],
        popupAnchor: [0, -40],
        className: 'vehicle-icon' // Add a class for potential CSS styling
    });

    var customerIcon = L.icon({
        iconUrl: '/static/img/person-icon.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    });

    var destinationIcon = L.icon({
        iconUrl: '/static/img/destination-icon.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    });
} catch (e) {
    console.error("Error loading custom icons:", e);
    // Use default icons if custom icons fail to load
    var riderIcon = L.icon.Default;
    var customerIcon = L.icon.Default;
    var destinationIcon = L.icon.Default;
}

// Geolocation functions
function getCurrentLocation(callback) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                callback([lat, lng]);
            },
            function(error) {
                console.error('Error getting location:', error);
                callback(null);
            }
        );
    } else {
        console.error('Geolocation is not supported by this browser.');
        callback(null);
    }
}

// Function to calculate fare based on pickup and destination
function calculateFare(vehicleType, pickupLat, pickupLng, destLat, destLng) {
    const data = {
        vehicle_type: vehicleType,
        pickup_latitude: pickupLat,
        pickup_longitude: pickupLng,
        destination_latitude: destLat,
        destination_longitude: destLng
    };

    return fetch('/customer/calculate_fare', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .catch(error => console.error('Error calculating fare:', error));
}

// Function to update rider location
function updateRiderLocation(lat, lng) {
    const data = {
        latitude: lat,
        longitude: lng
    };

    return fetch('/rider/update_location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .catch(error => console.error('Error updating location:', error));
}

// Function to refresh pending rides for riders
function refreshPendingRides(containerId) {
    return fetch('/rider/pending_rides', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.html) {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = data.html;
            }
        }
    })
    .catch(error => console.error('Error refreshing rides:', error));
}

// Search for address using OpenStreetMap Nominatim API
function searchAddress(query, callback) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const result = data[0];
                callback({
                    lat: parseFloat(result.lat),
                    lng: parseFloat(result.lon),
                    display_name: result.display_name
                });
            } else {
                callback(null);
            }
        })
        .catch(error => {
            console.error('Error searching address:', error);
            callback(null);
        });
}

// Reverse geocode to get address from coordinates
function reverseGeocode(lat, lng, callback) {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                callback(data.display_name);
            } else {
                callback(null);
            }
        })
        .catch(error => {
            console.error('Error reverse geocoding:', error);
            callback(null);
        });
}