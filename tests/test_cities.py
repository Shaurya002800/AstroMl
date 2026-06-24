import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from knowledge_base.cities import (
    INDIAN_LOCATIONS,
    get_city_coordinates,
    get_city_list,
    get_state_list,
)


class CityDatabaseTests(unittest.TestCase):
    def test_all_states_and_union_territories_are_available(self):
        self.assertEqual(len(get_state_list()), 36)
        self.assertIn("Uttar Pradesh", get_state_list())
        self.assertIn("Andaman and Nicobar Islands", get_state_list())
        self.assertIn(
            "Dadra and Nagar Haveli and Daman and Diu",
            get_state_list(),
        )

    def test_database_has_broad_city_coverage(self):
        city_count = sum(
            len(cities)
            for cities in INDIAN_LOCATIONS.values()
        )
        self.assertGreaterEqual(city_count, 150)
        self.assertIn("New Delhi", get_city_list("Delhi"))
        self.assertIn("Mumbai", get_city_list("Maharashtra"))
        self.assertIn("Bengaluru", get_city_list("Karnataka"))

    def test_bijnor_district_urban_local_bodies_are_available(self):
        expected_bijnor_towns = {
            "Afzalgarh",
            "Barhapur",
            "Bijnor",
            "Chandpur",
            "Dhampur",
            "Haldaur",
            "Jalalabad, Bijnor",
            "Jhalu",
            "Kiratpur",
            "Mandawar",
            "Nagina",
            "Najibabad",
            "Nehtaur",
            "Noorpur",
            "Sahanpur",
            "Sahaspur",
            "Seohara",
            "Sherkot",
        }
        self.assertTrue(
            expected_bijnor_towns.issubset(
                set(get_city_list("Uttar Pradesh"))
            )
        )
        self.assertEqual(
            get_city_coordinates("Bijnor", "Uttar Pradesh"),
            (29.3724, 78.1358),
        )

    def test_all_coordinates_are_valid(self):
        for state, cities in INDIAN_LOCATIONS.items():
            for city, coordinates in cities.items():
                with self.subTest(state=state, city=city):
                    latitude, longitude = coordinates
                    self.assertGreaterEqual(latitude, -90)
                    self.assertLessEqual(latitude, 90)
                    self.assertGreaterEqual(longitude, -180)
                    self.assertLessEqual(longitude, 180)
                    self.assertEqual(
                        get_city_coordinates(city, state),
                        coordinates,
                    )

    def test_unknown_state_or_city_returns_no_coordinates(self):
        self.assertIsNone(
            get_city_coordinates("Unknown City", "Delhi")
        )
        self.assertEqual(get_city_list("Unknown State"), [])


if __name__ == "__main__":
    unittest.main()
