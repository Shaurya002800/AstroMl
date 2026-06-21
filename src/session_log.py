"""
Session logging - saves each generated report to a local JSON file
for later reference.
"""

import os
import json
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta

try:
    from .secure_storage import decode_record, encode_record
except ImportError:
    from secure_storage import decode_record, encode_record

LOG_DIR = os.getenv(
    "SERENOVA_SESSION_DIR",
    os.path.join(os.path.dirname(__file__), "..", "data", "sessions"),
)


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def save_session(client_name: str, birth_details: dict, report: dict, interpretation: str) -> str:
    """
    Save a session record to a JSON file.

    Args:
        client_name: name entered for the client (can be empty)
        birth_details: dict with date, time, city, lat, lon, utc_datetime
        report: the full computed report dict
        interpretation: the LLM-generated interpretation text

    Returns:
        The filepath of the saved session file.
    """
    ensure_log_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    client_reference = _client_reference(client_name)
    store_client_name = os.getenv(
        "SERENOVA_STORE_CLIENT_NAME", "false"
    ).lower() == "true"

    session_record = {
        "session_timestamp": datetime.now().isoformat(),
        "client_name": client_name if store_client_name else "",
        "client_reference": client_reference,
        "privacy": {
            "raw_name_stored": store_client_name,
            "encryption_at_rest": bool(
                os.getenv("SERENOVA_ENCRYPTION_KEY")
            ),
        },
        "birth_details": birth_details,
        "report": report,
        "interpretation": interpretation,
    }

    payload, extension = encode_record(session_record)
    filename = f"{timestamp}_{client_reference}{extension}"
    filepath = os.path.join(LOG_DIR, filename)
    with open(filepath, "wb") as file:
        file.write(payload)

    return filepath


def list_sessions() -> list:
    """Return a list of (filename, client_name, timestamp) for all saved sessions, newest first."""
    ensure_log_dir()
    purge_expired_sessions()
    sessions = []

    for fname in os.listdir(LOG_DIR):
        if fname.endswith(".json") or fname.endswith(".json.enc"):
            filepath = os.path.join(LOG_DIR, fname)
            try:
                with open(filepath, "rb") as file:
                    data = decode_record(file.read(), fname)
                sessions.append({
                    "filename": fname,
                    "client_name": data.get("client_name", "Unknown"),
                    "client_reference": data.get("client_reference", "legacy"),
                    "timestamp": data.get("session_timestamp", ""),
                })
            except (json.JSONDecodeError, KeyError, RuntimeError):
                continue

    sessions.sort(key=lambda s: s["timestamp"], reverse=True)
    return sessions


def load_session(filename: str) -> dict:
    """Load a full session record by filename."""
    filepath = _safe_session_path(filename)
    with open(filepath, "rb") as file:
        return decode_record(file.read(), filename)


def delete_session(filename: str) -> None:
    """Delete one local session record."""
    os.remove(_safe_session_path(filename))


def purge_expired_sessions() -> int:
    """Delete local session files older than configured retention days."""
    raw_days = os.getenv("SERENOVA_SESSION_RETENTION_DAYS")
    if not raw_days:
        return 0
    retention_days = int(raw_days)
    if retention_days < 1:
        raise ValueError("SERENOVA_SESSION_RETENTION_DAYS must be at least 1.")

    cutoff = datetime.now() - timedelta(days=retention_days)
    removed = 0
    for filename in os.listdir(LOG_DIR):
        if not (
            filename.endswith(".json")
            or filename.endswith(".json.enc")
        ):
            continue
        path = os.path.join(LOG_DIR, filename)
        modified = datetime.fromtimestamp(os.path.getmtime(path))
        if modified < cutoff:
            os.remove(path)
            removed += 1
    return removed


def _client_reference(client_name: str) -> str:
    key = os.getenv("SERENOVA_PSEUDONYM_KEY")
    normalized = (client_name or "").strip().lower()
    if key and normalized:
        digest = hmac.new(
            key.encode("utf-8"),
            normalized.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return digest[:12]
    return uuid.uuid4().hex[:12]


def _safe_session_path(filename: str) -> str:
    if os.path.basename(filename) != filename:
        raise ValueError("Invalid session filename.")
    if not (
        filename.endswith(".json")
        or filename.endswith(".json.enc")
    ):
        raise ValueError("Unsupported session filename.")
    return os.path.join(LOG_DIR, filename)
