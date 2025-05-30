import unittest
from unittest.mock import MagicMock
from seating_planner import SeatingPlanner, SeatingPlan
from main import SeatingPlannerApp

class TestSeatingPlannerApp(unittest.TestCase):
    def setUp(self):
        self.mock_ui = MagicMock()
        self.mock_planner = MagicMock()
        self.app = SeatingPlannerApp(self.mock_ui, self.mock_planner)

    def test_handle_booking_success(self):
        self.mock_ui.number_of_seats_to_book_prompt.return_value = 2
        self.mock_planner.book_seats.return_value = 'BID123'
        self.mock_ui.confirm_seating_map_prompt.side_effect = ['', '']
        self.mock_planner.get_seating_plan.return_value = SeatingPlan()  # Replace with actual object

        self.app.handle_booking()

        self.mock_planner.book_seats.assert_called_with(2, start_seat=None)
        self.mock_ui.display_booking_id.assert_called_with('BID123')

    def test_handle_booking_invalid(self):
        self.mock_ui.number_of_seats_to_book_prompt.return_value = None
        self.app.handle_booking()
        self.mock_planner.book_seats.assert_not_called()

    def test_handle_view_booking_found(self):
        self.mock_ui.booking_id_prompt.side_effect = ['BID123']
        self.mock_planner.get_seating_plan.return_value = SeatingPlan()  # Replace with actual object

        self.app.handle_view_booking()
        self.mock_ui.display_seating_map.assert_called()

    def test_handle_view_booking_not_found(self):
        self.mock_ui.booking_id_prompt.side_effect = ['BID123', '']
        self.mock_planner.get_seating_plan.return_value = None

        self.app.handle_view_booking()
        self.mock_ui.display_error.assert_called_with("Booking ID cannot be found.")

    def test_run_exit(self):
        self.mock_ui.menu_prompt.side_effect = [3]
        self.app.run()
        self.mock_ui.display_exit_message.assert_called_once()

if __name__ == '__main__':
    unittest.main()