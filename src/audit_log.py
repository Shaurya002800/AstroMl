"""PII-minimized JSONL audit logging for API operations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone


DEFAULT_AUDIT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "audit",
    "audit.jsonl",
)


def record_audit_event(
    event: str,
    request_id: str,
    outcome: str,
    metadata: dict | None = None,
) -> None:
    path = os.getenv("SERENOVA_AUDIT_LOG_PATH", DEFAULT_AUDIT_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "request_id": request_id,
        "outcome": outcome,
        "metadata": metadata or {},
    }
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, separators=(",", ":")) + "\n")
