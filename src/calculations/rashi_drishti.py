"""
Jaimini-style sign aspects (rashi drishti).

Working convention:
- Movable signs aspect fixed signs except the adjacent fixed sign.
- Fixed signs aspect movable signs except the adjacent movable sign.
- Dual signs aspect the other dual signs.

This is kept separate from Parashari graha drishti.
"""

try:
    from .house_analysis import ZODIAC_SIGNS, get_house_number
except ImportError:
    from house_analysis import ZODIAC_SIGNS, get_house_number


MOVABLE_SIGNS = {"Aries", "Cancer", "Libra", "Capricorn"}
FIXED_SIGNS = {"Taurus", "Leo", "Scorpio", "Aquarius"}
DUAL_SIGNS = {"Gemini", "Virgo", "Sagittarius", "Pisces"}


def signs_aspected_by(source_sign: str) -> list[str]:
    """Return rashi-drishti target signs under the configured convention."""
    source_index = ZODIAC_SIGNS.index(source_sign)

    if source_sign in MOVABLE_SIGNS:
        adjacent_fixed = ZODIAC_SIGNS[(source_index + 1) % 12]
        return [
            sign
            for sign in ZODIAC_SIGNS
            if sign in FIXED_SIGNS and sign != adjacent_fixed
        ]

    if source_sign in FIXED_SIGNS:
        adjacent_movable = ZODIAC_SIGNS[(source_index - 1) % 12]
        return [
            sign
            for sign in ZODIAC_SIGNS
            if sign in MOVABLE_SIGNS and sign != adjacent_movable
        ]

    return [
        sign
        for sign in ZODIAC_SIGNS
        if sign in DUAL_SIGNS and sign != source_sign
    ]


def compute_rashi_drishti(chart: dict, ascendant_sign: str) -> dict:
    """Compute occupied-sign rashi drishti and carried planet contacts."""
    planets_by_sign = {sign: [] for sign in ZODIAC_SIGNS}
    for planet, data in chart["planets"].items():
        planets_by_sign[data["sign"]].append(planet)

    occupied_signs = sorted(
        sign
        for sign, planets in planets_by_sign.items()
        if planets
    )
    contacts = []

    for source_sign in occupied_signs:
        source_planets = sorted(planets_by_sign[source_sign])
        for target_sign in signs_aspected_by(source_sign):
            contacts.append({
                "source_sign": source_sign,
                "source_house": get_house_number(
                    source_sign, ascendant_sign
                ),
                "source_planets": source_planets,
                "target_sign": target_sign,
                "target_house": get_house_number(
                    target_sign, ascendant_sign
                ),
                "target_planets": sorted(planets_by_sign[target_sign]),
            })

    return {
        "system": "Jaimini-style rashi drishti",
        "convention": (
            "Movable-to-fixed excluding adjacent; fixed-to-movable excluding "
            "adjacent; dual-to-other-dual."
        ),
        "contacts": contacts,
        "note": (
            "Rashi drishti is sign-to-sign and is separate from Parashari "
            "planetary aspects. Interpretive traditions differ."
        ),
    }
