"""
Query-date sidereal transits mapped to natal whole-sign houses.

The module reports positions and sign-based contacts. It does not infer that a
transit alone causes a specific event.
"""

from datetime import timedelta

import swisseph as swe

try:
    from .chart import (
        PLANETS,
        compute_planetary_snapshot,
        get_julian_day,
        get_sign_and_degree,
    )
    from .dignity import get_dignity
    from .house_analysis import ASPECT_OFFSETS, ZODIAC_SIGNS, get_house_number
    from .planetary_conditions import annotate_planetary_conditions
except ImportError:
    from chart import (
        PLANETS,
        compute_planetary_snapshot,
        get_julian_day,
        get_sign_and_degree,
    )
    from dignity import get_dignity
    from house_analysis import ASPECT_OFFSETS, ZODIAC_SIGNS, get_house_number
    from planetary_conditions import annotate_planetary_conditions


SLOW_TRANSIT_PLANETS = {"Jupiter", "Saturn", "Rahu", "Ketu"}
INGRESS_SEARCH_DAYS = {
    "Jupiter": 550,
    "Saturn": 1400,
    "Rahu": 700,
    "Ketu": 700,
}
STATION_SEARCH_DAYS = {
    "Mercury": 90,
    "Venus": 400,
    "Mars": 500,
    "Jupiter": 500,
    "Saturn": 500,
}


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
    timing_windows = {
        planet: compute_sign_window(planet, query_datetime_utc)
        for planet in ("Jupiter", "Saturn", "Rahu", "Ketu")
    }
    station_windows = {
        planet: compute_station_window(planet, query_datetime_utc)
        for planet in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn")
    }

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
        "slow_planet_sign_windows": timing_windows,
        "station_windows": station_windows,
        "note": (
            "Transit contacts are timing context only. Interpret them together "
            "with natal promise, active dasha, dignity, and relevant divisional charts."
        ),
    }


def compute_sign_window(planet: str, query_datetime_utc) -> dict:
    """Find the approximate interval during which a slow planet remains in its sign."""
    current_sign = _planet_sign(planet, query_datetime_utc)
    max_days = INGRESS_SEARCH_DAYS[planet]
    previous_change = _find_sign_change(
        planet,
        query_datetime_utc,
        current_sign,
        direction=-1,
        max_days=max_days,
    )
    next_change = _find_sign_change(
        planet,
        query_datetime_utc,
        current_sign,
        direction=1,
        max_days=max_days,
    )

    return {
        "planet": planet,
        "sign": current_sign,
        "entered_sign_utc": (
            previous_change.isoformat() if previous_change else None
        ),
        "leaves_sign_utc": next_change.isoformat() if next_change else None,
        "precision": "Approximately one minute",
        "note": (
            "Retrograde motion can produce repeated entries into the same sign. "
            "This window describes the continuous stay containing the analysis date."
        ),
    }


def compute_station_window(planet: str, query_datetime_utc) -> dict:
    """Find nearest prior and next longitude-speed sign changes."""
    max_days = STATION_SEARCH_DAYS[planet]
    previous_station = _find_speed_change(
        planet,
        query_datetime_utc,
        direction=-1,
        max_days=max_days,
    )
    next_station = _find_speed_change(
        planet,
        query_datetime_utc,
        direction=1,
        max_days=max_days,
    )

    return {
        "planet": planet,
        "motion_at_query": (
            "Retrograde" if _planet_speed(planet, query_datetime_utc) < 0 else "Direct"
        ),
        "previous_station_utc": (
            previous_station.isoformat() if previous_station else None
        ),
        "next_station_utc": next_station.isoformat() if next_station else None,
        "search_horizon_days": max_days,
        "precision": "Approximately one minute",
    }


def _find_sign_change(
    planet: str,
    query_datetime_utc,
    current_sign: str,
    direction: int,
    max_days: int,
):
    step = timedelta(days=5 * direction)
    inside = query_datetime_utc

    for _ in range(max_days // 5):
        outside = inside + step
        if _planet_sign(planet, outside) != current_sign:
            if direction < 0:
                return _bisect_sign_boundary(
                    planet, outside, inside, current_sign
                )
            return _bisect_sign_boundary(
                planet, inside, outside, current_sign
            )
        inside = outside
    return None


def _bisect_sign_boundary(
    planet: str,
    inside_datetime,
    outside_datetime,
    inside_sign: str,
):
    left = inside_datetime
    right = outside_datetime
    left_is_inside = _planet_sign(planet, left) == inside_sign

    for _ in range(14):
        midpoint = left + (right - left) / 2
        midpoint_is_inside = _planet_sign(planet, midpoint) == inside_sign
        if midpoint_is_inside == left_is_inside:
            left = midpoint
        else:
            right = midpoint
    return left + (right - left) / 2


def _find_speed_change(
    planet: str,
    query_datetime_utc,
    direction: int,
    max_days: int,
):
    step = timedelta(days=direction)
    inside = query_datetime_utc
    inside_speed = _planet_speed(planet, inside)

    for _ in range(max_days):
        outside = inside + step
        outside_speed = _planet_speed(planet, outside)
        if inside_speed == 0 or inside_speed * outside_speed < 0:
            return _bisect_speed_boundary(planet, inside, outside)
        inside = outside
        inside_speed = outside_speed
    return None


def _bisect_speed_boundary(planet: str, datetime_a, datetime_b):
    left = min(datetime_a, datetime_b)
    right = max(datetime_a, datetime_b)
    left_speed = _planet_speed(planet, left)

    for _ in range(14):
        midpoint = left + (right - left) / 2
        midpoint_speed = _planet_speed(planet, midpoint)
        if left_speed == 0 or left_speed * midpoint_speed <= 0:
            right = midpoint
        else:
            left = midpoint
            left_speed = midpoint_speed
    return left + (right - left) / 2


def _planet_sign(planet: str, datetime_utc) -> str:
    longitude, _ = _planet_longitude_and_speed(planet, datetime_utc)
    return get_sign_and_degree(longitude)[0]


def _planet_speed(planet: str, datetime_utc) -> float:
    _, speed = _planet_longitude_and_speed(planet, datetime_utc)
    return speed


def _planet_longitude_and_speed(planet: str, datetime_utc) -> tuple[float, float]:
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    if planet == "Ketu":
        values, _ = swe.calc_ut(
            get_julian_day(datetime_utc),
            PLANETS["Rahu"],
            flags,
        )
        return (values[0] + 180) % 360, values[3]

    values, _ = swe.calc_ut(
        get_julian_day(datetime_utc),
        PLANETS[planet],
        flags,
    )
    return values[0], values[3]


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
