"""Limited deterministic grounding checks for generated interpretation text."""

from __future__ import annotations

import json
import re


KNOWN_YOGA_TERMS = {
    "Gajakesari",
    "Budhaditya",
    "Raja",
    "Chandra-Mangal",
    "Neecha Bhanga",
    "Pancha Mahapurusha",
    "Kemadruma",
    "Ruchaka",
    "Bhadra",
    "Hamsa",
    "Malavya",
    "Sasa",
}


def evaluate_interpretation_grounding(text: str, model_payload: dict) -> dict:
    serialized = json.dumps(model_payload, default=str)
    present_yogas = {
        yoga["name"]
        for yoga in model_payload.get("report", {}).get("yogas", [])
    }
    unsupported_yoga_terms = sorted(
        term
        for term in KNOWN_YOGA_TERMS
        if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)
        and not any(term.lower() in name.lower() for name in present_yogas)
    )

    mentioned_years = set(re.findall(r"\b(?:19|20)\d{2}\b", text))
    unsupported_years = sorted(
        year for year in mentioned_years if year not in serialized
    )

    return {
        "passed": not unsupported_yoga_terms and not unsupported_years,
        "unsupported_yoga_terms": unsupported_yoga_terms,
        "unsupported_years": unsupported_years,
        "note": (
            "This is a limited grounding check. It does not prove that every "
            "natural-language claim follows from the structured report."
        ),
    }
