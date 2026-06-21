"""Deterministic quality checks for structured astrology reports."""

from __future__ import annotations

try:
    from .consistency import evaluate_report_consistency
except ImportError:
    from evaluation.consistency import evaluate_report_consistency


def evaluate_report_quality(report: dict) -> dict:
    checks = {
        "ashtakavarga_total_337": (
            report.get("ashtakavarga", {}).get("validation_total") == 337
        ),
        "provenance_present": bool(report.get("provenance", {}).get("rules")),
        "domain_caveats_present": _domain_caveats_present(report),
        "yoga_evidence_complete": _yoga_evidence_complete(report),
        "disabled_vargas_not_calculated": _disabled_vargas_not_calculated(report),
        "transit_caveat_present": bool(
            report.get("transits", {}).get("note")
        ),
        "cross_section_consistency": evaluate_report_consistency(
            report
        )["passed"],
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "note": (
            "These checks validate report structure and guardrails, not the "
            "scientific truth or outcome accuracy of astrology."
        ),
    }


def _domain_caveats_present(report: dict) -> bool:
    reviews = report.get("domain_reviews", {})
    return bool(reviews) and all(
        review.get("caveat")
        for review in reviews.values()
    )


def _yoga_evidence_complete(report: dict) -> bool:
    return all(
        yoga.get("source")
        and yoga.get("caveat")
        and yoga.get("strength_assessment")
        for yoga in report.get("yogas", [])
    )


def _disabled_vargas_not_calculated(report: dict) -> bool:
    vargas = report.get("extended_divisional_charts", {})
    implemented = set(vargas.get("implemented", {}))
    disabled = set(vargas.get("disabled_pending_validation", {}))
    return implemented.isdisjoint(disabled)
