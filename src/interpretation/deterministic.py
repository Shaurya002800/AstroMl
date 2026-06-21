"""Deterministic Markdown fallback built only from consultation-brief data."""

from __future__ import annotations


def generate_deterministic_interpretation(model_payload: dict) -> str:
    brief = model_payload["consultation_brief"]
    lines = [
        "# Consultant Interpretation",
        "",
        "## Overview",
        brief["uncertainty_note"],
        "",
        "## Current Timing",
        _dasha_line(brief["dasha_focus"]),
        "",
    ]

    active_domains = sorted(
        brief.get("domain_reviews", {}).values(),
        key=lambda review: review["activation_score"],
        reverse=True,
    )
    if active_domains:
        lines.extend(["## Domain Review", ""])
        for review in active_domains:
            lines.extend([
                f"### {review['label']}",
                (
                    f"- Structural picture: {review['support_level']} "
                    f"(internal score {review['support_score']})."
                ),
                (
                    f"- Current activation: {review['activation_level']} "
                    f"(internal score {review['activation_score']})."
                ),
                f"- Session prompt: {review['consultant_prompt']}",
                f"- Caveat: {review['caveat']}",
                "",
            ])

    sensitivity = brief.get("birth_time_sensitivity", {})
    if sensitivity and not sensitivity.get("stable_within_15_minutes", True):
        lines.extend([
            "## Birth-Time Sensitivity",
            (
                "Several house or divisional-chart outputs change within "
                "15 minutes. Review the sensitivity table before emphasizing "
                "house- or varga-specific conclusions."
            ),
            "",
        ])

    yogas = brief.get("notable_strengths", {}).get("detected_yogas", [])
    if yogas:
        lines.extend(["## Yoga Flags", ""])
        for yoga in yogas:
            assessment = yoga.get("strength_assessment", {})
            lines.extend([
                f"- **{yoga['name']}**: {assessment.get('label', 'Review required')}.",
                f"  Caveat: {yoga.get('caveat', 'Manual review required.')}",
            ])
        lines.append("")

    questions = brief.get("session_questions", [])
    if questions:
        lines.extend(["## Questions for the Session", ""])
        lines.extend(f"- {question}" for question in questions)
        lines.append("")

    lines.extend([
        "## Consultant Note",
        (
            "This interpretation is deterministic computed support. It does not "
            "replace consultant judgment or professional medical, legal, or "
            "financial advice."
        ),
    ])
    return "\n".join(lines)


def _dasha_line(dasha: dict) -> str:
    parts = [f"{dasha['mahadasha_lord']} Mahadasha"]
    if dasha.get("antardasha_lord"):
        parts.append(f"{dasha['antardasha_lord']} Antardasha")
    if dasha.get("pratyantar_lord"):
        parts.append(f"{dasha['pratyantar_lord']} Pratyantar")
    return (
        "The active computed sequence is "
        + ", ".join(parts)
        + ". Treat it as timing context, not as a certain event."
    )
