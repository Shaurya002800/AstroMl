ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Exaltation sign for each planet (Rahu/Ketu exaltation is debated; using common convention)
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
    "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra",
    "Rahu": "Gemini", "Ketu": "Sagittarius"
}

# Debilitation = 7 signs away from exaltation (opposite sign)
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
    "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries",
    "Rahu": "Sagittarius", "Ketu": "Gemini"
}

# Own sign(s) - planet rules these signs
OWN_SIGNS = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
}

# Natural friendships between planets (simplified classical Naisargika Mitra table)
FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
}

ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
}

# Sign rulers (for friend/enemy sign placement check)
SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}


def get_dignity(planet: str, sign: str) -> dict:
    """
    Determine a planet's dignity (strength status) based on the sign it occupies.
    Returns a dict with status and a brief note.
    """
    if planet not in EXALTATION:
        return {"status": "N/A", "note": "Dignity not defined for this planet"}

    if sign == EXALTATION[planet]:
        return {"status": "Exalted", "note": f"{planet} is exalted in {sign} — peak strength"}

    if sign == DEBILITATION[planet]:
        return {"status": "Debilitated", "note": f"{planet} is debilitated in {sign} — weakened, may need other factors (neecha bhanga) to assess fully"}

    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return {"status": "Own Sign (Swakshetra)", "note": f"{planet} is in its own sign {sign} — strong and comfortable"}

    sign_ruler = SIGN_RULERS.get(sign)
    if sign_ruler and planet in FRIENDS and sign_ruler in FRIENDS[planet]:
        return {"status": "Friendly Sign", "note": f"{planet} is in a sign ruled by a friend ({sign_ruler}) — generally favorable"}

    if sign_ruler and planet in ENEMIES and sign_ruler in ENEMIES[planet]:
        return {"status": "Enemy Sign", "note": f"{planet} is in a sign ruled by an enemy ({sign_ruler}) — generally challenging"}

    return {"status": "Neutral", "note": f"{planet} is in {sign} — neutral placement"}


def get_navamsa_sign(longitude: float) -> str:
    """
    Compute the D9 Navamsa sign for a given sidereal longitude.
    Each sign (30°) is divided into 9 parts of 3°20' each.
    The navamsa sign sequence depends on the rashi (element-based starting point).
    """
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    navamsa_part = int(degree_in_sign // (30 / 9))  # 0-8

    # Starting navamsa sign depends on element of the rashi
    # Fire signs (Aries, Leo, Sag) start navamsa from Aries
    # Earth signs (Taurus, Virgo, Cap) start from Capricorn
    # Air signs (Gemini, Libra, Aqu) start from Libra
    # Water signs (Cancer, Scorpio, Pisces) start from Cancer
    fire_signs = [0, 4, 8]    # Aries, Leo, Sagittarius
    earth_signs = [1, 5, 9]   # Taurus, Virgo, Capricorn
    air_signs = [2, 6, 10]    # Gemini, Libra, Aquarius
    water_signs = [3, 7, 11]  # Cancer, Scorpio, Pisces

    if sign_index in fire_signs:
        start = 0   # Aries
    elif sign_index in earth_signs:
        start = 9   # Capricorn
    elif sign_index in air_signs:
        start = 6   # Libra
    else:  # water_signs
        start = 3   # Cancer

    navamsa_sign_index = (start + navamsa_part) % 12
    return ZODIAC_SIGNS[navamsa_sign_index]


def annotate_chart_with_dignity_and_navamsa(chart: dict) -> dict:
    """
    Take a chart dict (from chart.py) and add dignity + navamsa info to each planet.
    """
    for planet, data in chart["planets"].items():
        data["dignity"] = get_dignity(planet, data["sign"])
        data["navamsa_sign"] = get_navamsa_sign(data["longitude"])

    return chart


if __name__ == "__main__":
    from datetime import datetime
    from chart import compute_chart

    test_dt_utc = datetime(1990, 8, 15, 9, 0)
    delhi_lat, delhi_lon = 28.6139, 77.2090

    chart = compute_chart(test_dt_utc, delhi_lat, delhi_lon)
    chart = annotate_chart_with_dignity_and_navamsa(chart)

    for planet, data in chart["planets"].items():
        print(f"{planet}: {data['sign']} {data['degree']}° | "
              f"Dignity: {data['dignity']['status']} | "
              f"Navamsa: {data['navamsa_sign']}")