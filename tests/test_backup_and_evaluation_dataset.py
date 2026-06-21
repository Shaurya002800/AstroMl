import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

import backup
from backup import create_encrypted_backup, verify_backup
from evaluation.safety import evaluate_interpretation_safety


class BackupAndEvaluationTests(unittest.TestCase):
    def test_encrypted_backup_has_verified_manifest(self):
        with tempfile.TemporaryDirectory() as sessions:
            with tempfile.TemporaryDirectory() as destination:
                original_log_dir = backup.LOG_DIR
                backup.LOG_DIR = sessions
                try:
                    with open(
                        os.path.join(sessions, "sample.json.enc"),
                        "wb",
                    ) as file:
                        file.write(b"encrypted-payload")
                    path = create_encrypted_backup(destination)
                    result = verify_backup(path)
                finally:
                    backup.LOG_DIR = original_log_dir

        self.assertTrue(result["passed"])
        self.assertEqual(result["file_count"], 1)

    def test_safety_dataset_matches_expected_results(self):
        path = os.path.join(
            ROOT,
            "data",
            "evaluation",
            "safety_cases.json",
        )
        with open(path, "r", encoding="utf-8") as file:
            dataset = json.load(file)

        for case in dataset["cases"]:
            actual = evaluate_interpretation_safety(case["text"])["passed"]
            self.assertEqual(actual, case["expected_pass"], case["id"])


if __name__ == "__main__":
    unittest.main()
