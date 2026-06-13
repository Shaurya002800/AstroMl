"""
Common Indian cities with coordinates, for quick selection in the birth details form.
Coordinates are approximate (city center) - sufficient for astrological calculations,
where exact-to-the-meter precision isn't required.
"""

INDIAN_CITIES = {
    "New Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Dehradun": (30.3165, 78.0322),
    "Chandigarh": (30.7333, 76.7794),
    "Bhopal": (23.2599, 77.4126),
    "Patna": (25.5941, 85.1376),
    "Indore": (22.7196, 75.8577),
    "Surat": (21.1702, 72.8311),
    "Nagpur": (21.1458, 79.0882),
    "Kanpur": (26.4499, 80.3319),
    "Coimbatore": (11.0168, 76.9558),
    "Kochi": (9.9312, 76.2673),
    "Guwahati": (26.1445, 91.7362),
    "Bhubaneswar": (20.2961, 85.8245),
    "Amritsar": (31.6340, 74.8723),
    "Varanasi": (25.3176, 82.9739),
    "Visakhapatnam": (17.6868, 83.2185),
    "Ranchi": (23.3441, 85.3096),
    "Raipur": (21.2514, 81.6296),
    "Shimla": (31.1048, 77.1734),
    "Srinagar": (34.0837, 74.7973),
    "Goa (Panaji)": (15.4909, 73.8278),
}


def get_city_coordinates(city_name: str):
    """Return (lat, lon) for a given city name, or None if not found."""
    return INDIAN_CITIES.get(city_name)


def get_city_list():
    """Return sorted list of city names for dropdown display."""
    return sorted(INDIAN_CITIES.keys())