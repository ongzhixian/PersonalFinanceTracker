import unittest
from unittest.mock import patch
from app_configuration import AppConfiguration
from shared_data_models import Seat, SeatStatus, SeatingPlan
from console_ui import ConsoleUi

class TestConsoleUi(unittest.TestCase):

    def setUp(self):
        self.config = AppConfiguration(raw_config={})
        self.seat_status = SeatStatus.from_config(self.config)
        self.console_ui = ConsoleUi(self.config, self.seat_status)

    @patch('builtins.input', side_effect=['Test Movie 10 20'])
    def test_prompt_for_application_start_details_valid(self, mock_input):
        result = self.console_ui.prompt_for_application_start_details()
        self.assertEqual(result, ('Test Movie', 10, 20))

    @patch('builtins.input', side_effect=['', 'Test Movie -10 20', 'Test Movie 10 100', 'Test Movie 10 20'])
    def test_prompt_for_application_start_details_invalid(self, mock_input):
        result = self.console_ui.prompt_for_application_start_details()
        self.assertEqual(result, ('Test Movie', 10, 20))  # Ensure the final valid input is returned

    @patch('builtins.input', side_effect=['1'])
    def test_display_menu_valid_selection(self, mock_input):
        seat_matrix = [[Seat(row=0, col=i, status='available') for i in range(5)]]
        seating_plan = SeatingPlan(title="Test Movie", available_seats_count=5, plan=seat_matrix)
        result = self.console_ui.display_menu(seating_plan)
        self.assertEqual(result, 1)

    @patch('builtins.input', side_effect=['5', 'invalid', '2'])
    def test_display_menu_invalid_selection_then_valid(self, mock_input):
        seat_matrix = [[Seat(row=0, col=i, status='available') for i in range(5)]]
        seating_plan = SeatingPlan(title="Test Movie", available_seats_count=5, plan=seat_matrix)
        result = self.console_ui.display_menu(seating_plan)
        self.assertEqual(result, 2)

    @patch('builtins.input', side_effect=['10', '0', '5'])
    def test_prompt_for_number_of_seats_to_book_invalid_then_valid(self, mock_input):
        # Creating a valid seating plan with seats to prevent initialization errors
        seat_matrix = [[Seat(row=0, col=i, status='available') for i in range(5)]]
        seating_plan = SeatingPlan(title="Test Movie", available_seats_count=5, plan=seat_matrix)
        result = self.console_ui.prompt_for_number_of_seats_to_book(seating_plan)
        self.assertEqual(result, 5)

    @patch('builtins.input', side_effect=['confirm'])
    def test_prompt_for_booking_confirmation(self, mock_input):
        result = self.console_ui.prompt_for_booking_confirmation()  # Fixed typo
        self.assertEqual(result, 'confirm')

    @patch('builtins.input', side_effect=['123456'])
    def test_prompt_for_booking_id(self, mock_input):
        result = self.console_ui.prompt_for_booking_id()
        self.assertEqual(result, '123456')

    def test_prompt_for_application_start_details_prompt(self):
        expected_prompt = "\nPlease define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n> "

        config = AppConfiguration()  # Mock or provide an actual AppConfiguration instance
        console_ui = ConsoleUi(config)

        with patch("builtins.input", side_effect=KeyboardInterrupt) as mock_input:
            try:
                console_ui.prompt_for_application_start_details()
            except KeyboardInterrupt:
                pass  # Stop infinite loop safely

            mock_input.assert_called_with(expected_prompt)

    @patch("builtins.input", side_effect=["1"])
    def test_display_menu_prompt(self, mock_input):
        seat_matrix = [[Seat(row=0, col=i, status='available') for i in range(5)]]
        seating_plan = SeatingPlan(title="Test Movie", available_seats_count=5, plan=seat_matrix)

        with patch("builtins.print") as mock_print:
            self.console_ui.display_menu(seating_plan)

        mock_input.assert_called_with("Please enter your selection (1-3):\n> ")

if __name__ == '__main__':
    unittest.main()

