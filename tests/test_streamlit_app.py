import os
import sys
import tempfile
import unittest
from datetime import date, time
from unittest.mock import patch

from cryptography.fernet import Fernet
from streamlit.testing.v1 import AppTest


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

import session_log


class StreamlitAppTests(unittest.TestCase):
    def test_consultant_workflow_generates_and_encrypts_session(self):
        with tempfile.TemporaryDirectory() as directory:
            original_log_dir = session_log.LOG_DIR
            session_log.LOG_DIR = directory
            try:
                with patch.dict(
                    os.environ,
                    {
                        "SERENOVA_ENCRYPTION_KEY": (
                            Fernet.generate_key().decode("utf-8")
                        ),
                        "SERENOVA_PSEUDONYM_KEY": "ui-smoke-test",
                    },
                    clear=True,
                ):
                    app = AppTest.from_file(
                        os.path.join(ROOT, "src", "app.py"),
                        default_timeout=60,
                    ).run()
                    app.text_input[0].input("Verification Client")
                    app.date_input[0].set_value(date(1990, 8, 15))
                    app.time_input[0].set_value(time(14, 30))
                    app.selectbox[2].select("Delhi").run(timeout=60)
                    app.selectbox[3].select("New Delhi")
                    app.button[0].click().run(timeout=60)
            finally:
                session_log.LOG_DIR = original_log_dir

            files = os.listdir(directory)
            self.assertEqual([str(item) for item in app.exception], [])
            self.assertIn(
                "Chart calculated successfully",
                [item.value for item in app.success],
            )
            self.assertTrue(any(
                "saved securely" in item.value
                for item in app.caption
            ))
            self.assertIn(
                "Your Astrology Summary",
                [item.value for item in app.header],
            )
            self.assertTrue(any(
                "Important life areas" == item.value
                for item in app.subheader
            ))
            self.assertEqual(len(files), 1)
            self.assertTrue(files[0].endswith(".json.enc"))
            with open(os.path.join(directory, files[0]), "rb") as file:
                encrypted_payload = file.read()
            self.assertNotIn(b"1990-08-15", encrypted_payload)

    def test_language_switch_reuses_computed_report(self):
        with tempfile.TemporaryDirectory() as directory:
            original_log_dir = session_log.LOG_DIR
            session_log.LOG_DIR = directory
            try:
                with patch.dict(
                    os.environ,
                    {
                        "SERENOVA_ENCRYPTION_KEY": (
                            Fernet.generate_key().decode("utf-8")
                        ),
                    },
                    clear=True,
                ):
                    app = AppTest.from_file(
                        os.path.join(ROOT, "src", "app.py"),
                        default_timeout=60,
                    ).run()
                    app.selectbox[2].select("Delhi").run(timeout=60)
                    app.selectbox[3].select("New Delhi")
                    app.button[0].click().run(timeout=60)
                    file_count = len(os.listdir(directory))
                    app.session_state["report_language_label"] = "हिंदी"
                    app.run(timeout=60)
            finally:
                session_log.LOG_DIR = original_log_dir

            self.assertEqual([str(item) for item in app.exception], [])
            self.assertIn(
                "आपकी ज्योतिषीय रिपोर्ट",
                [item.value for item in app.header],
            )
            self.assertEqual(len(os.listdir(directory)), file_count)

    def test_missing_place_does_not_calculate_with_a_hidden_default(self):
        app = AppTest.from_file(
            os.path.join(ROOT, "src", "app.py"),
            default_timeout=60,
        ).run()
        app.button[0].click().run(timeout=60)

        self.assertTrue(any(
            "Select a state and city" in item.value
            for item in app.error
        ))
        self.assertNotIn(
            "Chart calculated successfully",
            [item.value for item in app.success],
        )


if __name__ == "__main__":
    unittest.main()
