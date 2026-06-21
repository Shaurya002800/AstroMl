import os
import sys
import unittest
from copy import deepcopy


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from validation.reference_charts import (
    load_reference_fixtures,
    run_reference_validation,
    validate_reference_fixture,
)


class ReferenceValidationTests(unittest.TestCase):
    def test_internal_reference_fixture_passes_and_is_not_overclaimed(self):
        result = run_reference_validation()

        self.assertTrue(result["passed"])
        self.assertGreaterEqual(result["fixture_count"], 4)
        self.assertEqual(result["independently_verified_fixture_count"], 0)
        self.assertIn(
            "do not constitute independent accuracy validation",
            result["note"],
        )

    def test_unknown_verification_status_is_rejected(self):
        fixture = deepcopy(load_reference_fixtures()[0])
        fixture["verification_status"] = "independent-ish"

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported verification_status",
        ):
            validate_reference_fixture(fixture)

    def test_independent_status_requires_evidence_metadata(self):
        fixture = deepcopy(load_reference_fixtures()[0])
        fixture["verification_status"] = "external_software_verified"

        with self.assertRaisesRegex(
            ValueError,
            "missing verification evidence",
        ):
            validate_reference_fixture(fixture)


if __name__ == "__main__":
    unittest.main()
