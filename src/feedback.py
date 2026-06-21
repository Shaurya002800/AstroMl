"""Privacy-minimized consultant feedback storage."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone


FEEDBACK_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "feedback",
    "consultant_feedback.jsonl",
)
ALLOWED_RATINGS = {"useful", "mixed", "not_useful"}
ALLOWED_TAGS = {
    "accurate_calculation",
    "useful_question",
    "too_generic",
    "false_positive",
    "missing_context",
    "overstated",
    "timing_mismatch",
}


def save_feedback(
    session_identifier: str,
    rating: str,
    tags: list[str] | None = None,
    note: str = "",
) -> dict:
    if rating not in ALLOWED_RATINGS:
        raise ValueError(f"Unsupported feedback rating: {rating}")
    tags = tags or []
    unknown_tags = set(tags) - ALLOWED_TAGS
    if unknown_tags:
        raise ValueError(f"Unsupported feedback tags: {sorted(unknown_tags)}")

    store_notes = os.getenv(
        "SERENOVA_STORE_FEEDBACK_NOTES", "false"
    ).lower() == "true"
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "session_reference": hashlib.sha256(
            session_identifier.encode("utf-8")
        ).hexdigest()[:16],
        "rating": rating,
        "tags": sorted(set(tags)),
        "note": note.strip() if store_notes else "",
        "raw_note_stored": store_notes,
    }
    path = os.getenv("SERENOVA_FEEDBACK_PATH", FEEDBACK_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, separators=(",", ":")) + "\n")
    return record
