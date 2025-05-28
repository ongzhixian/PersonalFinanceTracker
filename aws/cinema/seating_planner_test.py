import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from console_ui import ConsoleUi
from seating_planner import SeatingPlanner
import main  # Import main to test the main function

class TestSeatingPlanner(unittest.TestCase):

    def setUp(self):
        self.planner = SeatingPlanner("Test Event", 3, 5)  # 3 rows, 5 seats per row

    def test_initialization(self):
        self.assertEqual(self.planner.title, "Test Event")
        self.assertEqual(self.planner.num_rows, 3)
        self.assertEqual(self.planner.seats_per_row, 5)
        expected_plan = [['O', 'O', 'O', 'O', 'O'],
                         ['O', 'O', 'O', 'O', 'O'],
                         ['O', 'O', 'O', 'O', 'O']]
        self.assertEqual(self.planner.get_seating_plan(), expected_plan)
        self.assertEqual(self.planner._proposed_bookings, {})

    def test_initialization_invalid_inputs(self):
        with self.assertRaises(ValueError):
            SeatingPlanner("", 3, 5)
        with self.assertRaises(ValueError):
            SeatingPlanner("Test", 0, 5)
        with self.assertRaises(ValueError):
            SeatingPlanner("Test", 3, -1)

    def test_get_seating_plan(self):
        plan = self.planner.get_seating_plan()
        self.assertEqual(len(plan), 3)
        self.assertEqual(len(plan[0]), 5)
        self.assertEqual(plan[0][0], 'O')

    def test_get_proposed_seating_plan_success(self):
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(2)
        self.assertIsNotNone(booking_id)
        self.assertEqual(proposed_map[0][0], 'P')
        self.assertEqual(proposed_map[0][1], 'P')
        self.assertIn(booking_id, self.planner._proposed_bookings)
        self.assertEqual(len(self.planner._proposed_bookings[booking_id]), 2)

    def test_get_proposed_seating_plan_no_space(self):
        # Book all seats in the first row
        for i in range(5):
            self.planner._seating_plan[0][i] = 'X'

        # Try to book 5 seats, should not find in first row
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(5)
        self.assertIsNotNone(booking_id)  # Should find in the second row
        self.assertEqual(proposed_map[1][0], 'P')
        self.assertEqual(proposed_map[1][4], 'P')
        self.assertIn(booking_id, self.planner._proposed_bookings)

        # Try to book more seats than available in a row
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(6)
        self.assertEqual(booking_id, "")
        self.assertEqual(proposed_map, [])

        # Book all seats
        for r in range(3):
            for c in range(5):
                self.planner._seating_plan[r][c] = 'X'
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(1)
        self.assertEqual(booking_id, "")
        self.assertEqual(proposed_map, [])

    def test_get_proposed_seating_plan_with_start_seat_success(self):
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(2, start_seat=(1, 2))
        self.assertIsNotNone(booking_id)
        self.assertEqual(proposed_map[1][2], 'P')
        self.assertEqual(proposed_map[1][3], 'P')

    def test_get_proposed_seating_plan_with_start_seat_fail(self):
        # Book a seat to block the proposed start
        self.planner._seating_plan[1][3] = 'X'
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(2, start_seat=(1, 2))
        self.assertEqual(booking_id, "")
        self.assertEqual(proposed_map, [])

        # Start seat out of bounds
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(1, start_seat=(9, 9))
        self.assertEqual(booking_id, "")
        self.assertEqual(proposed_map, [])

    def test_confirm_proposed_seating_map_success(self):
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(2)
        initial_plan = self.planner.get_seating_plan()

        confirmed = self.planner.confirm_proposed_seating_map(booking_id, proposed_map)
        self.assertTrue(confirmed)
        self.assertEqual(self.planner._seating_plan[0][0], 'X')
        self.assertEqual(self.planner._seating_plan[0][1], 'X')
        self.assertNotIn(booking_id, self.planner._proposed_bookings)

    def test_confirm_proposed_seating_map_invalid_id(self):
        proposed_map = self.planner.get_seating_plan()  # Dummy map
        confirmed = self.planner.confirm_proposed_seating_map("non-existent-id", proposed_map)
        self.assertFalse(confirmed)

    def test_confirm_proposed_seating_map_conflict(self):
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(2)
        # Simulate another booking taking one of the proposed seats
        self.planner._seating_plan[0][0] = 'X'

        confirmed = self.planner.confirm_proposed_seating_map(booking_id, proposed_map)
        self.assertFalse(confirmed)
        # Assert that the actual seating plan is not changed by the failed confirmation
        self.assertEqual(self.planner._seating_plan[0][0], 'X')
        self.assertEqual(self.planner._seating_plan[0][1], 'O')  # Should remain 'O'
        self.assertNotIn(booking_id, self.planner._proposed_bookings)  # Should be removed


