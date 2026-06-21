"""
Additional divisional charts with explicit Parashari working conventions.

Implemented:
- D2 Hora
- D3 Drekkana
- D4 Chaturthamsa
- D12 Dwadashamsa
- D30 Trimsamsa

D16, D24, and D60 remain disabled until an edition/convention is selected and
cross-engine fixtures are available.
"""

try:
    from .dignity import ZODIAC_SIGNS
except ImportError:
    from dignity import ZODIAC_SIGNS


VARGA_METADATA = {
    "D2": {
        "name": "Hora",
        "focus": "Resources and family support",
        "equal_divisions": 2,
    },
    "D3": {
        "name": "Drekkana",
        "focus": "Siblings, initiative, and resilience",
        "equal_divisions": 3,
    },
    "D4": {
        "name": "Chaturthamsa",
        "focus": "Property, fortune, and settled foundations",
        "equal_divisions": 4,
    },
    "D12": {
        "name": "Dwadashamsa",
        "focus": "Parents and inherited family patterns",
        "equal_divisions": 12,
    },
    "D30": {
        "name": "Trimsamsa",
        "focus": "Challenges and vulnerabilities",
        "equal_divisions": None,
    },
}

DISABLED_VARGAS = {
    "D16": "Convention selection and cross-engine validation pending.",
    "D24": "Convention selection and cross-engine validation pending.",
    "D60": (
        "Highly birth-time-sensitive; convention selection, rectification policy, "
        "and cross-engine validation pending."
    ),
}


def get_hora_sign(longitude: float) -> str:
    sign_index, degree = _sign_and_degree(longitude)
    is_odd_sign = sign_index % 2 == 0
    if is_odd_sign:
        return "Leo" if degree < 15 else "Cancer"
    return "Cancer" if degree < 15 else "Leo"


def get_drekkana_sign(longitude: float) -> str:
    sign_index, degree = _sign_and_degree(longitude)
    part = min(int(degree // 10), 2)
    return ZODIAC_SIGNS[(sign_index + (0, 4, 8)[part]) % 12]


def get_chaturthamsa_sign(longitude: float) -> str:
    sign_index, degree = _sign_and_degree(longitude)
    part = min(int(degree // 7.5), 3)
    return ZODIAC_SIGNS[(sign_index + part * 3) % 12]


def get_dwadashamsa_sign(longitude: float) -> str:
    sign_index, degree = _sign_and_degree(longitude)
    part = min(int(degree // 2.5), 11)
    return ZODIAC_SIGNS[(sign_index + part) % 12]


def get_trimsamsa_sign(longitude: float) -> str:
    sign_index, degree = _sign_and_degree(longitude)
    is_odd_sign = sign_index % 2 == 0

    if is_odd_sign:
        if degree < 5:
            return "Aries"
        if degree < 10:
            return "Aquarius"
        if degree < 18:
            return "Sagittarius"
        if degree < 25:
            return "Gemini"
        return "Libra"

    if degree < 5:
        return "Taurus"
    if degree < 12:
        return "Virgo"
    if degree < 20:
        return "Pisces"
    if degree < 25:
        return "Capricorn"
    return "Scorpio"


def build_extended_divisional_charts(
    chart: dict,
    boundary_threshold_degrees: float = 0.05,
) -> dict:
    calculators = {
        "D2": get_hora_sign,
        "D3": get_drekkana_sign,
        "D4": get_chaturthamsa_sign,
        "D12": get_dwadashamsa_sign,
        "D30": get_trimsamsa_sign,
    }
    result = {}

    for varga, calculator in calculators.items():
        ascendant_longitude = chart["ascendant"]["longitude"]
        result[varga] = {
            **VARGA_METADATA[varga],
            "status": "implemented_needs_cross_engine_validation",
            "ascendant_sign": calculator(ascendant_longitude),
            "ascendant_boundary_sensitivity": _boundary_sensitivity(
                ascendant_longitude,
                varga,
                boundary_threshold_degrees,
            ),
            "planets": {
                planet: {
                    "sign": calculator(data["longitude"]),
                    "boundary_sensitivity": _boundary_sensitivity(
                        data["longitude"],
                        varga,
                        boundary_threshold_degrees,
                    ),
                }
                for planet, data in chart["planets"].items()
            },
        }

    return {
        "implemented": result,
        "disabled_pending_validation": DISABLED_VARGAS,
        "boundary_threshold_degrees": boundary_threshold_degrees,
        "note": (
            "Near-boundary placements can change with small birth-time or "
            "calculation differences and require manual review."
        ),
    }


def _boundary_sensitivity(
    longitude: float,
    varga: str,
    threshold: float,
) -> dict:
    _, degree = _sign_and_degree(longitude)
    if varga == "D30":
        sign_index = int(longitude // 30)
        boundaries = (
            [0, 5, 10, 18, 25, 30]
            if sign_index % 2 == 0
            else [0, 5, 12, 20, 25, 30]
        )
    else:
        divisions = VARGA_METADATA[varga]["equal_divisions"]
        part_size = 30 / divisions
        boundaries = [part_size * index for index in range(divisions + 1)]

    distance = min(abs(degree - boundary) for boundary in boundaries)
    return {
        "near_boundary": distance <= threshold,
        "distance_degrees": round(distance, 6),
        "threshold_degrees": threshold,
    }


def _sign_and_degree(longitude: float) -> tuple[int, float]:
    normalized = longitude % 360
    return int(normalized // 30), normalized % 30
