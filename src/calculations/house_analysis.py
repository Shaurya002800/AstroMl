"""
Whole-sign house lordships and Parashari planetary aspects.

Node aspects are intentionally excluded because conventions differ between
traditions. This module reports only the standard seven-planet graha drishti
pattern used by the model.
"""

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

ASPECT_OFFSETS = {
    "Sun": [7],
    "Moon": [7],
    "Mars": [4, 7, 8],
    "Mercury": [7],
    "Jupiter": [5, 7, 9],
    "Venus": [7],
    "Saturn": [3, 7, 10],
}


def get_house_number(sign: str, ascendant_sign: str) -> int:
    ascendant_index = ZODIAC_SIGNS.index(ascendant_sign)
    sign_index = ZODIAC_SIGNS.index(sign)
    return ((sign_index - ascendant_index) % 12) + 1


def analyze_house_lordships(chart: dict, ascendant_sign: str) -> dict:
    """Return whole-sign house ownership, occupants, and lord placement."""
    ascendant_index = ZODIAC_SIGNS.index(ascendant_sign)
    occupants = {house: [] for house in range(1, 13)}

    for planet, data in chart["planets"].items():
        occupants[get_house_number(data["sign"], ascendant_sign)].append(planet)

    houses = {}
    for house in range(1, 13):
        sign = ZODIAC_SIGNS[(ascendant_index + house - 1) % 12]
        lord = SIGN_RULERS[sign]
        lord_data = chart["planets"][lord]
        houses[house] = {
            "sign": sign,
            "lord": lord,
            "occupants": occupants[house],
            "lord_placement": {
                "house": get_house_number(lord_data["sign"], ascendant_sign),
                "sign": lord_data["sign"],
                "dignity": lord_data["dignity"]["status"],
                "retrograde": lord_data["is_retrograde"],
                "combust": lord_data["combustion"]["is_combust"],
            },
        }

    return {
        "house_system": "Whole sign",
        "houses": houses,
    }


def compute_parashari_aspects(chart: dict, ascendant_sign: str) -> dict:
    """Compute sign-based Parashari graha drishti for the seven planets."""
    planet_houses = {
        planet: get_house_number(data["sign"], ascendant_sign)
        for planet, data in chart["planets"].items()
    }
    aspects = []

    for planet, offsets in ASPECT_OFFSETS.items():
        source_house = planet_houses[planet]
        for offset in offsets:
            target_house = ((source_house + offset - 2) % 12) + 1
            aspected_planets = sorted(
                other
                for other, house in planet_houses.items()
                if other != planet and house == target_house
            )
            aspects.append(
                {
                    "planet": planet,
                    "from_house": source_house,
                    "aspect": offset,
                    "to_house": target_house,
                    "to_sign": ZODIAC_SIGNS[
                        (ZODIAC_SIGNS.index(ascendant_sign) + target_house - 1) % 12
                    ],
                    "aspected_planets": aspected_planets,
                }
            )

    return {
        "system": "Parashari graha drishti, sign-based",
        "node_aspects_included": False,
        "note": (
            "Rahu and Ketu aspects are excluded because traditions differ. "
            "These are sign-based aspects and do not assign percentage strength."
        ),
        "aspects": aspects,
    }
