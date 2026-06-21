import os
import sys
import unittest
from datetime import datetime

import pytz


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from time_utils import local_datetime_to_utc


class TimeUtilsTests(unittest.TestCase):
    def test_unambiguous_ist_conversion(self):
        result = local_datetime_to_utc(
            datetime(1990, 8, 15, 14, 30),
            "Asia/Kolkata",
        )
        self.assertEqual(result, datetime(1990, 8, 15, 9, 0))

    def test_ambiguous_new_york_time_requires_policy(self):
        local = datetime(2024, 11, 3, 1, 30)
        with self.assertRaises(pytz.AmbiguousTimeError):
            local_datetime_to_utc(local, "America/New_York")

        earlier = local_datetime_to_utc(
            local, "America/New_York", "earlier"
        )
        later = local_datetime_to_utc(
            local, "America/New_York", "later"
        )
        self.assertEqual(earlier, datetime(2024, 11, 3, 5, 30))
        self.assertEqual(later, datetime(2024, 11, 3, 6, 30))

    def test_nonexistent_new_york_time_can_shift_forward(self):
        local = datetime(2024, 3, 10, 2, 30)
        with self.assertRaises(pytz.NonExistentTimeError):
            local_datetime_to_utc(local, "America/New_York")

        shifted = local_datetime_to_utc(
            local, "America/New_York", "shift_forward"
        )
        self.assertEqual(shifted, datetime(2024, 3, 10, 7, 0))


if __name__ == "__main__":
    unittest.main()
