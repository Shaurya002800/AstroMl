import os
import sys
import unittest
from datetime import datetime


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))
sys.path.append(os.path.join(ROOT, "src", "calculations"))

from ashtakavarga import compute_sarvashtakavarga
from chart import compute_chart
from dasha import (
    compute_antardasha,
    compute_mahadasha_timeline,
    compute_pratyantar_dasha,
    get_current_dasha,
)
from dignity import annotate_chart_with_dignity_and_navamsa
from dispositors import analyze_dispositors
from functional_roles import classify_functional_roles
from house_analysis import analyze_house_lordships, compute_parashari_aspects
from planetary_conditions import annotate_planetary_conditions, angular_separation
from report import generate_full_report
from transits import (
    compute_sign_window,
    compute_station_window,
    compute_transit_report,
)


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.birth_dt_utc = datetime(1990, 8, 15, 9, 0)
        self.lat = 28.6139
        self.lon = 77.2090

    def test_report_contains_expected_top_level_sections(self):
        report = generate_full_report(self.birth_dt_utc, self.lat, self.lon)

        self.assertIn("ascendant", report)
        self.assertIn("planets", report)
        self.assertIn("current_dasha", report)
        self.assertIn("ashtakavarga", report)
        self.assertIn("yogas", report)
        self.assertIn("d10_career_chart", report)
        self.assertIn("functional_roles", report)
        self.assertIn("dispositor_analysis", report)
        self.assertIn("transits", report)
        self.assertIn("domain_reviews", report)

    def test_sarvashtakavarga_total_is_classical_337(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        chart = annotate_chart_with_dignity_and_navamsa(chart)
        sav = compute_sarvashtakavarga(chart, chart["ascendant"]["sign"])

        self.assertEqual(sav["total_sum"], 337)

    def test_all_reported_planets_have_required_interpretation_fields(self):
        report = generate_full_report(self.birth_dt_utc, self.lat, self.lon)

        required = {
            "sign",
            "degree",
            "nakshatra",
            "pada",
            "dignity",
            "dignity_note",
            "motion",
            "is_retrograde",
            "longitude_speed",
            "combustion",
            "navamsa_sign",
            "dasamsa_sign",
            "saptamsa_sign",
        }
        for data in report["planets"].values():
            self.assertTrue(required.issubset(data.keys()))

    def test_angular_separation_wraps_at_zero_aries(self):
        self.assertEqual(angular_separation(359.0, 1.0), 2.0)

    def test_house_lordships_cover_all_houses(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        chart = annotate_chart_with_dignity_and_navamsa(chart)
        chart = annotate_planetary_conditions(chart)
        analysis = analyze_house_lordships(chart, chart["ascendant"]["sign"])

        self.assertEqual(set(analysis["houses"].keys()), set(range(1, 13)))
        for data in analysis["houses"].values():
            self.assertIn(data["lord_placement"]["house"], range(1, 13))

    def test_parashari_aspect_counts_match_standard_pattern(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        aspects = compute_parashari_aspects(chart, chart["ascendant"]["sign"])
        counts = {}
        for aspect in aspects["aspects"]:
            counts[aspect["planet"]] = counts.get(aspect["planet"], 0) + 1

        self.assertEqual(counts["Mars"], 3)
        self.assertEqual(counts["Jupiter"], 3)
        self.assertEqual(counts["Saturn"], 3)
        self.assertEqual(counts["Sun"], 1)
        self.assertFalse(aspects["node_aspects_included"])

    def test_nested_dasha_periods_partition_parent_period(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        moon_longitude = chart["planets"]["Moon"]["longitude"]
        maha = compute_mahadasha_timeline(
            self.birth_dt_utc, moon_longitude
        )[0]
        antars = compute_antardasha(
            maha["lord"], maha["start"], maha["duration_years"]
        )
        pratyantars = compute_pratyantar_dasha(
            antars[0]["lord"],
            antars[0]["start"],
            antars[0]["duration_years"],
        )

        self.assertEqual(antars[0]["start"], maha["start"])
        self.assertEqual(antars[-1]["end"], maha["end"])
        self.assertEqual(pratyantars[0]["start"], antars[0]["start"])
        self.assertEqual(pratyantars[-1]["end"], antars[0]["end"])

    def test_current_dasha_includes_pratyantar(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        result = get_current_dasha(
            self.birth_dt_utc,
            chart["planets"]["Moon"]["longitude"],
            datetime(2026, 6, 18),
        )

        self.assertIsNotNone(result["mahadasha"])
        self.assertIsNotNone(result["antardasha"])
        self.assertIsNotNone(result["pratyantar"])

    def test_taurus_ascendant_marks_saturn_as_yogakaraka(self):
        roles = classify_functional_roles("Taurus")["roles"]

        self.assertEqual(roles["Saturn"]["owned_houses"], [9, 10])
        self.assertTrue(roles["Saturn"]["is_yogakaraka"])
        self.assertEqual(
            roles["Saturn"]["functional_tendency"],
            "Strongly supportive potential",
        )

    def test_functional_roles_preserve_mixed_ownership(self):
        roles = classify_functional_roles("Scorpio")["roles"]

        self.assertEqual(roles["Mars"]["owned_houses"], [1, 6])
        self.assertEqual(
            roles["Mars"]["functional_tendency"],
            "Mixed with supportive potential",
        )
        self.assertIn(6, roles["Mars"]["dusthana_houses"])

    def test_dispositor_analysis_detects_final_dispositors(self):
        chart = {
            "planets": {
                "Sun": {"sign": "Leo"},
                "Moon": {"sign": "Cancer"},
                "Mars": {"sign": "Aries"},
                "Mercury": {"sign": "Gemini"},
                "Jupiter": {"sign": "Sagittarius"},
                "Venus": {"sign": "Taurus"},
                "Saturn": {"sign": "Capricorn"},
                "Rahu": {"sign": "Aries"},
                "Ketu": {"sign": "Libra"},
            }
        }
        analysis = analyze_dispositors(chart)

        self.assertEqual(
            analysis["chains"]["Rahu"]["terminal_dispositor"],
            "Mars",
        )
        self.assertEqual(
            analysis["chains"]["Ketu"]["terminal_dispositor"],
            "Venus",
        )
        self.assertEqual(analysis["cycles"], [])

    def test_dispositor_analysis_detects_mutual_cycle(self):
        chart = {
            "planets": {
                "Sun": {"sign": "Leo"},
                "Moon": {"sign": "Taurus"},
                "Mars": {"sign": "Aries"},
                "Mercury": {"sign": "Gemini"},
                "Jupiter": {"sign": "Sagittarius"},
                "Venus": {"sign": "Cancer"},
                "Saturn": {"sign": "Capricorn"},
                "Rahu": {"sign": "Taurus"},
                "Ketu": {"sign": "Cancer"},
            }
        }
        analysis = analyze_dispositors(chart)

        self.assertIn(["Moon", "Venus"], analysis["cycles"])
        self.assertEqual(
            analysis["chains"]["Moon"]["terminal_type"],
            "cycle",
        )

    def test_transits_map_all_planets_to_natal_houses(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        transit_report = compute_transit_report(
            datetime(2026, 6, 20, 6, 30),
            chart,
            chart["ascendant"]["sign"],
        )

        self.assertEqual(len(transit_report["positions"]), 9)
        for data in transit_report["positions"].values():
            self.assertIn(data["house_from_natal_ascendant"], range(1, 13))
            self.assertIn(data["house_from_natal_moon"], range(1, 13))
        self.assertEqual(
            set(transit_report["slow_transit_focus"]),
            {"Jupiter", "Saturn", "Rahu", "Ketu"},
        )

    def test_slow_planet_sign_window_contains_query_date(self):
        query = datetime(2026, 6, 20, 6, 30)
        window = compute_sign_window("Jupiter", query)

        self.assertEqual(window["sign"], "Cancer")
        self.assertLess(
            datetime.fromisoformat(window["entered_sign_utc"]),
            query,
        )
        self.assertGreater(
            datetime.fromisoformat(window["leaves_sign_utc"]),
            query,
        )

    def test_station_window_reports_motion_and_future_station(self):
        query = datetime(2026, 6, 20, 6, 30)
        window = compute_station_window("Saturn", query)

        self.assertEqual(window["motion_at_query"], "Direct")
        self.assertIsNotNone(window["next_station_utc"])
        self.assertGreater(
            datetime.fromisoformat(window["next_station_utc"]),
            query,
        )

    def test_domain_reviews_separate_support_from_activation(self):
        report = generate_full_report(
            self.birth_dt_utc,
            self.lat,
            self.lon,
            datetime(2026, 6, 20, 6, 30),
        )
        reviews = report["domain_reviews"]

        self.assertEqual(
            set(reviews),
            {"career", "relationships", "finance", "education", "wellbeing"},
        )
        for review in reviews.values():
            self.assertIsInstance(review["support_score"], int)
            self.assertIsInstance(review["activation_score"], int)
            self.assertIn("not an event prediction", review["caveat"])


if __name__ == "__main__":
    unittest.main()
