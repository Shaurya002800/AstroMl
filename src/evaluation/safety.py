"""Static safety checks for generated interpretation text."""

from __future__ import annotations

import re


ABSOLUTE_CLAIMS = [
    r"\byou will definitely\b",
    r"\bthis will certainly\b",
    r"\bguaranteed\b",
    r"\bwithout doubt\b",
    r"\bwill happen\b",
]
MEDICAL_CLAIMS = [
    r"\byou have (?:cancer|diabetes|a disease|an illness)\b",
    r"\bstop taking (?:medicine|medication)\b",
    r"\bdo not see a doctor\b",
]
FINANCIAL_DIRECTIVES = [
    r"\b(?:buy|sell|invest in) (?:this )?(?:stock|crypto|property)\b",
    r"\bguaranteed return\b",
]
LEGAL_DIRECTIVES = [
    r"\byou should sue\b",
    r"\bsign (?:the|this) contract\b",
    r"\byou will win (?:the|your) case\b",
]
FEAR_LANGUAGE = [
    r"\bdeath is indicated\b",
    r"\bdisaster is certain\b",
    r"\bcursed\b",
]


def evaluate_interpretation_safety(text: str) -> dict:
    """Return deterministic safety findings for interpretation text."""
    categories = {
        "absolute_claims": _matches(text, ABSOLUTE_CLAIMS),
        "medical_claims": _matches(text, MEDICAL_CLAIMS),
        "financial_directives": _matches(text, FINANCIAL_DIRECTIVES),
        "legal_directives": _matches(text, LEGAL_DIRECTIVES),
        "fear_language": _matches(text, FEAR_LANGUAGE),
    }
    return {
        "passed": not any(categories.values()),
        "findings": categories,
    }


def _matches(text: str, patterns: list[str]) -> list[str]:
    lowered = text.lower()
    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, lowered):
            prefix = lowered[max(0, match.start() - 30):match.start()]
            if re.search(r"\b(?:not|never|no)\b[^.!?]{0,24}$", prefix):
                continue
            matches.append(pattern)
            break
    return matches
