import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from evaluation.safety import evaluate_interpretation_safety
from evaluation.report_quality import evaluate_report_quality
from evaluation.grounding import evaluate_interpretation_grounding
from provenance import load_provenance_registry
from report import generate_full_report
from datetime import datetime


class ProvenanceAndSafetyTests(unittest.TestCase):
    def test_provenance_registry_has_valid_source_references(self):
        registry = load_provenance_registry()

        self.assertIn("CORE_SIDEREAL_POSITIONS", registry["rules"])
        self.assertIn("SWISS_EPHEMERIS_PROGRAMMER", registry["sources"])
        for rule in registry["rules"].values():
            self.assertTrue(rule["sources"])
            self.assertTrue(rule["validation_status"])

    def test_grounded_tendency_language_passes(self):
        result = evaluate_interpretation_safety(
            "This period may support reflection. Discuss it with the client "
            "and preserve the chart caveats."
        )

        self.assertTrue(result["passed"])

    def test_explicit_negation_of_guarantee_passes(self):
        result = evaluate_interpretation_safety(
            "This is not a guaranteed prediction."
        )

        self.assertTrue(result["passed"])

    def test_absolute_and_medical_claims_fail(self):
        result = evaluate_interpretation_safety(
            "This will certainly happen. Stop taking medication."
        )

        self.assertFalse(result["passed"])
        self.assertTrue(result["findings"]["absolute_claims"])
        self.assertTrue(result["findings"]["medical_claims"])

    def test_legal_directive_fails(self):
        result = evaluate_interpretation_safety(
            "You should sue immediately."
        )

        self.assertFalse(result["passed"])
        self.assertTrue(result["findings"]["legal_directives"])

    def test_invented_yoga_and_year_fail_grounding(self):
        payload = {
            "report": {
                "yogas": [],
                "meta": {"query_date": "2026-06-20T00:00:00"},
            }
        }
        result = evaluate_interpretation_grounding(
            "Dhana Yoga guarantees an event in 2037.",
            payload,
        )

        self.assertFalse(result["passed"])
        self.assertIn("2037", result["unsupported_years"])

    def test_structured_report_quality_gate_passes(self):
        report = generate_full_report(
            datetime(1990, 8, 15, 9, 0),
            28.6139,
            77.209,
            datetime(2026, 6, 20, 6, 30),
        )
        quality = evaluate_report_quality(report)

        self.assertTrue(quality["passed"])
        self.assertTrue(all(quality["checks"].values()))


if __name__ == "__main__":
    unittest.main()
