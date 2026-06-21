"""Birth-time sensitivity analysis for house and varga-dependent results."""

from __future__ import annotations

from datetime import timedelta

try:
    from .chart import compute_chart
    from .dignity import get_navamsa_sign
    from .divisional_charts import get_dasamsa_sign, get_saptamsa_sign
    from .extended_divisional_charts import (
        get_chaturthamsa_sign,
        get_drekkana_sign,
        get_dwadashamsa_sign,
        get_hora_sign,
        get_trimsamsa_sign,
    )
    from .house_analysis import get_house_number
except ImportError:
    from chart import compute_chart
    from dignity import get_navamsa_sign
    from divisional_charts import get_dasamsa_sign, get_saptamsa_sign
    from extended_divisional_charts import (
        get_chaturthamsa_sign,
        get_drekkana_sign,
        get_dwadashamsa_sign,
        get_hora_sign,
        get_trimsamsa_sign,
    )
    from house_analysis import get_house_number


DEFAULT_OFFSETS_MINUTES = [-60, -30, -15, 15, 30, 60]
VARGA_CALCULATORS = {
    "D2": get_hora_sign,
    "D3": get_drekkana_sign,
    "D4": get_chaturthamsa_sign,
    "D7": get_saptamsa_sign,
    "D9": get_navamsa_sign,
    "D10": get_dasamsa_sign,
    "D12": get_dwadashamsa_sign,
    "D30": get_trimsamsa_sign,
}


def compute_birth_time_sensitivity(
    birth_datetime_utc,
    latitude: float,
    longitude: float,
    baseline_chart: dict,
    offsets_minutes: list[int] | None = None,
) -> dict:
    offsets = offsets_minutes or DEFAULT_OFFSETS_MINUTES
    baseline = _snapshot(baseline_chart)
    scenarios = {}

    for offset in offsets:
        shifted_chart = compute_chart(
            birth_datetime_utc + timedelta(minutes=offset),
            latitude,
            longitude,
        )
        shifted = _snapshot(shifted_chart)
        scenarios[str(offset)] = {
            "offset_minutes": offset,
            "ascendant_sign": shifted["ascendant_sign"],
            "ascendant_degree": shifted_chart["ascendant"]["degree"],
            "ascendant_sign_changed": (
                shifted["ascendant_sign"] != baseline["ascendant_sign"]
            ),
            "changed_planet_houses": sorted(
                planet
                for planet, house in shifted["planet_houses"].items()
                if house != baseline["planet_houses"][planet]
            ),
            "changed_ascendant_vargas": sorted(
                varga
                for varga, sign in shifted["ascendant_vargas"].items()
                if sign != baseline["ascendant_vargas"][varga]
            ),
            "changed_planet_vargas": {
                varga: sorted(
                    planet
                    for planet, sign in placements.items()
                    if sign != baseline["planet_vargas"][varga][planet]
                )
                for varga, placements in shifted["planet_vargas"].items()
                if any(
                    sign != baseline["planet_vargas"][varga][planet]
                    for planet, sign in placements.items()
                )
            },
        }

    return {
        "offsets_minutes": offsets,
        "scenarios": scenarios,
        "stable_within_15_minutes": _stable_within(scenarios, 15),
        "stable_within_60_minutes": _stable_within(scenarios, 60),
        "note": (
            "This sensitivity report does not rectify birth time. It shows "
            "which house and divisional outputs change under nearby times."
        ),
    }


def _snapshot(chart: dict) -> dict:
    ascendant_sign = chart["ascendant"]["sign"]
    return {
        "ascendant_sign": ascendant_sign,
        "planet_houses": {
            planet: get_house_number(data["sign"], ascendant_sign)
            for planet, data in chart["planets"].items()
        },
        "ascendant_vargas": {
            varga: calculator(chart["ascendant"]["longitude"])
            for varga, calculator in VARGA_CALCULATORS.items()
        },
        "planet_vargas": {
            varga: {
                planet: calculator(data["longitude"])
                for planet, data in chart["planets"].items()
            }
            for varga, calculator in VARGA_CALCULATORS.items()
        },
    }


def _stable_within(scenarios: dict, threshold_minutes: int) -> bool:
    relevant = [
        scenario
        for scenario in scenarios.values()
        if abs(scenario["offset_minutes"]) <= threshold_minutes
    ]
    return all(
        not scenario["ascendant_sign_changed"]
        and not scenario["changed_planet_houses"]
        and not scenario["changed_ascendant_vargas"]
        and not scenario["changed_planet_vargas"]
        for scenario in relevant
    )
