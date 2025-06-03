import unittest
from unittest.mock import patch, MagicMock, call

from main import SeatingApp, MenuOption


class TestMenuOption(unittest.TestCase):
    """Tests for MenuOption enumeration."""

    def test_enum_values(self):
        """Verifies MenuOption members are correctly assigned."""
        self.assertEqual(MenuOption.BOOK_SEATS.name, "BOOK_SEATS")
        self.assertEqual(MenuOption.VIEW_BOOKING.name, "VIEW_BOOKING")
        self.assertEqual(MenuOption.EXIT.name, "EXIT")


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
        """Tests start method. Ensures seating planner initializes."""
        self.mock_console_ui.prompt_for_application_start_details.return_value = ("Movie 1", 10, 20)
        self.mock_seating_planner.get_seating_plan.return_value = MagicMock()

        with patch.object(self.app, '_run_event_loop') as mock_run_event_loop:
            self.app.start()
            self.assertIsNotNone(self.app.seating_planner)
            mock_run_event_loop.assert_called_once()

    def test_start_application_with_exception(self):
        """Tests start method when exception occurred."""
        with (patch.object(self.app.console_ui, 'prompt_for_application_start_details', side_effect=Exception("Simulated error")),
              patch('sys.exit') as mock_sys_exit):
            with patch("builtins.print") as mock_print:
                self.app.start()
        mock_print.assert_has_calls([call('Error initializing application: Simulated error')])
        mock_sys_exit.assert_called_once()

    # Handle booking

    def test_on_select_booking_call_handle_booking(self):
        """Tests that user selection is processed correctly."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.display_menu.return_value = 1

        with patch.object(self.app, '_handle_booking') as mock_handle_booking:
            self.app._process_user_selection()
            mock_handle_booking.assert_called_once()

    def test_handle_booking_when_user_enter_blank_book_seats_not_called(self):
        """Tests return to main menu functionality when seat booking."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.prompt_for_number_of_seats_to_book.return_value = None

        with patch.object(self.app.seating_planner, 'book_seats') as mock_book_seats:
            mock_book_seats.assert_not_called()


    # @patch('builtins.input', side_effect=["10"])
    def test_handle_booking_with_no_seating_changes(self):
        """Tests seat booking functionality."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.prompt_for_number_of_seats_to_book.return_value = 10

        self.app.seating_planner.cancel_booking = MagicMock()
        with patch.object(self.app.seating_planner, 'book_seats', return_value="BOOK123") as mock_book_seats:
            with patch.object(self.app.console_ui, 'prompt_for_booking_confirmation', side_effect=[""]):
                self.app._handle_booking()
                mock_book_seats.assert_called_once()
                self.app.seating_planner.cancel_booking.assert_not_called()
                # self.assertTrue(self.app.seating_planner.book_seats.called)

    def test_handle_booking_with_seating_changes(self):
        """Tests seat booking functionality."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.prompt_for_number_of_seats_to_book.return_value = 10

        self.app.seating_planner.cancel_booking = MagicMock()
        with patch.object(self.app.seating_planner, 'book_seats', return_value="BOOK123") as mock_book_seats:
            with patch.object(self.app.console_ui, 'prompt_for_booking_confirmation', side_effect=["B3"]):
                self.app._handle_booking()
                mock_book_seats.assert_has_calls([
                    call(10, start_seat=None),
                    call(10, start_seat='B3')
                ])
                self.app.seating_planner.cancel_booking.assert_called_once_with("BOOK123")

    def test_handle_booking_when_seating_planner_not_defined(self):
        """Tests handle booking when seating planner is not defined."""
        self.app._handle_booking()
        self.assertIsNone(self.app.seating_planner)

    def test_on_select_view_booking_call_handle_view_booking(self):
        """Tests that booking view is handled."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.display_menu.return_value = 2

        with patch.object(self.app, '_handle_view_booking') as mock_handle_view_booking:
            self.app._process_user_selection()
            mock_handle_view_booking.assert_called_once()

    def test_handle_view_booking(self):
        """Tests viewing booking functionality."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.prompt_for_booking_id.side_effect = ["BOOK123", ""]

        with patch.object(self.mock_console_ui, 'display_seating_map') as mock_display_seating_map:
            self.app._handle_view_booking()
            self.app.seating_planner.get_seating_plan.assert_called_with("BOOK123")
            mock_display_seating_map.assert_called_with(seating_plan_mock)

    def test_handle_view_booking_when_seating_planner_not_defined(self):
        """Tests viewing booking functionality."""
        with patch.object(self.mock_console_ui, 'prompt_for_booking_id') as mock_prompt_for_booking_id:
            self.app._handle_view_booking()
        self.assertIsNone(self.app.seating_planner)
        mock_prompt_for_booking_id.assert_not_called()

    def test_handle_view_booking_when_seating_plan_is_not_defined(self):
        """Tests viewing booking functionality."""
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = None
        self.mock_console_ui.prompt_for_booking_id.side_effect = ["BOOK123", ""]

        with patch("builtins.print") as mock_print:
            self.app._handle_view_booking()
        mock_print.assert_has_calls([call('Booking ID not found. Please try again.')])

    def test_handle_view_booking_when_exception(self):
        """Tests viewing booking functionality."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        with patch.object(self.app.console_ui, 'prompt_for_booking_id', side_effect=Exception("Simulated error")):
            with patch("builtins.print") as mock_print:
                self.app._handle_view_booking()
                mock_print.assert_has_calls([call('Error viewing booking: Simulated error')])

    def test_on_select_exit_application_call_exit_application(self):
        """Tests that exit application is handled."""
        seating_plan_mock = MagicMock()
        self.app.seating_planner = MagicMock()
        self.app.seating_planner.get_seating_plan.return_value = seating_plan_mock
        self.mock_console_ui.display_menu.return_value = 3

        with patch.object(self.app, '_exit_application') as mock_exit_application:
            self.app._process_user_selection()
            mock_exit_application.assert_called_once()

    @patch('builtins.input', side_effect=["3"])  # Exit option
    @patch('sys.exit')
    def test_exit_application(self, mock_sys_exit, mock_input):
        """Tests that the application exits cleanly."""
        self.app._exit_application()
        self.mock_console_ui.display_exit_message.assert_called_once()
        mock_sys_exit.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()
