"""
Query-date sidereal transits mapped to natal whole-sign houses.

The module reports positions and sign-based contacts. It does not infer that a
transit alone causes a specific event.
"""

from chart import compute_planetary_snapshot
from dignity import get_dignity
from house_analysis import ASPECT_OFFSETS, ZODIAC_SIGNS, get_house_number
from planetary_conditions import annotate_planetary_conditions


SLOW_TRANSIT_PLANETS = {"Jupiter", "Saturn", "Rahu", "Ketu"}


def compute_transit_report(
    query_datetime_utc,
    natal_chart: dict,
    natal_ascendant_sign: str,
) -> dict:
    """Compute transits relative to natal Ascendant, Moon, and planets."""
    snapshot = compute_planetary_snapshot(query_datetime_utc)
    transit_chart = {"planets": snapshot["planets"]}
    annotate_planetary_conditions(transit_chart)
    natal_moon_sign = natal_chart["planets"]["Moon"]["sign"]

    positions = {}
    conjunctions = []

    for planet, data in transit_chart["planets"].items():
        natal_house = get_house_number(data["sign"], natal_ascendant_sign)
        moon_house = get_house_number(data["sign"], natal_moon_sign)
        conjunct_natal_planets = sorted(
            natal_planet
            for natal_planet, natal_data in natal_chart["planets"].items()
            if natal_data["sign"] == data["sign"]
        )
        positions[planet] = {
            "sign": data["sign"],
            "degree": round(data["degree"], 2),
            "nakshatra": data["nakshatra"],
            "pada": data["pada"],
            "motion": data["motion"],
            "is_retrograde": data["is_retrograde"],
            "dignity": get_dignity(planet, data["sign"])["status"],
            "house_from_natal_ascendant": natal_house,
            "house_from_natal_moon": moon_house,
            "conjunct_natal_planets_by_sign": conjunct_natal_planets,
            "is_slow_transit_focus": planet in SLOW_TRANSIT_PLANETS,
        }
        if conjunct_natal_planets:
            conjunctions.append({
                "transit_planet": planet,
                "sign": data["sign"],
                "natal_planets": conjunct_natal_planets,
                "contact_type": "Same-sign conjunction",
            })

    aspects = _compute_transit_aspects(
        transit_chart=transit_chart,
        natal_chart=natal_chart,
        natal_ascendant_sign=natal_ascendant_sign,
    )

    return {
        "query_datetime_utc": query_datetime_utc.isoformat(),
        "ayanamsa": "Lahiri",
        "house_system": "Whole sign",
        "positions": positions,
        "same_sign_conjunctions": conjunctions,
        "parashari_aspects_to_natal_chart": aspects,
        "slow_transit_focus": {
            planet: positions[planet]
            for planet in ("Jupiter", "Saturn", "Rahu", "Ketu")
        },
        "note": (
            "Transit contacts are timing context only. Interpret them together "
            "with natal promise, active dasha, dignity, and relevant divisional charts."
        ),
    }


def _compute_transit_aspects(
    transit_chart: dict,
    natal_chart: dict,
    natal_ascendant_sign: str,
) -> list[dict]:
    natal_planet_houses = {
        planet: get_house_number(data["sign"], natal_ascendant_sign)
        for planet, data in natal_chart["planets"].items()
    }
    aspects = []

    for planet, offsets in ASPECT_OFFSETS.items():
        source_house = get_house_number(
            transit_chart["planets"][planet]["sign"],
            natal_ascendant_sign,
        )
        for offset in offsets:
            target_house = ((source_house + offset - 2) % 12) + 1
            target_planets = sorted(
                natal_planet
                for natal_planet, house in natal_planet_houses.items()
                if house == target_house
            )
            aspects.append({
                "transit_planet": planet,
                "from_natal_house": source_house,
                "aspect": offset,
                "to_natal_house": target_house,
                "to_sign": ZODIAC_SIGNS[
                    (
                        ZODIAC_SIGNS.index(natal_ascendant_sign)
                        + target_house
                        - 1
                    ) % 12
                ],
                "natal_planets_aspected": target_planets,
            })

    return aspects
