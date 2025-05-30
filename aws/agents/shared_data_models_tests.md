# test_app_configuration.py

import json
import os
import tempfile
import unittest

from app_configuration import AppConfiguration
from shared_data_models import SeatStatusEnum, Seat, SeatingPlan, MenuOption


class TestSeatStatus(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8")
        self.config_data = {
            "seat_statuses": {
                "available": "O",
                "booked": "B",
                "proposed": "P"
            }
        }
        json.dump(self.config_data, self.temp_file)
        self.temp_file.close()
        AppConfiguration.reset_instance()

    def tearDown(self):
        os.unlink(self.temp_file.name)
        AppConfiguration.reset_instance()

    def test_seat_status_from_config(self):
        config = AppConfiguration(self.temp_file.name)
        status = SeatStatusEnum.from_config(config)
        self.assertEqual(status.AVAILABLE, "O")
        self.assertEqual(status.BOOKED, "B")
        self.assertEqual(status.PROPOSED, "P")

    def test_seat_status_defaults(self):
        # Remove 'proposed'
        data = {
            "seat_statuses": {
                "available": "A",
                "booked": "B"
            }
        }
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            json.dump(data, f)
        config = AppConfiguration(self.temp_file.name)
        status = SeatStatusEnum.from_config(config)
        self.assertEqual(status.AVAILABLE, "A")
        self.assertEqual(status.BOOKED, "B")
        self.assertEqual(status.PROPOSED, "P")  # Default

class TestSeatingPlan(unittest.TestCase):
    def test_seating_plan(self):
        seats = [
            [Seat(0, 0, "O"), Seat(0, 1, "B")],
            [Seat(1, 0, "O"), Seat(1, 1, "P")]
        ]
        plan = SeatingPlan(title="Test Plan", plan=seats, available_seats_count=2)
        self.assertEqual(plan.title, "Test Plan")
        self.assertEqual(plan.available_seats_count, 2)
        self.assertEqual(plan.plan[0][0].status, "O")
        self.assertEqual(plan.plan[1][1].status, "P")

class TestMenuOption(unittest.TestCase):
    def test_enum(self):
        self.assertEqual(MenuOption.BOOK_SEATS.name, "BOOK_SEATS")
        self.assertTrue(isinstance(MenuOption.EXIT, MenuOption))

if __name__ == "__main__":
    unittest.main()