# Unit test for the main function
class TestMainFunction(unittest.TestCase):

    @patch('main.ConsoleUi')
    @patch('main.SeatingPlanner')
    @patch('builtins.exit')
    def test_main_exit_option(self, mock_exit, MockSeatingPlanner, MockConsoleUi):
        mock_ui_instance = MockConsoleUi.return_value
        mock_ui_instance.application_start_prompt.return_value = ("Test", 2, 2)
        mock_ui_instance.menu_prompt.side_effect = [3]  # User chooses to exit

        main.main()
        mock_exit.assert_called_once_with(0)
        mock_ui_instance.display_message.assert_called_with("Exiting application. Goodbye!")

    @patch('main.ConsoleUi')
    @patch('main.SeatingPlanner')
    @patch('builtins.exit')
    def test_main_book_and_confirm_success(self, mock_exit, MockSeatingPlanner, MockConsoleUi):
        mock_ui_instance = MockConsoleUi.return_value
        mock_planner_instance = MockSeatingPlanner.return_value

        # Mock initial setup
        mock_ui_instance.application_start_prompt.return_value = ("Test", 2, 2)
        mock_planner_instance.get_seating_plan.return_value = [['O', 'O'], ['O', 'O']]

        # Simulate user choosing to book (1), then confirming
        mock_ui_instance.menu_prompt.side_effect = [1, 3]  # Book, then exit after booking
        mock_ui_instance.number_of_seats_to_book_prompt.return_value = 1

        # Mock proposed seating plan and confirmation
        mock_planner_instance.get_proposed_seating_plan.return_value = ("mock_booking_id", [['P', 'O'], ['O', 'O']])
        mock_ui_instance.confirm_proposed_seating_map_prompt.return_value = "confirm"
        mock_planner_instance.confirm_proposed_seating_map.return_value = True  # Booking successful

        main.main()

        mock_ui_instance.application_start_prompt.assert_called_once()
        mock_ui_instance.menu_prompt.assert_called_with([['O', 'O'], ['O', 'O']])
        mock_ui_instance.number_of_seats_to_book_prompt.assert_called_once()
        mock_planner_instance.get_proposed_seating_plan.assert_called_with(1, start_seat=None)
        mock_ui_instance.display_seating_map.assert_called_with([['P', 'O'], ['O', 'O']])
        mock_ui_instance.confirm_proposed_seating_map_prompt.assert_called_once()
        mock_planner_instance.confirm_proposed_seating_map.assert_called_with("mock_booking_id",
                                                                              [['P', 'O'], ['O', 'O']])
        mock_ui_instance.display_message.assert_called_with("Seats booked successfully!")
        mock_exit.assert_called_once_with(0)

    @patch('main.ConsoleUi')
    @patch('main.SeatingPlanner')
    @patch('builtins.exit')
    def test_main_book_and_confirm_fail_then_cancel(self, mock_exit, MockSeatingPlanner, MockConsoleUi):
        mock_ui_instance = MockConsoleUi.return_value
        mock_planner_instance = MockSeatingPlanner.return_value

        mock_ui_instance.application_start_prompt.return_value = ("Test", 2, 2)
        mock_planner_instance.get_seating_plan.return_value = [['O', 'O'], ['O', 'O']]

        mock_ui_instance.menu_prompt.side_effect = [1, 3]  # Book, then exit
        mock_ui_instance.number_of_seats_to_book_prompt.return_value = 1

        # Simulate a booking failure and then a cancellation
        mock_planner_instance.get_proposed_seating_plan.side_effect = [
            ("mock_booking_id_1", [['P', 'O'], ['O', 'O']]),  # First proposal
            ("", [])  # No more seats found after conflict (or user tried again and no seats)
        ]
        mock_ui_instance.confirm_proposed_seating_map_prompt.side_effect = ["confirm", ""]  # Confirm first, then cancel

        mock_planner_instance.confirm_proposed_seating_map.side_effect = [False, False]  # First booking fails

        main.main()

        mock_ui_instance.display_message.assert_any_call(
            "Booking failed. Some seats became unavailable. Please try again.")
        mock_ui_instance.display_message.assert_any_call("Booking cancelled.")
        mock_exit.assert_called_once_with(0)

    @patch('main.ConsoleUi')
    @patch('main.SeatingPlanner')
    @patch('builtins.exit')
    def test_main_view_bookings(self, mock_exit, MockSeatingPlanner, MockConsoleUi):
        mock_ui_instance = MockConsoleUi.return_value
        mock_planner_instance = MockSeatingPlanner.return_value

        mock_ui_instance.application_start_prompt.return_value = ("Test", 2, 2)
        mock_planner_instance.get_seating_plan.side_effect = [
            [['O', 'O'], ['O', 'O']],  # Initial state
            [['X', 'O'], ['O', 'O']]  # After some hypothetical booking
        ]

        mock_ui_instance.menu_prompt.side_effect = [2, 3]  # View bookings, then exit

        main.main()

        # Check if get_seating_plan was called for displaying current bookings
        # It's called once at the start of the loop and once for option 2
        self.assertEqual(mock_planner_instance.get_seating_plan.call_count, 2)
        mock_ui_instance.display_seating_map.assert_any_call([['X', 'O'], ['O', 'O']])
        mock_exit.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)