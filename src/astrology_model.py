"""
Deterministic consultation model.

This module turns the computed astrology report into a structured brief for the
consultant. It does not invent astrological facts and does not call an LLM.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from report import generate_full_report


UNCERTAINTY_NOTE = (
    "Use this as computed support for the consultant, not as a guaranteed "
    "prediction. Final interpretation should consider client context and the "
    "consultant's judgment."
)

TIME_PRECISION_NOTES = {
    "exact": "Birth time marked exact by the consultant.",
    "within_15_min": (
        "Birth time is approximate within 15 minutes; ascendant degree, "
        "divisional charts, and close timing windows need review."
    ),
    "within_1_hour": (
        "Birth time is approximate within 1 hour; houses, divisional charts, "
        "and some dasha timing should be treated cautiously."
    ),
    "unknown": (
        "Birth time is unknown; ascendant, houses, divisional charts, and "
        "house-based yogas are not reliable without rectification."
    ),
}


def build_consultation_brief(report: dict[str, Any], time_precision: str = "exact") -> dict[str, Any]:
    """
    Build a structured, auditable consultation brief from a computed report.

    The brief is designed to be consumed by both the Streamlit UI and the LLM
    interpretation layer. Every point is derived from the report data.
    """
    ashtakavarga = report["ashtakavarga"]["sarva_by_house"]
    planets = report["planets"]
    dasha = report["current_dasha"]
    yogas = report.get("yogas", [])

    strong_houses = []
    attention_houses = []
    for house_num, data in ashtakavarga.items():
        strength = data["strength"].lower()
        entry = {
            "house": int(house_num),
            "sign": data["sign"],
            "bindus": data["bindus"],
            "strength": data["strength"],
            "house_name": data["house_name"],
            "significations": data["house_significations"],
        }
        if strength.startswith("very strong") or strength.startswith("strong"):
            strong_houses.append(entry)
        elif strength.startswith("weak") or strength.startswith("very weak"):
            attention_houses.append(entry)

    dignities = []
    attention_planets = []
    for planet, data in planets.items():
        status = data["dignity"]
        item = {
            "planet": planet,
            "sign": data["sign"],
            "degree": data["degree"],
            "nakshatra": data["nakshatra"],
            "pada": data["pada"],
            "dignity": status,
            "note": data["dignity_note"],
            "navamsa_sign": data["navamsa_sign"],
            "dasamsa_sign": data["dasamsa_sign"],
        }
        if status in {"Exalted", "Own Sign (Swakshetra)"}:
            dignities.append(item)
        elif status in {"Debilitated", "Enemy Sign"}:
            attention_planets.append(item)

    d10_planets_by_house = report["d10_career_chart"]["planets_by_house"]
    career_focus = [
        {
            "house": int(house),
            "planets": planets_in_house,
            "note": (
                "D10 placement for consultant review; interpret with D1, "
                "10th lord, dasha, and client context."
            ),
        }
        for house, planets_in_house in sorted(d10_planets_by_house.items(), key=lambda kv: int(kv[0]))
    ]

    session_questions = _build_session_questions(dasha, strong_houses, attention_houses, yogas)

    return {
        "model_version": "0.1.0",
        "method": "deterministic_jyotish_rules_plus_guarded_llm_synthesis",
        "assumptions": {
            "ayanamsa": "Lahiri",
            "planetary_engine": "Swiss Ephemeris via pyswisseph",
            "house_logic": "Whole-sign/rashi logic for rule engine unless otherwise noted",
            "time_precision": time_precision,
            "time_precision_note": TIME_PRECISION_NOTES.get(time_precision, TIME_PRECISION_NOTES["exact"]),
        },
        "uncertainty_note": UNCERTAINTY_NOTE,
        "dasha_focus": {
            "mahadasha_lord": dasha["mahadasha"]["lord"],
            "mahadasha_start": dasha["mahadasha"]["start"],
            "mahadasha_end": dasha["mahadasha"]["end"],
            "antardasha_lord": dasha["antardasha"]["lord"] if dasha.get("antardasha") else None,
            "antardasha_start": dasha["antardasha"]["start"] if dasha.get("antardasha") else None,
            "antardasha_end": dasha["antardasha"]["end"] if dasha.get("antardasha") else None,
        },
        "notable_strengths": {
            "strong_houses": strong_houses,
            "strong_planets": dignities,
            "detected_yogas": yogas,
        },
        "attention_flags": {
            "weaker_houses": attention_houses,
            "challenging_planets": attention_planets,
        },
        "career_review": {
            "d10_ascendant_sign": report["d10_career_chart"]["ascendant_sign"],
            "planets_by_house": career_focus,
        },
        "session_questions": session_questions,
    }


def create_session_model(
    birth_datetime_utc: datetime,
    lat: float,
    lon: float,
    query_datetime: datetime | None = None,
    time_precision: str = "exact",
) -> dict[str, Any]:
    """
    Full deterministic model payload for one consultation.
    """
    report = generate_full_report(birth_datetime_utc, lat, lon, query_datetime)
    brief = build_consultation_brief(report, time_precision=time_precision)
    return {
        "report": report,
        "consultation_brief": brief,
    }


def _build_session_questions(
    dasha: dict[str, Any],
    strong_houses: list[dict[str, Any]],
    attention_houses: list[dict[str, Any]],
    yogas: list[dict[str, Any]],
) -> list[str]:
    questions = [
        (
            f"Current period is {dasha['mahadasha']['lord']} mahadasha"
            + (
                f" with {dasha['antardasha']['lord']} antardasha"
                if dasha.get("antardasha")
                else ""
            )
            + ". Ask what themes have become most active recently."
        )
    ]

    if strong_houses:
        top = sorted(strong_houses, key=lambda h: h["bindus"], reverse=True)[:2]
        for house in top:
            questions.append(
                f"House {house['house']} is {house['strength']}. Ask about current developments related to {house['significations']}"
            )

    if attention_houses:
        weakest = sorted(attention_houses, key=lambda h: h["bindus"])[:2]
        for house in weakest:
            questions.append(
                f"House {house['house']} needs attention. Ask gently about effort, delays, or support needed around {house['significations']}"
            )

    if yogas:
        questions.append(
            "For detected yogas, ask whether the client has seen these themes in real life before emphasizing them."
        )

    return questions
