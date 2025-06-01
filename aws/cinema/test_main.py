import unittest
from unittest.mock import patch, MagicMock

from main import SeatingApp


class TestSeatingApp(unittest.TestCase):

    @patch('main.AppConfiguration')
    @patch('main.ConsoleUi')
    @patch('main.SeatingPlanner')
    def setUp(self, mock_seating_planner, mock_console_ui, mock_app_config):
        """Sets up test instances with mocked dependencies."""
        self.mock_app_config = mock_app_config.return_value
        self.mock_console_ui = mock_console_ui.return_value
        self.mock_seating_planner = mock_seating_planner.return_value
        self.app = SeatingApp('./config.json')

    def test_initialization(self):
        """Tests that SeatingApp initializes properly with configuration and UI components."""
        self.assertIsNotNone(self.app.app_configuration)
        self.assertIsNotNone(self.app.console_ui)
        self.assertIsNone(self.app.seating_planner)

    @patch('builtins.input', side_effect=["Movie 1", "10", "20"])
    def test_start_application(self, mock_input):
        """Tests the start method and ensures seating planner initializes."""
        self.mock_console_ui.prompt_for_application_start_details.return_value = ("Movie 1", 10, 20)
        self.mock_seating_planner.get_seating_plan.return_value = MagicMock()

        with patch.object(self.app, '_run_event_loop') as mock_run_event_loop:
            self.app.start()
            self.assertIsNotNone(self.app.seating_planner)
            mock_run_event_loop.assert_called_once()

    @patch('builtins.input', side_effect=["3"])  # Exit option
    @patch('sys.exit')
    def test_exit_application(self, mock_sys_exit, mock_input):
        """Tests that the application exits cleanly."""
        self.app._exit_application()
        mock_sys_exit.assert_called_once_with(0)

    @patch('builtins.input', side_effect=["1"])
    def test_process_user_selection(self, mock_input):
        """Tests that user selection is processed correctly."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.display_menu.return_value = 1

        with patch.object(self.app, '_handle_booking') as mock_handle_booking:
            self.app._process_user_selection()
            mock_handle_booking.assert_called_once()

    @patch('builtins.input', side_effect=["2"])
    def test_view_booking(self, mock_input):
        """Tests that booking view is handled correctly."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.display_menu.return_value = 2

        with patch.object(self.app, '_handle_view_booking') as mock_handle_view_booking:
            self.app._process_user_selection()
            mock_handle_view_booking.assert_called_once()

    @patch('builtins.input', side_effect=["10"])
    def test_handle_booking(self, mock_input):
        """Tests seat booking functionality."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.prompt_for_number_of_seats_to_book.return_value = 10

        with patch.object(self.app.seating_planner, 'book_seats', return_value="BOOK123"):
            with patch.object(self.app.console_ui, 'prompt_for_booking_confirmation', side_effect=[""]):
                self.app._handle_booking()
                self.assertTrue(self.app.seating_planner.book_seats.called)

    @patch('builtins.input', side_effect=["BOOK123"])
    def test_handle_view_booking(self, mock_input):
        """Tests viewing booking functionality."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.prompt_for_booking_id.return_value = "BOOK123"

        with patch.object(self.app.console_ui, 'display_seating_map'):
            self.app._handle_view_booking()
            self.assertTrue(self.app.seating_planner.get_seating_plan.called)

if __name__ == '__main__':
    unittest.main()
