"""Cross-section consistency checks for structured reports."""

from __future__ import annotations

from datetime import datetime


def evaluate_report_consistency(report: dict) -> dict:
    checks = {
        "dasha_periods_contain_query": _dasha_contains_query(report),
        "slow_transits_match_positions": _slow_transits_match(report),
        "domain_labels_match_scores": _domain_labels_match(report),
        "cancelled_yogas_are_mitigated": _cancelled_yogas_mitigated(report),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
    }


def _dasha_contains_query(report: dict) -> bool:
    query = datetime.fromisoformat(report["meta"]["query_date"])
    for level in ("mahadasha", "antardasha", "pratyantar"):
        period = report["current_dasha"].get(level)
        if not period:
            continue
        if not (
            datetime.fromisoformat(period["start"])
            <= query
            < datetime.fromisoformat(period["end"])
        ):
            return False
    return True


def _slow_transits_match(report: dict) -> bool:
    transits = report["transits"]
    return all(
        data == transits["positions"][planet]
        for planet, data in transits["slow_transit_focus"].items()
    )


def _domain_labels_match(report: dict) -> bool:
    for review in report["domain_reviews"].values():
        score = review["activation_score"]
        expected = (
            "Highly active" if score >= 5
            else "Active" if score >= 3
            else "Some current activation" if score >= 1
            else "No major activation detected by current rule set"
        )
        if review["activation_level"] != expected:
            return False
    return True


def _cancelled_yogas_mitigated(report: dict) -> bool:
    return all(
        yoga.get("cancellation_status") != "cancellation_indicated"
        or "mitigated" in yoga["strength_assessment"]["label"].lower()
        for yoga in report.get("yogas", [])
    )
