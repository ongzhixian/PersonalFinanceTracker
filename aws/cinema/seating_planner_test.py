import unittest
from seating_planner import SeatingPlanner
from shared_data_models import SeatingPlan

class TestSeatingPlanner(unittest.TestCase):

    def setUp(self):
        self.planner = SeatingPlanner("Test Venue", 3, 5)

    def test_initialization(self):
        self.assertEqual(self.planner.title, "Test Venue")
        self.assertEqual(self.planner.num_rows, 3)
        self.assertEqual(self.planner.seats_per_row, 5)
        # Check initial seating plan
        expected_plan = [
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O']
        ]
        returned_seating_plan = self.planner.get_seating_plan()
        self.assertIsInstance(returned_seating_plan, SeatingPlan)
        self.assertEqual(returned_seating_plan.title, "Test Venue")
        self.assertEqual(returned_seating_plan.plan, expected_plan)

    def test_initialization_invalid_inputs(self):
        with self.assertRaises(ValueError):
            SeatingPlanner("", 3, 5)  # Empty title
        with self.assertRaises(ValueError):
            SeatingPlanner("Test Venue", 0, 5)  # Zero rows
        with self.assertRaises(ValueError):
            SeatingPlanner("Test Venue", 3, -1)  # Negative seats per row

    def test_get_seating_plan(self):
        # Already tested in initialization, but good to have a dedicated one
        expected_plan_status = [
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O']
        ]
        returned_seating_plan = self.planner.get_seating_plan()
        self.assertIsInstance(returned_seating_plan, SeatingPlan)
        self.assertEqual(returned_seating_plan.title, "Test Venue")
        self.assertEqual(returned_seating_plan.plan, expected_plan_status)

    def test_get_proposed_seating_plan_no_start_seat(self):
        # Propose 3 seats
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(3)
        self.assertIsNotNone(booking_id)
        self.assertEqual(len(proposed_map), 3)
        self.assertEqual(len(proposed_map[0]), 5)

        # Expected map with 'P' for proposed seats
        expected_proposed_map = [
            ['P', 'P', 'P', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O']
        ]
        self.assertEqual(proposed_map, expected_proposed_map)

        # Ensure the actual seating plan is unchanged before confirmation
        actual_plan = self.planner.get_seating_plan().plan
        self.assertEqual(actual_plan, [
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O']
        ])
        self.assertIn(booking_id, self.planner._proposed_bookings)
        self.assertEqual(self.planner._proposed_bookings[booking_id].seats, [(0, 0), (0, 1), (0, 2)])


    def test_get_proposed_seating_plan_with_start_seat(self):
        # Propose 2 seats starting at (1, 1)
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(2, (1, 1))
        self.assertIsNotNone(booking_id)

        expected_proposed_map = [
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'P', 'P', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O']
        ]
        self.assertEqual(proposed_map, expected_proposed_map)
        self.assertIn(booking_id, self.planner._proposed_bookings)
        self.assertEqual(self.planner._proposed_bookings[booking_id].seats, [(1, 1), (1, 2)])

    def test_get_proposed_seating_plan_not_enough_seats(self):
        # Fill some seats to make it harder to find
        booking_id_1, _ = self.planner.get_proposed_seating_plan(3, (0, 0))
        self.planner.confirm_proposed_seating_map(booking_id_1)

        # Try to find 4 seats, which won't fit in the first row anymore
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(4)
        self.assertIsNotNone(booking_id)
        self.assertEqual(len(proposed_map), 3)
        self.assertEqual(len(proposed_map[0]), 5)

        expected_proposed_map = [
            ['X', 'X', 'X', 'O', 'O'], # Existing booked seats
            ['P', 'P', 'P', 'P', 'O'], # New proposed seats
            ['O', 'O', 'O', 'O', 'O']
        ]
        self.assertEqual(proposed_map, expected_proposed_map)
        self.assertIn(booking_id, self.planner._proposed_bookings)
        self.assertEqual(self.planner._proposed_bookings[booking_id].seats, [(1, 0), (1, 1), (1, 2), (1, 3)])

    def test_get_proposed_seating_plan_no_space(self):
        # Book all seats
        for r in range(self.planner.num_rows):
            booking_id, _ = self.planner.get_proposed_seating_plan(self.planner.seats_per_row, (r, 0))
            self.planner.confirm_proposed_seating_map(booking_id)

        # Try to propose 1 seat
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(1)
        self.assertEqual(booking_id, "")
        self.assertEqual(proposed_map, [])

    def test_get_proposed_seating_plan_invalid_number_of_seats(self):
        with self.assertRaises(ValueError):
            self.planner.get_proposed_seating_plan(0)
        with self.assertRaises(ValueError):
            self.planner.get_proposed_seating_plan(-1)

    def test_get_proposed_seating_plan_start_seat_out_of_bounds(self):
        booking_id, proposed_map = self.planner.get_proposed_seating_plan(2, (5, 0))
        self.assertEqual(booking_id, "")
        self.assertEqual(proposed_map, [])

        booking_id, proposed_map = self.planner.get_proposed_seating_plan(2, (0, 10))
        self.assertEqual(booking_id, "")
        self.assertEqual(proposed_map, [])

    def test_confirm_proposed_seating_map(self):
        booking_id, _ = self.planner.get_proposed_seating_plan(2, (0, 0))
        self.assertTrue(self.planner.confirm_proposed_seating_map(booking_id))

        expected_plan = [
            ['X', 'X', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O']
        ]
        self.assertEqual(self.planner.get_seating_plan().plan, expected_plan)
        self.assertNotIn(booking_id, self.planner._proposed_bookings)

    def test_confirm_proposed_seating_map_invalid_id(self):
        self.assertFalse(self.planner.confirm_proposed_seating_map("invalid-id"))

    def test_confirm_proposed_seating_map_seats_taken(self):
        booking_id_1, _ = self.planner.get_proposed_seating_plan(2, (0, 0))
        booking_id_2, _ = self.planner.get_proposed_seating_plan(1, (0, 0)) # Propose same seat

        # Confirm the first booking, making the seat unavailable
        self.assertTrue(self.planner.confirm_proposed_seating_map(booking_id_1))

        # Try to confirm the second booking, which should now fail
        self.assertFalse(self.planner.confirm_proposed_seating_map(booking_id_2))

        # The seat (0,0) should be 'X' from the first booking, and the second proposed booking should be gone
        expected_plan = [
            ['X', 'X', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O']
        ]
        self.assertEqual(self.planner.get_seating_plan().plan, expected_plan)
        self.assertNotIn(booking_id_2, self.planner._proposed_bookings)

    def test_cancel_proposed_seating_map(self):
        booking_id, _ = self.planner.get_proposed_seating_plan(2, (0, 0))
        self.assertTrue(self.planner.cancel_proposed_seating_map(booking_id))
        self.assertNotIn(booking_id, self.planner._proposed_bookings)

        # Seating plan should remain unchanged
        expected_plan = [
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O']
        ]
        self.assertEqual(self.planner.get_seating_plan().plan, expected_plan)

    def test_cancel_proposed_seating_map_invalid_id(self):
        self.assertFalse(self.planner.cancel_proposed_seating_map("non-existent-id"))

if __name__ == '__main__':
    unittest.main()