"""
Transparent planetary-strength component profile.

This is not full Shadbala. It exposes a small set of auditable components:
dignity, combustion, D1/D9 vargottama, and directional-house alignment.
"""

try:
    from .house_analysis import get_house_number
except ImportError:
    from house_analysis import get_house_number


CLASSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
DIRECTIONAL_HOUSES = {
    "Sun": 10,
    "Moon": 4,
    "Mars": 10,
    "Mercury": 1,
    "Jupiter": 1,
    "Venus": 4,
    "Saturn": 7,
}
DIGNITY_SCORES = {
    "Exalted": 3,
    "Own Sign (Swakshetra)": 2,
    "Friendly Sign": 1,
    "Neutral": 0,
    "Enemy Sign": -1,
    "Debilitated": -2,
}


def compute_planetary_strength_profile(chart: dict, ascendant_sign: str) -> dict:
    profiles = {}

    for planet in CLASSICAL_PLANETS:
        data = chart["planets"][planet]
        house = get_house_number(data["sign"], ascendant_sign)
        dignity = data["dignity"]["status"]
        dignity_score = DIGNITY_SCORES.get(dignity, 0)
        combust = data["combustion"]["is_combust"]
        vargottama = data["sign"] == data["navamsa_sign"]
        directional_house = DIRECTIONAL_HOUSES[planet]
        directional_alignment = house == directional_house
        score = (
            dignity_score
            - (1 if combust else 0)
            + (1 if vargottama else 0)
            + (1 if directional_alignment else 0)
        )

        profiles[planet] = {
            "house": house,
            "dignity": {
                "status": dignity,
                "score": dignity_score,
            },
            "combustion": {
                "is_combust": combust,
                "score": -1 if combust else 0,
            },
            "vargottama_d1_d9": {
                "present": vargottama,
                "score": 1 if vargottama else 0,
            },
            "directional_alignment": {
                "preferred_house": directional_house,
                "present": directional_alignment,
                "score": 1 if directional_alignment else 0,
            },
            "retrograde_condition": data["is_retrograde"],
            "component_score": score,
            "label": _strength_label(score),
        }

    return {
        "method": "Serenova transparent component profile",
        "is_full_shadbala": False,
        "planets": profiles,
        "note": (
            "This is not full Shadbala and is not a probability. Retrograde "
            "motion is exposed but not assigned an automatic positive/negative score."
        ),
    }


def _strength_label(score: int) -> str:
    if score >= 4:
        return "Strong component support"
    if score >= 2:
        return "Moderate component support"
    if score >= 0:
        return "Mixed/neutral component support"
    return "Attention-heavy component profile"
