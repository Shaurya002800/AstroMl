"""Encrypted-session backup creation and integrity verification."""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone

try:
    from .session_log import LOG_DIR
except ImportError:
    from session_log import LOG_DIR


def create_encrypted_backup(destination_dir: str) -> str:
    os.makedirs(destination_dir, exist_ok=True)
    session_files = sorted(
        filename
        for filename in os.listdir(LOG_DIR)
        if filename.endswith(".json.enc")
    )
    plaintext_files = [
        filename
        for filename in os.listdir(LOG_DIR)
        if filename.endswith(".json")
    ]
    if plaintext_files:
        raise ValueError(
            "Refusing backup while plaintext session files are present."
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(destination_dir, f"serenova_sessions_{timestamp}.zip")
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": {},
    }

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in session_files:
            file_path = os.path.join(LOG_DIR, filename)
            with open(file_path, "rb") as file:
                payload = file.read()
            manifest["files"][filename] = hashlib.sha256(payload).hexdigest()
            archive.writestr(f"sessions/{filename}", payload)
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, indent=2).encode("utf-8"),
        )

    verification = verify_backup(path)
    if not verification["passed"]:
        raise RuntimeError(f"Backup verification failed: {verification}")
    return path


def verify_backup(path: str) -> dict:
    findings = []
    with zipfile.ZipFile(path, "r") as archive:
        manifest = json.loads(archive.read("manifest.json"))
        for filename, expected_hash in manifest["files"].items():
            payload = archive.read(f"sessions/{filename}")
            actual_hash = hashlib.sha256(payload).hexdigest()
            findings.append({
                "filename": filename,
                "passed": actual_hash == expected_hash,
            })
    return {
        "passed": all(item["passed"] for item in findings),
        "file_count": len(findings),
        "findings": findings,
    }
