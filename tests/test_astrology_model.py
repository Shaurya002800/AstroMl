import os
import sys
import unittest
from datetime import datetime


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from astrology_model import build_consultation_brief, create_session_model
from report import generate_full_report


class AstrologyModelTests(unittest.TestCase):
    def setUp(self):
        self.birth_dt_utc = datetime(1990, 8, 15, 9, 0)
        self.lat = 28.6139
        self.lon = 77.2090

    def test_consultation_brief_preserves_guardrails(self):
        report = generate_full_report(self.birth_dt_utc, self.lat, self.lon)
        brief = build_consultation_brief(report, time_precision="within_15_min")

        self.assertEqual(brief["model_version"], "0.3.0")
        self.assertEqual(brief["assumptions"]["ayanamsa"], "Lahiri")
        self.assertIn("not as a guaranteed prediction", brief["uncertainty_note"])
        self.assertIn("15 minutes", brief["assumptions"]["time_precision_note"])
        self.assertGreaterEqual(len(brief["session_questions"]), 1)
        self.assertIn("pratyantar_lord", brief["dasha_focus"])
        self.assertIn("aspect_review", brief)
        self.assertIn("functional_role_review", brief)
        self.assertIn("dispositor_review", brief)
        self.assertIn("transit_review", brief)

    def test_create_session_model_returns_report_and_brief(self):
        payload = create_session_model(self.birth_dt_utc, self.lat, self.lon)

        self.assertIn("report", payload)
        self.assertIn("consultation_brief", payload)
        self.assertEqual(
            payload["consultation_brief"]["dasha_focus"]["mahadasha_lord"],
            payload["report"]["current_dasha"]["mahadasha"]["lord"],
        )


if __name__ == "__main__":
    unittest.main()
