"""Indian states, union territories, and major cities for birth-place entry.

Coordinates are approximate city-centre coordinates. They are suitable for
initial chart calculation, while the manual-coordinate option remains available
for villages, border areas, hospitals far from the city centre, and overseas
births.
"""

INDIAN_LOCATIONS = {
    "Andaman and Nicobar Islands": {
        "Port Blair": (11.6234, 92.7265),
    },
    "Andhra Pradesh": {
        "Guntur": (16.3067, 80.4365),
        "Kurnool": (15.8281, 78.0373),
        "Tirupati": (13.6288, 79.4192),
        "Vijayawada": (16.5062, 80.6480),
        "Visakhapatnam": (17.6868, 83.2185),
    },
    "Arunachal Pradesh": {
        "Itanagar": (27.0844, 93.6053),
        "Pasighat": (28.0661, 95.3260),
        "Tawang": (27.5861, 91.8594),
    },
    "Assam": {
        "Dibrugarh": (27.4728, 94.9120),
        "Guwahati": (26.1445, 91.7362),
        "Jorhat": (26.7509, 94.2037),
        "Silchar": (24.8333, 92.7789),
        "Tezpur": (26.6528, 92.7926),
    },
    "Bihar": {
        "Bhagalpur": (25.2425, 86.9842),
        "Gaya": (24.7914, 85.0002),
        "Muzaffarpur": (26.1197, 85.3910),
        "Patna": (25.5941, 85.1376),
        "Purnia": (25.7771, 87.4753),
    },
    "Chandigarh": {
        "Chandigarh": (30.7333, 76.7794),
    },
    "Chhattisgarh": {
        "Bhilai": (21.1938, 81.3509),
        "Bilaspur": (22.0797, 82.1409),
        "Jagdalpur": (19.0748, 82.0080),
        "Raipur": (21.2514, 81.6296),
    },
    "Dadra and Nagar Haveli and Daman and Diu": {
        "Daman": (20.3974, 72.8328),
        "Silvassa": (20.2766, 73.0083),
    },
    "Delhi": {
        "New Delhi": (28.6139, 77.2090),
    },
    "Goa": {
        "Margao": (15.2832, 73.9862),
        "Panaji": (15.4909, 73.8278),
        "Vasco da Gama": (15.3860, 73.8440),
    },
    "Gujarat": {
        "Ahmedabad": (23.0225, 72.5714),
        "Bhavnagar": (21.7645, 72.1519),
        "Gandhinagar": (23.2156, 72.6369),
        "Rajkot": (22.3039, 70.8022),
        "Surat": (21.1702, 72.8311),
        "Vadodara": (22.3072, 73.1812),
    },
    "Haryana": {
        "Faridabad": (28.4089, 77.3178),
        "Gurugram": (28.4595, 77.0266),
        "Hisar": (29.1492, 75.7217),
        "Karnal": (29.6857, 76.9905),
        "Panipat": (29.3909, 76.9635),
    },
    "Himachal Pradesh": {
        "Dharamshala": (32.2190, 76.3234),
        "Mandi": (31.7087, 76.9320),
        "Shimla": (31.1048, 77.1734),
        "Solan": (30.9045, 77.0967),
    },
    "Jammu and Kashmir": {
        "Anantnag": (33.7311, 75.1487),
        "Jammu": (32.7266, 74.8570),
        "Srinagar": (34.0837, 74.7973),
    },
    "Jharkhand": {
        "Bokaro": (23.6693, 86.1511),
        "Dhanbad": (23.7957, 86.4304),
        "Jamshedpur": (22.8046, 86.2029),
        "Ranchi": (23.3441, 85.3096),
    },
    "Karnataka": {
        "Bengaluru": (12.9716, 77.5946),
        "Belagavi": (15.8497, 74.4977),
        "Hubballi": (15.3647, 75.1240),
        "Mangaluru": (12.9141, 74.8560),
        "Mysuru": (12.2958, 76.6394),
        "Shivamogga": (13.9299, 75.5681),
    },
    "Kerala": {
        "Alappuzha": (9.4981, 76.3388),
        "Kochi": (9.9312, 76.2673),
        "Kollam": (8.8932, 76.6141),
        "Kozhikode": (11.2588, 75.7804),
        "Thrissur": (10.5276, 76.2144),
        "Thiruvananthapuram": (8.5241, 76.9366),
    },
    "Ladakh": {
        "Kargil": (34.5539, 76.1349),
        "Leh": (34.1526, 77.5771),
    },
    "Lakshadweep": {
        "Kavaratti": (10.5667, 72.6417),
    },
    "Madhya Pradesh": {
        "Bhopal": (23.2599, 77.4126),
        "Gwalior": (26.2183, 78.1828),
        "Indore": (22.7196, 75.8577),
        "Jabalpur": (23.1815, 79.9864),
        "Sagar": (23.8388, 78.7378),
        "Ujjain": (23.1765, 75.7885),
    },
    "Maharashtra": {
        "Aurangabad": (19.8762, 75.3433),
        "Kolhapur": (16.7050, 74.2433),
        "Mumbai": (19.0760, 72.8777),
        "Nagpur": (21.1458, 79.0882),
        "Nashik": (19.9975, 73.7898),
        "Pune": (18.5204, 73.8567),
        "Thane": (19.2183, 72.9781),
    },
    "Manipur": {
        "Churachandpur": (24.3335, 93.6742),
        "Imphal": (24.8170, 93.9368),
    },
    "Meghalaya": {
        "Shillong": (25.5788, 91.8933),
        "Tura": (25.5138, 90.2036),
    },
    "Mizoram": {
        "Aizawl": (23.7271, 92.7176),
        "Lunglei": (22.8671, 92.7655),
    },
    "Nagaland": {
        "Dimapur": (25.9091, 93.7266),
        "Kohima": (25.6751, 94.1086),
    },
    "Odisha": {
        "Bhubaneswar": (20.2961, 85.8245),
        "Cuttack": (20.4625, 85.8830),
        "Puri": (19.8135, 85.8312),
        "Rourkela": (22.2604, 84.8536),
        "Sambalpur": (21.4669, 83.9812),
    },
    "Puducherry": {
        "Karaikal": (10.9254, 79.8380),
        "Puducherry": (11.9416, 79.8083),
    },
    "Punjab": {
        "Amritsar": (31.6340, 74.8723),
        "Bathinda": (30.2110, 74.9455),
        "Jalandhar": (31.3260, 75.5762),
        "Ludhiana": (30.9010, 75.8573),
        "Patiala": (30.3398, 76.3869),
    },
    "Rajasthan": {
        "Ajmer": (26.4499, 74.6399),
        "Bikaner": (28.0229, 73.3119),
        "Jaipur": (26.9124, 75.7873),
        "Jodhpur": (26.2389, 73.0243),
        "Kota": (25.2138, 75.8648),
        "Udaipur": (24.5854, 73.7125),
    },
    "Sikkim": {
        "Gangtok": (27.3389, 88.6065),
        "Namchi": (27.1667, 88.3500),
    },
    "Tamil Nadu": {
        "Chennai": (13.0827, 80.2707),
        "Coimbatore": (11.0168, 76.9558),
        "Madurai": (9.9252, 78.1198),
        "Salem": (11.6643, 78.1460),
        "Tiruchirappalli": (10.7905, 78.7047),
        "Tirunelveli": (8.7139, 77.7567),
        "Vellore": (12.9165, 79.1325),
    },
    "Telangana": {
        "Hyderabad": (17.3850, 78.4867),
        "Karimnagar": (18.4386, 79.1288),
        "Khammam": (17.2473, 80.1514),
        "Nizamabad": (18.6725, 78.0941),
        "Warangal": (17.9689, 79.5941),
    },
    "Tripura": {
        "Agartala": (23.8315, 91.2868),
        "Dharmanagar": (24.3667, 92.1667),
    },
    "Uttar Pradesh": {
        "Agra": (27.1767, 78.0081),
        "Ayodhya": (26.7922, 82.1998),
        "Ghaziabad": (28.6692, 77.4538),
        "Gorakhpur": (26.7606, 83.3732),
        "Kanpur": (26.4499, 80.3319),
        "Lucknow": (26.8467, 80.9462),
        "Meerut": (28.9845, 77.7064),
        "Varanasi": (25.3176, 82.9739),
    },
    "Uttarakhand": {
        "Dehradun": (30.3165, 78.0322),
        "Haldwani": (29.2183, 79.5130),
        "Haridwar": (29.9457, 78.1642),
        "Rishikesh": (30.0869, 78.2676),
    },
    "West Bengal": {
        "Asansol": (23.6739, 86.9524),
        "Darjeeling": (27.0410, 88.2663),
        "Durgapur": (23.5204, 87.3119),
        "Howrah": (22.5958, 88.2636),
        "Kolkata": (22.5726, 88.3639),
        "Siliguri": (26.7271, 88.3953),
    },
}


INDIAN_CITIES = {
    city: coordinates
    for cities in INDIAN_LOCATIONS.values()
    for city, coordinates in cities.items()
}


def get_state_list() -> list[str]:
    """Return sorted state and union-territory names."""
    return sorted(INDIAN_LOCATIONS)


def get_city_list(state_name: str | None = None) -> list[str]:
    """Return sorted cities for one state, or all known cities."""
    if state_name is None:
        return sorted(INDIAN_CITIES)
    return sorted(INDIAN_LOCATIONS.get(state_name, {}))


def get_city_coordinates(
    city_name: str,
    state_name: str | None = None,
) -> tuple[float, float] | None:
    """Return coordinates for a city, optionally constrained to a state."""
    if state_name is not None:
        return INDIAN_LOCATIONS.get(state_name, {}).get(city_name)
    return INDIAN_CITIES.get(city_name)
