"""
Planetary motion and combustion conditions.

Combustion thresholds vary across Jyotish traditions. The values below are an
explicit, configurable working convention and are returned with every result.
"""

COMBUSTION_ORBS = {
    "Moon": {"direct": 12.0, "retrograde": 12.0},
    "Mars": {"direct": 17.0, "retrograde": 17.0},
    "Mercury": {"direct": 14.0, "retrograde": 12.0},
    "Jupiter": {"direct": 11.0, "retrograde": 11.0},
    "Venus": {"direct": 10.0, "retrograde": 8.0},
    "Saturn": {"direct": 15.0, "retrograde": 15.0},
}


def angular_separation(longitude_a: float, longitude_b: float) -> float:
    """Return the shortest angular separation between two longitudes."""
    difference = abs(longitude_a - longitude_b) % 360
    return min(difference, 360 - difference)


def annotate_planetary_conditions(chart: dict) -> dict:
    """Add motion and combustion data to each planet in the chart."""
    sun_longitude = chart["planets"]["Sun"]["longitude"]

    for planet, data in chart["planets"].items():
        data["motion"] = "Retrograde" if data["is_retrograde"] else "Direct"

        if planet == "Sun":
            data["combustion"] = {
                "status": "Not applicable",
                "is_combust": False,
                "separation_from_sun": 0.0,
                "orb_used": None,
                "note": "The Sun is the reference point for combustion.",
            }
            continue

        if planet not in COMBUSTION_ORBS:
            data["combustion"] = {
                "status": "Not assessed",
                "is_combust": False,
                "separation_from_sun": round(
                    angular_separation(data["longitude"], sun_longitude), 4
                ),
                "orb_used": None,
                "note": "Standard combustion is not applied to lunar nodes in this model.",
            }
            continue

        motion_key = "retrograde" if data["is_retrograde"] else "direct"
        orb = COMBUSTION_ORBS[planet][motion_key]
        separation = angular_separation(data["longitude"], sun_longitude)
        is_combust = separation <= orb

        data["combustion"] = {
            "status": "Combust" if is_combust else "Not combust",
            "is_combust": is_combust,
            "separation_from_sun": round(separation, 4),
            "orb_used": orb,
            "note": (
                "Combustion thresholds are a configurable working convention; "
                "the consultant should consider dignity, house ownership, and "
                "other mitigating factors."
            ),
        }

    return chart
