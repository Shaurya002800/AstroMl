"""Aggregate privacy-minimized consultant feedback for pilot review."""

from __future__ import annotations

import json
from collections import Counter


def load_feedback_records(path: str) -> list[dict]:
    records = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))
    return records


def summarize_feedback(records: list[dict]) -> dict:
    rating_counts = Counter(
        record["rating"]
        for record in records
    )
    tag_counts = Counter(
        tag
        for record in records
        for tag in record.get("tags", [])
    )
    total = len(records)
    return {
        "session_count": total,
        "rating_counts": dict(sorted(rating_counts.items())),
        "tag_counts": dict(sorted(tag_counts.items())),
        "useful_or_mixed_rate": _rate(
            rating_counts["useful"] + rating_counts["mixed"],
            total,
        ),
        "not_useful_rate": _rate(
            rating_counts["not_useful"],
            total,
        ),
        "false_positive_rate": _rate(
            tag_counts["false_positive"],
            total,
        ),
        "overstatement_rate": _rate(
            tag_counts["overstated"],
            total,
        ),
        "timing_mismatch_rate": _rate(
            tag_counts["timing_mismatch"],
            total,
        ),
        "note": (
            "These are consultant workflow metrics, not scientific prediction "
            "accuracy. Review tagged sessions qualitatively before release."
        ),
    }


def _rate(count: int, total: int) -> float | None:
    if total == 0:
        return None
    return round(count / total, 4)
