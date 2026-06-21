import os
import sys
import unittest
from datetime import datetime, timedelta


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
from extended_divisional_charts import (
    build_extended_divisional_charts,
    get_chaturthamsa_sign,
    get_drekkana_sign,
    get_dwadashamsa_sign,
    get_hora_sign,
    get_trimsamsa_sign,
)
from functional_roles import classify_functional_roles
from house_analysis import analyze_house_lordships, compute_parashari_aspects
from planetary_conditions import annotate_planetary_conditions, angular_separation
from report import generate_full_report
from rashi_drishti import compute_rashi_drishti, signs_aspected_by
from sensitivity import compute_birth_time_sensitivity
from planetary_strength import compute_planetary_strength_profile
from transits import (
    compute_sign_window,
    compute_station_window,
    compute_transit_report,
)
from yogas import check_kemadruma_yoga, detect_all_yogas


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.birth_dt_utc = datetime(1990, 8, 15, 9, 0)
        self.lat = 28.6139
        self.lon = 77.2090

    def test_report_contains_expected_top_level_sections(self):
        report = generate_full_report(self.birth_dt_utc, self.lat, self.lon)

        self.assertIn("ascendant", report)
        self.assertIn("release", report)
        self.assertIn("planets", report)
        self.assertIn("current_dasha", report)
        self.assertIn("ashtakavarga", report)
        self.assertIn("yogas", report)
        self.assertIn("d10_career_chart", report)
        self.assertIn("functional_roles", report)
        self.assertIn("dispositor_analysis", report)
        self.assertIn("transits", report)
        self.assertIn("domain_reviews", report)
        self.assertIn("extended_divisional_charts", report)
        self.assertIn("birth_time_sensitivity", report)
        self.assertIn("planetary_strength", report)
        self.assertIn("rashi_drishti", report)

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

    def test_mahadasha_timeline_covers_120_years_after_birth(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        timeline = compute_mahadasha_timeline(
            self.birth_dt_utc,
            chart["planets"]["Moon"]["longitude"],
        )
        required_end = self.birth_dt_utc + timedelta(days=120 * 365.25)

        self.assertGreaterEqual(timeline[-1]["end"], required_end)
        self.assertGreaterEqual(len(timeline), 10)

    def test_current_dasha_supports_late_life_query(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        result = get_current_dasha(
            self.birth_dt_utc,
            chart["planets"]["Moon"]["longitude"],
            datetime(2109, 8, 15, 9, 0),
        )

        self.assertNotIn("error", result)
        self.assertIsNotNone(result["mahadasha"])

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

    def test_hora_uses_odd_even_solar_lunar_order(self):
        self.assertEqual(get_hora_sign(10.0), "Leo")
        self.assertEqual(get_hora_sign(20.0), "Cancer")
        self.assertEqual(get_hora_sign(40.0), "Cancer")
        self.assertEqual(get_hora_sign(50.0), "Leo")

    def test_drekkana_uses_first_fifth_and_ninth_signs(self):
        self.assertEqual(get_drekkana_sign(5.0), "Aries")
        self.assertEqual(get_drekkana_sign(15.0), "Leo")
        self.assertEqual(get_drekkana_sign(25.0), "Sagittarius")

    def test_chaturthamsa_and_dwadashamsa_progressions(self):
        self.assertEqual(get_chaturthamsa_sign(30.0), "Taurus")
        self.assertEqual(get_chaturthamsa_sign(38.0), "Leo")
        self.assertEqual(get_dwadashamsa_sign(3.0), "Taurus")

    def test_trimsamsa_nonuniform_odd_even_mappings(self):
        self.assertEqual(get_trimsamsa_sign(4.0), "Aries")
        self.assertEqual(get_trimsamsa_sign(6.0), "Aquarius")
        self.assertEqual(get_trimsamsa_sign(33.0), "Taurus")
        self.assertEqual(get_trimsamsa_sign(36.0), "Virgo")

    def test_extended_vargas_expose_boundary_sensitivity_and_disabled_charts(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        vargas = build_extended_divisional_charts(chart)

        self.assertEqual(
            set(vargas["implemented"]),
            {"D2", "D3", "D4", "D12", "D30"},
        )
        self.assertEqual(
            set(vargas["disabled_pending_validation"]),
            {"D16", "D24", "D60"},
        )
        for varga in vargas["implemented"].values():
            self.assertIn("ascendant_boundary_sensitivity", varga)

    def test_detected_yogas_include_planets_and_strength_evidence(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        chart = annotate_chart_with_dignity_and_navamsa(chart)
        chart = annotate_planetary_conditions(chart)
        yogas = detect_all_yogas(
            chart,
            chart["ascendant"]["sign"],
            [
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn",
                "Aquarius", "Pisces",
            ],
        )

        for yoga in yogas:
            self.assertIn("involved_planets", yoga)
            self.assertIn("simplified", yoga)
            self.assertIn("strength_assessment", yoga)
            self.assertIn("label", yoga["strength_assessment"])

    def test_kemadruma_cancellation_is_not_hidden(self):
        zodiac = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn",
            "Aquarius", "Pisces",
        ]
        chart = {
            "planets": {
                "Moon": {"sign": "Aries"},
                "Sun": {"sign": "Gemini"},
                "Mars": {"sign": "Gemini"},
                "Mercury": {"sign": "Gemini"},
                "Jupiter": {"sign": "Gemini"},
                "Venus": {"sign": "Gemini"},
                "Saturn": {"sign": "Gemini"},
                "Rahu": {"sign": "Gemini"},
                "Ketu": {"sign": "Gemini"},
            }
        }
        result = check_kemadruma_yoga(chart, "Aries", zodiac)

        self.assertTrue(result["present"])
        self.assertEqual(
            result["cancellation_status"],
            "cancellation_indicated",
        )
        self.assertTrue(result["cancellation_evidence"])

    def test_birth_time_sensitivity_reports_changed_vargas(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        sensitivity = compute_birth_time_sensitivity(
            self.birth_dt_utc,
            self.lat,
            self.lon,
            chart,
        )

        self.assertEqual(
            sensitivity["offsets_minutes"],
            [-60, -30, -15, 15, 30, 60],
        )
        self.assertFalse(sensitivity["stable_within_15_minutes"])
        self.assertIn(
            "D9",
            sensitivity["scenarios"]["15"]["changed_ascendant_vargas"],
        )
        self.assertTrue(
            sensitivity["scenarios"]["60"]["ascendant_sign_changed"]
        )

    def test_planetary_strength_is_transparent_and_not_shadbala(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        chart = annotate_chart_with_dignity_and_navamsa(chart)
        chart = annotate_planetary_conditions(chart)
        profile = compute_planetary_strength_profile(
            chart,
            chart["ascendant"]["sign"],
        )

        self.assertFalse(profile["is_full_shadbala"])
        self.assertEqual(len(profile["planets"]), 7)
        for data in profile["planets"].values():
            self.assertIn("dignity", data)
            self.assertIn("combustion", data)
            self.assertIn("vargottama_d1_d9", data)
            self.assertIn("directional_alignment", data)

    def test_rashi_drishti_movable_fixed_and_dual_rules(self):
        self.assertEqual(
            signs_aspected_by("Aries"),
            ["Leo", "Scorpio", "Aquarius"],
        )
        self.assertEqual(
            signs_aspected_by("Taurus"),
            ["Cancer", "Libra", "Capricorn"],
        )
        self.assertEqual(
            signs_aspected_by("Gemini"),
            ["Virgo", "Sagittarius", "Pisces"],
        )

    def test_rashi_drishti_reports_planets_carried_by_signs(self):
        chart = compute_chart(self.birth_dt_utc, self.lat, self.lon)
        result = compute_rashi_drishti(
            chart, chart["ascendant"]["sign"]
        )

        self.assertEqual(result["system"], "Jaimini-style rashi drishti")
        self.assertTrue(result["contacts"])
        for contact in result["contacts"]:
            self.assertIn(contact["source_house"], range(1, 13))
            self.assertIn(contact["target_house"], range(1, 13))


if __name__ == "__main__":
    unittest.main()
