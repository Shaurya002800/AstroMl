"""
Evidence-based domain synthesis.

Support and activation are deliberately separate:
- support reflects structural chart factors;
- activation reflects current dasha/transit emphasis.
Neither is an event-probability score.
"""

from knowledge_base.domain_definitions import DOMAIN_DEFINITIONS


STRONG_DIGNITIES = {"Exalted", "Own Sign (Swakshetra)"}
SUPPORTIVE_DIGNITIES = {"Friendly Sign"}
CHALLENGING_DIGNITIES = {"Debilitated", "Enemy Sign"}


def build_domain_reviews(report: dict) -> dict:
    """Build bounded domain reviews from existing deterministic evidence."""
    return {
        domain: _review_domain(report, definition)
        for domain, definition in DOMAIN_DEFINITIONS.items()
    }


def _review_domain(report: dict, definition: dict) -> dict:
    support_evidence = []
    attention_evidence = []
    activation_evidence = []
    support_score = 0
    activation_score = 0

    for house in definition["houses"]:
        house_key = str(house)
        strength = report["ashtakavarga"]["sarva_by_house"][house_key]
        house_points = _ashtakavarga_points(strength["bindus"])
        support_score += house_points
        evidence = {
            "type": "house_strength",
            "house": house,
            "bindus": strength["bindus"],
            "strength": strength["strength"],
        }
        if house_points >= 0:
            support_evidence.append(evidence)
        else:
            attention_evidence.append(evidence)

        lordship = report["house_lordships"]["houses"][house_key]
        lord_data = report["planets"][lordship["lord"]]
        dignity_points = _dignity_points(lord_data["dignity"])
        support_score += dignity_points
        lord_evidence = {
            "type": "house_lord",
            "house": house,
            "lord": lordship["lord"],
            "lord_house": lordship["lord_placement"]["house"],
            "dignity": lord_data["dignity"],
            "combust": lord_data["combustion"]["is_combust"],
        }
        if dignity_points >= 0 and not lord_data["combustion"]["is_combust"]:
            support_evidence.append(lord_evidence)
        else:
            attention_evidence.append(lord_evidence)
        if lord_data["combustion"]["is_combust"]:
            support_score -= 1

    active_lords = [
        report["current_dasha"][level]["lord"]
        for level in ("mahadasha", "antardasha", "pratyantar")
        if report["current_dasha"].get(level)
    ]
    functional_roles = report["functional_roles"]["roles"]
    for level, lord in zip(
        ("mahadasha", "antardasha", "pratyantar"),
        active_lords,
    ):
        role = functional_roles.get(lord, {"owned_houses": []})
        owned_domain_houses = sorted(
            set(role["owned_houses"])
            & set(definition["houses"])
        )
        if owned_domain_houses or lord in definition["planets"]:
            activation_score += 1
            activation_evidence.append({
                "type": "dasha",
                "level": level,
                "lord": lord,
                "owned_domain_houses": owned_domain_houses,
                "is_domain_planet": lord in definition["planets"],
            })

    for planet, transit in report["transits"]["slow_transit_focus"].items():
        if transit["house_from_natal_ascendant"] in definition["houses"]:
            activation_score += 1
            activation_evidence.append({
                "type": "slow_transit",
                "planet": planet,
                "house": transit["house_from_natal_ascendant"],
                "sign": transit["sign"],
                "motion": transit["motion"],
            })

    return {
        "label": definition["label"],
        "houses_reviewed": definition["houses"],
        "planets_reviewed": definition["planets"],
        "divisional_chart": definition["divisional_chart"],
        "support_level": _support_level(support_score),
        "support_score": support_score,
        "activation_level": _activation_level(activation_score),
        "activation_score": activation_score,
        "supporting_evidence": support_evidence,
        "attention_evidence": attention_evidence,
        "activation_evidence": activation_evidence,
        "consultant_prompt": definition["consultant_prompt"],
        "caveat": (
            "This is an evidence summary, not an event prediction or probability. "
            "Conflicting factors must remain visible in the session."
        ),
    }


def _ashtakavarga_points(bindus: int) -> int:
    if bindus >= 30:
        return 2
    if bindus >= 25:
        return 1
    if bindus < 20:
        return -1
    return 0


def _dignity_points(dignity: str) -> int:
    if dignity in STRONG_DIGNITIES:
        return 2
    if dignity in SUPPORTIVE_DIGNITIES:
        return 1
    if dignity in CHALLENGING_DIGNITIES:
        return -1
    return 0


def _support_level(score: int) -> str:
    if score >= 8:
        return "Strong structural support"
    if score >= 3:
        return "Moderate structural support"
    if score >= 0:
        return "Mixed structural support"
    return "Attention-heavy structural picture"


def _activation_level(score: int) -> str:
    if score >= 5:
        return "Highly active"
    if score >= 3:
        return "Active"
    if score >= 1:
        return "Some current activation"
    return "No major activation detected by current rule set"
