import unittest
from typing import Dict, Optional
from unittest.mock import patch

from app_configuration import AppConfiguration
from shared_data_models import SeatStatus, SeatingPlan
from console_ui import ConsoleUi


class TestConsoleUi(unittest.TestCase):

    def setUp(self):
        self.config = AppConfiguration()
        self.seat_status = SeatStatus.from_config(self.config)
        self.console_ui = ConsoleUi(self.config, self.seat_status)

    @patch('builtins.input', side_effect=['Test Movie 10 20'])
    def test_prompt_for_application_start_details_valid(self, mock_input):
        result = self.console_ui.prompt_for_application_start_details()
        self.assertEqual(result, ('Test Movie', 10, 20))

    @patch('builtins.input', side_effect=['', 'Test Movie -10 20', 'Test Movie 10 100', 'Test Movie 10 20'])
    def test_prompt_for_application_start_details_invalid(self, mock_input):
        result = self.console_ui.prompt_for_application_start_details()
        self.assertEqual(result, ('Test Movie', 10, 20))

    @patch('builtins.input', side_effect=['1'])
    def test_display_menu_valid_selection(self, mock_input):
        seating_plan = SeatingPlan(title="Test Movie", available_seats_count=50, plan=[])
        result = self.console_ui.display_menu(seating_plan)
        self.assertEqual(result, 1)

    @patch('builtins.input', side_effect=['5', '2'])
    def test_display_menu_invalid_selection_then_valid(self, mock_input):
        seating_plan = SeatingPlan(title="Test Movie", available_seats_count=50, plan=[])
        result = self.console_ui.display_menu(seating_plan)
        self.assertEqual(result, 2)

    @patch('builtins.input', side_effect=['5', '0', '10'])
    def test_prompt_for_number_of_seats_to_book_invalid_then_valid(self, mock_input):
        seating_plan = SeatingPlan(title="Test Movie", available_seats_count=20, plan=[])
        result = self.console_ui.prompt_for_number_of_seats_to_book(seating_plan)
        self.assertEqual(result, 10)

    @patch('builtins.input', side_effect=['confirm'])
    def test_prompt_for_booking_confirmation(self, mock_input):
        result = self.console_ui.propmpt_for_booking_confirmation()
        self.assertEqual(result, 'confirm')

    @patch('builtins.input', side_effect=['123456'])
    def test_prompt_for_booking_id(self, mock_input):
        result = self.console_ui.prompt_for_booking_id()
        self.assertEqual(result, '123456')

if __name__ == '__main__':
    unittest.main()
