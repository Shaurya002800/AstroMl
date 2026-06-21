import os
import sys
import unittest
from datetime import datetime


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from astrology_model import build_consultation_brief
from presentation import (
    build_plain_language_report,
    render_plain_language_markdown,
)
from report import generate_full_report


class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        report = generate_full_report(
            datetime(1990, 8, 15, 9, 0),
            28.6139,
            77.209,
            query_datetime=datetime(2026, 6, 21, 6, 30),
        )
        cls.payload = {
            "report": report,
            "consultation_brief": build_consultation_brief(
                report,
                time_precision="within_15_min",
            ),
        }

    def test_all_languages_preserve_same_domain_order(self):
        summaries = {
            language: build_plain_language_report(
                self.payload,
                language,
            )
            for language in ("en", "hi", "hinglish")
        }
        expected_order = [
            item["key"]
            for item in summaries["en"]["priority_areas"]
        ]

        self.assertEqual(
            [item["key"] for item in summaries["hi"]["priority_areas"]],
            expected_order,
        )
        self.assertEqual(
            [
                item["key"]
                for item in summaries["hinglish"]["priority_areas"]
            ],
            expected_order,
        )

    def test_summary_is_conclusion_first_without_internal_scores(self):
        summary = build_plain_language_report(self.payload, "en")
        markdown = render_plain_language_markdown(summary)

        self.assertIn("Main picture", markdown)
        self.assertIn("Important life areas", markdown)
        self.assertNotIn("support_score", markdown)
        self.assertNotIn("activation_score", markdown)
        self.assertNotIn("bindus", markdown.lower())

    def test_hindi_and_hinglish_are_rendered_deterministically(self):
        hindi = build_plain_language_report(self.payload, "hi")
        hinglish = build_plain_language_report(self.payload, "hinglish")

        self.assertEqual(hindi["title"], "आपकी ज्योतिषीय रिपोर्ट")
        self.assertIn("करियर और काम", {
            area["title"] for area in hindi["priority_areas"]
        })
        self.assertEqual(
            hinglish["title"],
            "Aapki Astrology Summary",
        )
        self.assertIn("Career aur kaam", {
            area["title"] for area in hinglish["priority_areas"]
        })

    def test_unknown_language_is_rejected(self):
        with self.assertRaises(ValueError):
            build_plain_language_report(self.payload, "fr")


if __name__ == "__main__":
    unittest.main()
