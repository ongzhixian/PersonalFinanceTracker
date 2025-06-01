import unittest
from unittest.mock import patch, MagicMock
from main import SeatingApp


class TestSeatingApp(unittest.TestCase):
    """Unit tests for SeatingApp class."""

    @patch("main.AppConfiguration")
    @patch("main.ConsoleUi")
    @patch("main.SeatingPlanner")
    def setUp(self, mock_seating_planner, mock_console_ui, mock_app_configuration):
        """Set up mocks and initialize SeatingApp instance."""
        self.mock_console_ui = mock_console_ui.return_value
        self.mock_seating_planner = mock_seating_planner.return_value
        self.mock_app_configuration = mock_app_configuration.return_value

        self.app = SeatingApp("./test_configuration.json")
        self.app.console_ui = self.mock_console_ui
        self.app.seating_planner = self.mock_seating_planner

    def test_start_initializes_correctly(self):
        """Tests whether the application starts correctly with expected values."""
        self.mock_console_ui.prompt_for_application_start_details.return_value = ("Movie Title", 10, 10)
        self.app.start()
        self.mock_seating_planner.assert_called_once_with("Movie Title", 10, 10)

    def test_handle_booking_successful(self):
        """Tests successful seat booking."""
        self.mock_console_ui.prompt_for_number_of_seats_to_book.return_value = 2
        self.mock_seating_planner.book_seats.return_value = "BOOK123"
        self.mock_console_ui.prompt_for_booking_confirmation.return_value = ""

        with patch("builtins.print") as mocked_print:
            self.app._handle_booking()
            mocked_print.assert_called_with("Booking confirmed. Booking ID: BOOK123")

    def test_handle_booking_cancel_and_retry(self):
        """Tests seat booking cancellation and retry flow."""
        self.mock_console_ui.prompt_for_number_of_seats_to_book.return_value = 2
        self.mock_seating_planner.book_seats.return_value = "BOOK123"
        self.mock_console_ui.prompt_for_booking_confirmation.side_effect = ["B2", ""]

        self.app._handle_booking()
        self.mock_seating_planner.cancel_booking.assert_called_once_with("BOOK123")

    def test_handle_view_booking_successful(self):
        """Tests viewing a booking successfully."""
        self.mock_console_ui.prompt_for_booking_id.return_value = "BOOK123"
        self.mock_seating_planner.get_seating_plan.return_value = {"A1": "Booked", "A2": "Available"}

        self.app._handle_view_booking()
        self.mock_seating_planner.get_seating_plan.assert_called_once_with("BOOK123")

    def test_handle_view_booking_invalid_id(self):
        """Tests invalid booking ID scenario."""
        self.mock_console_ui.prompt_for_booking_id.return_value = "INVALID"
        self.mock_seating_planner.get_seating_plan.return_value = None

        with patch("builtins.print") as mocked_print:
            self.app._handle_view_booking()
            mocked_print.assert_called_with("Booking ID not found. Please try again.")

    def test_exit_application(self):
        """Tests application exit."""
        with patch("sys.exit") as mocked_exit:
            self.app._exit_application()
            mocked_exit.assert_called_with(0)


if __name__ == "__main__":
    unittest.main()
