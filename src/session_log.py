"""
Session logging - saves each generated report to a local JSON file
for later reference.
"""

import os
import json
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sessions")


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
    safe_name = "".join(c if c.isalnum() else "_" for c in (client_name or "client")).strip("_")
    filename = f"{timestamp}_{safe_name or 'client'}.json"
    filepath = os.path.join(LOG_DIR, filename)

    session_record = {
        "session_timestamp": datetime.now().isoformat(),
        "client_name": client_name,
        "birth_details": birth_details,
        "report": report,
        "interpretation": interpretation,
    }

    with open(filepath, "w") as f:
        json.dump(session_record, f, indent=2, default=str)

    return filepath


def list_sessions() -> list:
    """Return a list of (filename, client_name, timestamp) for all saved sessions, newest first."""
    ensure_log_dir()
    sessions = []

    for fname in os.listdir(LOG_DIR):
        if fname.endswith(".json"):
            filepath = os.path.join(LOG_DIR, fname)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                sessions.append({
                    "filename": fname,
                    "client_name": data.get("client_name", "Unknown"),
                    "timestamp": data.get("session_timestamp", ""),
                })
            except (json.JSONDecodeError, KeyError):
                continue

    sessions.sort(key=lambda s: s["timestamp"], reverse=True)
    return sessions


def load_session(filename: str) -> dict:
    """Load a full session record by filename."""
    filepath = os.path.join(LOG_DIR, filename)
    with open(filepath, "r") as f:
        return json.load(f)