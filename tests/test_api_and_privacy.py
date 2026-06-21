import json
import os
import sys
import tempfile
import unittest
from cryptography.fernet import Fernet
from unittest.mock import patch

from fastapi.testclient import TestClient


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from api import app
from feedback import save_feedback
from legacy_migration import migrate_plaintext_sessions
from session_log import delete_session, save_session
from session_log import load_session
from secure_storage import SecureStorageConfigurationError


class ApiAndPrivacyTests(unittest.TestCase):
    def test_health_is_available_without_birth_data(self):
        client = TestClient(app)
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_status_does_not_claim_production_readiness(self):
        client = TestClient(app)
        with patch.dict(
            os.environ,
            {"SERENOVA_ADMIN_TOKEN": "admin-secret"},
            clear=True,
        ):
            response = client.get(
                "/status",
                headers={"x-api-key": "admin-secret"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["production_ready"])
        self.assertFalse(
            response.json()["checks"][
                "independent_reference_fixtures_present"
            ]
        )
        self.assertFalse(
            response.json()["checks"][
                "independent_reference_fixture_target_met"
            ]
        )
        self.assertEqual(
            response.json()["required_independent_reference_fixtures"],
            25,
        )

    def test_status_requires_external_release_approvals(self):
        client = TestClient(app)
        with patch.dict(
            os.environ,
            {
                "SERENOVA_API_TOKEN": "consultant-secret",
                "SERENOVA_ADMIN_TOKEN": "admin-secret",
                "SERENOVA_ENCRYPTION_KEY": Fernet.generate_key().decode(
                    "utf-8"
                ),
                "GROQ_API_KEY": "configured",
            },
            clear=True,
        ):
            response = client.get(
                "/status",
                headers={"x-api-key": "admin-secret"},
            )

        self.assertEqual(response.status_code, 200)
        checks = response.json()["checks"]
        self.assertFalse(response.json()["production_ready"])
        self.assertFalse(checks["expert_rule_review_approved"])
        self.assertFalse(checks["consultant_pilot_approved"])
        self.assertFalse(checks["privacy_review_approved"])
        self.assertFalse(checks["backup_recovery_drill_completed"])

    def test_status_rejects_consultant_token(self):
        client = TestClient(app)
        with patch.dict(
            os.environ,
            {
                "SERENOVA_API_TOKEN": "consultant-secret",
                "SERENOVA_ADMIN_TOKEN": "admin-secret",
            },
            clear=True,
        ):
            response = client.get(
                "/status",
                headers={"x-api-key": "consultant-secret"},
            )

        self.assertEqual(response.status_code, 401)

    def test_operational_status_detects_plaintext_sessions(self):
        import operational_status

        with tempfile.TemporaryDirectory() as directory:
            with open(
                os.path.join(directory, "legacy.json"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write("{}")
            original_log_dir = operational_status.LOG_DIR
            operational_status.LOG_DIR = directory
            try:
                with patch.dict(os.environ, {}, clear=True):
                    status = operational_status.build_operational_status()
            finally:
                operational_status.LOG_DIR = original_log_dir

        self.assertFalse(status["checks"]["no_plaintext_sessions_present"])

    def test_report_endpoint_requires_configured_authentication(self):
        client = TestClient(app)
        with patch.dict(os.environ, {}, clear=True):
            response = client.post(
                "/v1/report",
                json={
                    "birth_datetime_utc": "1990-08-15T09:00:00",
                    "latitude": 28.6139,
                    "longitude": 77.209,
                },
            )

        self.assertEqual(response.status_code, 503)

    def test_session_storage_omits_raw_name_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            import session_log

            original_log_dir = session_log.LOG_DIR
            session_log.LOG_DIR = directory
            try:
                with patch.dict(
                    os.environ,
                    {
                        "SERENOVA_PSEUDONYM_KEY": "test-key",
                        "SERENOVA_ALLOW_PLAINTEXT_SESSIONS": "true",
                    },
                    clear=True,
                ):
                    path = save_session(
                        "Sensitive Name",
                        {"date": "1990-01-01"},
                        {"report": "sample"},
                        "sample interpretation",
                    )
                with open(path, "r", encoding="utf-8") as file:
                    stored = json.load(file)
            finally:
                session_log.LOG_DIR = original_log_dir

        self.assertEqual(stored["client_name"], "")
        self.assertNotEqual(stored["client_reference"], "")
        self.assertFalse(stored["privacy"]["raw_name_stored"])

    def test_session_storage_refuses_plaintext_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            import session_log

            original_log_dir = session_log.LOG_DIR
            session_log.LOG_DIR = directory
            try:
                with patch.dict(os.environ, {}, clear=True):
                    with self.assertRaises(SecureStorageConfigurationError):
                        save_session("", {}, {}, "")
            finally:
                session_log.LOG_DIR = original_log_dir

    def test_encrypted_session_round_trip(self):
        key = Fernet.generate_key().decode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            import session_log

            original_log_dir = session_log.LOG_DIR
            session_log.LOG_DIR = directory
            try:
                with patch.dict(
                    os.environ,
                    {"SERENOVA_ENCRYPTION_KEY": key},
                    clear=True,
                ):
                    path = save_session(
                        "Encrypted Client",
                        {"date": "1990-01-01"},
                        {"report": "sample"},
                        "interpretation",
                    )
                    loaded = load_session(os.path.basename(path))
                    with open(path, "rb") as file:
                        raw_payload = file.read()
            finally:
                session_log.LOG_DIR = original_log_dir

        self.assertTrue(path.endswith(".json.enc"))
        self.assertNotIn(b"1990-01-01", raw_payload)
        self.assertEqual(loaded["birth_details"]["date"], "1990-01-01")
        self.assertTrue(loaded["privacy"]["encryption_at_rest"])

    def test_feedback_omits_free_text_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "feedback.jsonl")
            with patch.dict(
                os.environ,
                {"SERENOVA_FEEDBACK_PATH": path},
                clear=True,
            ):
                record = save_feedback(
                    "session-file.json",
                    "mixed",
                    ["too_generic"],
                    "Contains private session context",
                )

        self.assertEqual(record["note"], "")
        self.assertFalse(record["raw_note_stored"])
        self.assertEqual(record["tags"], ["too_generic"])

    def test_session_filename_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            delete_session("../private.json")

    def test_legacy_session_migration_encrypts_before_optional_delete(self):
        key = Fernet.generate_key().decode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "legacy.json")
            with open(source, "w", encoding="utf-8") as file:
                json.dump({"client_name": "Legacy"}, file)
            with patch.dict(
                os.environ,
                {"SERENOVA_ENCRYPTION_KEY": key},
                clear=True,
            ):
                result = migrate_plaintext_sessions(
                    directory,
                    delete_plaintext=True,
                )
            encrypted = source + ".enc"

            self.assertEqual(result["migrated_count"], 1)
            self.assertFalse(os.path.exists(source))
            self.assertTrue(os.path.exists(encrypted))
            with open(encrypted, "rb") as file:
                self.assertNotIn(b"Legacy", file.read())


if __name__ == "__main__":
    unittest.main()
