"""
Ascendant-based functional planetary roles.

This module reports house ownership and commonly used functional-role flags.
It deliberately avoids reducing a planet to an unconditional benefic/malefic
verdict; placement, dignity, aspects, dasha, and divisional charts still matter.
"""

from house_analysis import SIGN_RULERS, ZODIAC_SIGNS


CLASSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
KENDRA_HOUSES = {1, 4, 7, 10}
YOGAKARAKA_KENDRAS = {4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
YOGAKARAKA_TRIKONAS = {5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
UPACHAYA_HOUSES = {3, 6, 10, 11}
MARAKA_HOUSES = {2, 7}
FUNCTIONALLY_CHALLENGING_HOUSES = {3, 6, 8, 11, 12}


def get_planet_house_ownership(ascendant_sign: str) -> dict:
    """Return houses owned by each classical planet for an ascendant."""
    ascendant_index = ZODIAC_SIGNS.index(ascendant_sign)
    ownership = {planet: [] for planet in CLASSICAL_PLANETS}

    for house in range(1, 13):
        sign = ZODIAC_SIGNS[(ascendant_index + house - 1) % 12]
        ownership[SIGN_RULERS[sign]].append(house)

    return ownership


def classify_functional_roles(ascendant_sign: str) -> dict:
    """Classify functional roles from whole-sign house ownership."""
    ownership = get_planet_house_ownership(ascendant_sign)
    roles = {}

    for planet, houses in ownership.items():
        house_set = set(houses)
        owns_kendra = sorted(house_set & KENDRA_HOUSES)
        owns_trikona = sorted(house_set & TRIKONA_HOUSES)
        owns_dusthana = sorted(house_set & DUSTHANA_HOUSES)
        owns_upachaya = sorted(house_set & UPACHAYA_HOUSES)
        owns_maraka = sorted(house_set & MARAKA_HOUSES)
        is_yogakaraka = bool(
            house_set & YOGAKARAKA_KENDRAS
            and house_set & YOGAKARAKA_TRIKONAS
        )

        tendency, reason = _functional_tendency(
            house_set=house_set,
            is_yogakaraka=is_yogakaraka,
        )
        roles[planet] = {
            "owned_houses": sorted(houses),
            "owns_lagna": 1 in house_set,
            "kendra_houses": owns_kendra,
            "trikona_houses": owns_trikona,
            "dusthana_houses": owns_dusthana,
            "upachaya_houses": owns_upachaya,
            "maraka_houses": owns_maraka,
            "is_yogakaraka": is_yogakaraka,
            "functional_tendency": tendency,
            "reason": reason,
        }

    return {
        "ascendant_sign": ascendant_sign,
        "house_system": "Whole sign",
        "roles": roles,
        "note": (
            "These are ownership-based functional tendencies, not final planet "
            "strengths or guaranteed outcomes. Natural character, placement, "
            "dignity, aspects, dasha, and divisional charts must also be reviewed."
        ),
    }


def _functional_tendency(house_set: set[int], is_yogakaraka: bool) -> tuple[str, str]:
    challenging = house_set & FUNCTIONALLY_CHALLENGING_HOUSES
    trinal = house_set & YOGAKARAKA_TRIKONAS

    if is_yogakaraka:
        return (
            "Strongly supportive potential",
            "Owns both a non-Lagna Kendra and a Dharma Trikona; flagged as Yogakaraka.",
        )
    if 1 in house_set and not challenging:
        return (
            "Supportive/self-signifying",
            "Owns the Ascendant without simultaneous ownership of a challenging house.",
        )
    if trinal and not challenging:
        return (
            "Supportive potential",
            "Owns the 5th or 9th house without simultaneous challenging-house ownership.",
        )
    if trinal or 1 in house_set:
        return (
            "Mixed with supportive potential",
            "Owns a Lagna/Trikona house and also a functionally challenging house.",
        )
    if house_set and house_set.issubset(FUNCTIONALLY_CHALLENGING_HOUSES):
        return (
            "Challenging potential",
            "Ownership is limited to houses commonly treated as functionally challenging.",
        )
    return (
        "Mixed/context-dependent",
        "House ownership combines multiple roles; no single ownership label is decisive.",
    )
