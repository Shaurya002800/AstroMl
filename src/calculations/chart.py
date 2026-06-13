import swisseph as swe
from datetime import datetime
import os

# Point to ephemeris data files
EPHE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ephemeris")
swe.set_ephe_path(EPHE_PATH)

# Use Lahiri ayanamsa - standard for Vedic astrology
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,   # North Node (Mean)
    # Ketu derived separately (180° from Rahu)
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]


def get_julian_day(birth_datetime_utc: datetime) -> float:
    """Convert a UTC datetime to Julian Day (required by Swiss Ephemeris)."""
    return swe.julday(
        birth_datetime_utc.year,
        birth_datetime_utc.month,
        birth_datetime_utc.day,
        birth_datetime_utc.hour + birth_datetime_utc.minute / 60.0
    )


def get_sign_and_degree(longitude: float):
    """Given sidereal longitude (0-360), return (sign_name, degree_within_sign)."""
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    return ZODIAC_SIGNS[sign_index], degree_in_sign


def get_nakshatra(longitude: float):
    """Given sidereal longitude (0-360), return (nakshatra_name, pada_number 1-4)."""
    nak_span = 360 / 27  # 13.333...
    nak_index = int(longitude // nak_span)
    pada = int((longitude % nak_span) // (nak_span / 4)) + 1
    return NAKSHATRAS[nak_index], pada


def get_planet_positions(jd: float) -> dict:
    """Return sidereal longitude for each planet at given Julian Day."""
    positions = {}
    flags = swe.FLG_SIDEREAL

    for name, code in PLANETS.items():
        lon, _ = swe.calc_ut(jd, code, flags)[0:2] if False else (swe.calc_ut(jd, code, flags)[0][0], None)
        positions[name] = lon

    # Ketu = Rahu + 180
    positions["Ketu"] = (positions["Rahu"] + 180) % 360

    return positions


def get_ascendant(jd: float, lat: float, lon: float) -> float:
    """Return sidereal longitude of the ascendant (Lagna)."""
    houses = swe.houses_ex(jd, lat, lon, b'P', flags=swe.FLG_SIDEREAL)  # Placidus
    ascendant = houses[0][0]
    return ascendant


def compute_chart(birth_datetime_utc: datetime, lat: float, lon: float) -> dict:
    """
    Main entry point: compute full chart data.
    birth_datetime_utc: datetime object in UTC
    lat, lon: birth place coordinates
    """
    jd = get_julian_day(birth_datetime_utc)

    planet_positions = get_planet_positions(jd)
    ascendant_lon = get_ascendant(jd, lat, lon)

    chart = {
        "julian_day": jd,
        "ascendant": {
            "longitude": ascendant_lon,
            "sign": get_sign_and_degree(ascendant_lon)[0],
            "degree": round(get_sign_and_degree(ascendant_lon)[1], 4),
            "nakshatra": get_nakshatra(ascendant_lon)[0],
            "pada": get_nakshatra(ascendant_lon)[1],
        },
        "planets": {}
    }

    for planet, lon_val in planet_positions.items():
        sign, deg = get_sign_and_degree(lon_val)
        nak, pada = get_nakshatra(lon_val)
        chart["planets"][planet] = {
            "longitude": round(lon_val, 4),
            "sign": sign,
            "degree": round(deg, 4),
            "nakshatra": nak,
            "pada": pada,
        }

    return chart


if __name__ == "__main__":
    # Test with a sample birth: 15 Aug 1990, 14:30 IST, New Delhi
    # Convert IST to UTC: subtract 5:30
    test_dt_utc = datetime(1990, 8, 15, 9, 0)  # 14:30 IST - 5:30 = 09:00 UTC
    delhi_lat, delhi_lon = 28.6139, 77.2090

    result = compute_chart(test_dt_utc, delhi_lat, delhi_lon)

    print("Ascendant:", result["ascendant"])
    print("\nPlanetary Positions:")
    for planet, data in result["planets"].items():
        print(f"  {planet}: {data['sign']} {data['degree']}° "
              f"(Nakshatra: {data['nakshatra']} Pada {data['pada']})")