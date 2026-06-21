"""Authenticated encryption helpers for local session records."""

from __future__ import annotations

import json
import os

from cryptography.fernet import Fernet, InvalidToken


class SecureStorageConfigurationError(RuntimeError):
    """Raised when sensitive storage is attempted without an approved policy."""


def encryption_enabled() -> bool:
    return bool(os.getenv("SERENOVA_ENCRYPTION_KEY"))


def plaintext_storage_allowed() -> bool:
    return os.getenv(
        "SERENOVA_ALLOW_PLAINTEXT_SESSIONS", "false"
    ).lower() == "true"


def encode_record(record: dict) -> tuple[bytes, str]:
    payload = json.dumps(record, indent=2, default=str).encode("utf-8")
    key = os.getenv("SERENOVA_ENCRYPTION_KEY")
    if key:
        return Fernet(key.encode("utf-8")).encrypt(payload), ".json.enc"
    if plaintext_storage_allowed():
        return payload, ".json"
    raise SecureStorageConfigurationError(
        "Session storage requires SERENOVA_ENCRYPTION_KEY. "
        "Plaintext development storage must be explicitly enabled with "
        "SERENOVA_ALLOW_PLAINTEXT_SESSIONS=true."
    )


def decode_record(payload: bytes, filename: str) -> dict:
    if filename.endswith(".json.enc"):
        key = os.getenv("SERENOVA_ENCRYPTION_KEY")
        if not key:
            raise SecureStorageConfigurationError(
                "SERENOVA_ENCRYPTION_KEY is required to read encrypted sessions."
            )
        try:
            payload = Fernet(key.encode("utf-8")).decrypt(payload)
        except InvalidToken as error:
            raise SecureStorageConfigurationError(
                "Unable to decrypt session with the configured key."
            ) from error
    elif not plaintext_storage_allowed():
        raise SecureStorageConfigurationError(
            "Plaintext session reading is disabled."
        )
    return json.loads(payload.decode("utf-8"))
