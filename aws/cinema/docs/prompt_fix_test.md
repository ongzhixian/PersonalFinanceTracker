Given Python code:

```main.py
import sys
from app_configuration import AppConfiguration
from console_ui import ConsoleUi
from seating_planner import SeatingPlanner

class SeatingApp:
    """
    Manages interactions between ConsoleUi and SeatingPlanner for a movie seating application.
    """

    def __init__(self, config_path: str) -> None:
        """
        Initializes the application with configurations and UI components.
        :param config_path: Path to the application configuration file.
        """
        self.app_configuration = AppConfiguration(config_path)
        self.console_ui = ConsoleUi(self.app_configuration)
        self.seating_planner: SeatingPlanner | None = None

    def start(self) -> None:
        """
        Starts the seating planner application and manages user interactions.
        """
        try:
            title, number_of_rows, seats_per_row = self.console_ui.prompt_for_application_start_details()
            self.seating_planner = SeatingPlanner(title, number_of_rows, seats_per_row)
            self._run_event_loop()
        except Exception as e:
            print(f"Error initializing application: {e}")
            sys.exit(1)

    def _run_event_loop(self) -> None:
        """
        Handles the main event loop for user interaction.
        """
        while True:
            self._process_user_selection()

    def _process_user_selection(self) -> None:
        """
        Handles user selection for seat booking, viewing seating map, and exiting.
        """
        if not self.seating_planner:
            print("Seating planner is not initialized.")
            return

        seating_plan = self.seating_planner.get_seating_plan()
        user_selection = self.console_ui.display_menu(seating_plan)

        selection_handlers = {
            1: self._handle_booking,
            2: self._handle_view_booking,
            3: self._exit_application,
        }

        selection_handler = selection_handlers.get(user_selection)
        if selection_handler:
            selection_handler()
        else:
            print("Invalid selection. Please choose a valid option.")

    def _handle_booking(self) -> None:
        """
        Handles seat booking functionality.
        """
        if not self.seating_planner:
            return

        try:
            seating_plan = self.seating_planner.get_seating_plan()
            number_of_seats_to_book = self.console_ui.prompt_for_number_of_seats_to_book(seating_plan)
            if number_of_seats_to_book is None:
                return

            start_seat = None
            has_displayed_successfully_book_tickets = False
            while True:
                booking_id = self.seating_planner.book_seats(number_of_seats_to_book, start_seat=start_seat)
                seating_plan = self.seating_planner.get_seating_plan(booking_id)
                if not has_displayed_successfully_book_tickets:
                    print(f'\nSuccessfully reserved {number_of_seats_to_book} {seating_plan.title} tickets.')
                    has_displayed_successfully_book_tickets = True
                self.console_ui.display_seating_map(seating_plan)

                response = self.console_ui.prompt_for_booking_confirmation()
                if response == '':
                    print(f"\nBooking ID: {booking_id} confirmed.")
                    break

                start_seat = response
                self.seating_planner.cancel_booking(booking_id)
        except Exception as e:
            print(f"Error processing booking: {e}")

    def _handle_view_booking(self) -> None:
        """
        Handles viewing seating plans based on booking ID.
        """
        if not self.seating_planner:
            return

        try:
            while True:
                booking_id = self.console_ui.prompt_for_booking_id()
                if booking_id == '':
                    break

                seating_plan = self.seating_planner.get_seating_plan(booking_id)
                if seating_plan is None:
                    print("Booking ID not found. Please try again.")
                    continue

                self.console_ui.display_seating_map(seating_plan)

        except Exception as e:
            print(f"Error viewing booking: {e}")

    def _exit_application(self) -> None:
        """
        Exits the application cleanly.
        """
        self.console_ui.display_exit_message()
        sys.exit(0)


if __name__ == '__main__':
    SeatingApp('./app_configuration.json').start()

```

```test_main.py
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

```

Fix test_handle_view_booking unit test.

Generate new unit test for prompt_for_booking_confirmation function.
Unit test should only check if input prompt matches the following:
"Press Enter to confirm selection or enter new position: "
Test should ensure prompt_for_booking_confirmation display the expected prompt
Do not change `test_console_ui.setUp`
All unit tests must be runnable. 
All unit tests must pass.


Generate unit tests for main.py using unittest. 
All unit tests must be runnable. 
All unit tests must pass.

