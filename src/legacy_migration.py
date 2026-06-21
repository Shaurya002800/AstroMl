"""Migrate legacy plaintext session JSON files to encrypted records."""

from __future__ import annotations

import json
import os

try:
    from .secure_storage import encode_record, encryption_enabled
except ImportError:
    from secure_storage import encode_record, encryption_enabled


def migrate_plaintext_sessions(
    session_dir: str,
    delete_plaintext: bool = False,
) -> dict:
    if not encryption_enabled():
        raise RuntimeError(
            "SERENOVA_ENCRYPTION_KEY is required for migration."
        )

    migrated = []
    skipped = []
    for filename in sorted(os.listdir(session_dir)):
        if not filename.endswith(".json"):
            continue
        source_path = os.path.join(session_dir, filename)
        target_path = source_path + ".enc"
        if os.path.exists(target_path):
            skipped.append({
                "filename": filename,
                "reason": "encrypted target already exists",
            })
            continue

        with open(source_path, "r", encoding="utf-8") as file:
            record = json.load(file)
        payload, extension = encode_record(record)
        if extension != ".json.enc":
            raise RuntimeError("Migration did not produce encrypted output.")
        with open(target_path, "wb") as file:
            file.write(payload)

        migrated.append({
            "source": filename,
            "target": os.path.basename(target_path),
            "plaintext_deleted": delete_plaintext,
        })
        if delete_plaintext:
            os.remove(source_path)

    return {
        "migrated_count": len(migrated),
        "migrated": migrated,
        "skipped": skipped,
    }
