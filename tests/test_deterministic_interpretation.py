import os
import sys
import unittest
from datetime import datetime


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))
sys.path.append(os.path.join(ROOT, "src", "interpretation"))

from astrology_model import create_session_model
from deterministic import generate_deterministic_interpretation
from evaluation.safety import evaluate_interpretation_safety


class DeterministicInterpretationTests(unittest.TestCase):
    def test_fallback_is_structured_and_passes_safety_scan(self):
        payload = create_session_model(
            datetime(1990, 8, 15, 9, 0),
            28.6139,
            77.209,
            datetime(2026, 6, 20, 6, 30),
        )
        text = generate_deterministic_interpretation(payload)

        self.assertIn("## Current Timing", text)
        self.assertIn("## Domain Review", text)
        self.assertIn("Consultant Note", text)
        self.assertTrue(evaluate_interpretation_safety(text)["passed"])


if __name__ == "__main__":
    unittest.main()
