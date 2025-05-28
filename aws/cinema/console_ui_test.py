import unittest
from unittest.mock import patch, call
from console_ui import ConsoleUi


class TestConsoleUi(unittest.TestCase):

    def setUp(self):
        """Set up a new ConsoleUi instance before each test."""
        self.ui = ConsoleUi()

    @patch('builtins.input', side_effect=["Movie Title 10 20"])
    def test_application_start_prompt_valid_input(self, mock_input):
        """Test application_start_prompt with valid input."""
        title, rows, seats_per_row = self.ui.application_start_prompt()
        self.assertEqual(title, "Movie Title")
        self.assertEqual(rows, 10)
        self.assertEqual(seats_per_row, 20)
        mock_input.assert_called_once()

    @patch('builtins.input', side_effect=["Invalid", "Movie 10 20"])
    @patch('builtins.print')
    def test_application_start_prompt_invalid_format(self, mock_print, mock_input):
        """Test application_start_prompt with invalid format then valid."""
        title, rows, seats_per_row = self.ui.application_start_prompt()
        self.assertEqual(title, "Movie")
        self.assertEqual(rows, 10)
        self.assertEqual(seats_per_row, 20)
        # Check that the invalid format message was printed
        mock_print.assert_any_call("Invalid format. Please ensure you provide a title, number of rows, and seats per row.")

    @patch('builtins.input', side_effect=["Movie 0 20", "Movie 27 20", "Movie 10 0", "Movie 10 51", "Movie 10 20"])
    @patch('builtins.print')
    def test_application_start_prompt_invalid_row_seat_counts(self, mock_print, mock_input):
        """Test application_start_prompt with invalid row/seat counts then valid."""
        expected_error_rows = "Invalid input. Number of rows must be a positive integer and not exceed 26 (A-Z)."
        expected_error_seats = "Invalid input. Number of seats per row must be a positive integer and not exceed 50."

        title, rows, seats_per_row = self.ui.application_start_prompt()
        self.assertEqual(title, "Movie")
        self.assertEqual(rows, 10)
        self.assertEqual(seats_per_row, 20)
        # Check that the invalid messages were printed
        mock_print.assert_any_call(expected_error_rows)
        mock_print.assert_any_call(expected_error_seats)

    @patch('builtins.input', side_effect=["Movie ABC 20", "Movie 10 DEF", "Movie 10 20"])
    @patch('builtins.print')
    def test_application_start_prompt_non_integer_input(self, mock_print, mock_input):
        """Test application_start_prompt with non-integer row/seat counts then valid."""
        title, rows, seats_per_row = self.ui.application_start_prompt()
        self.assertEqual(title, "Movie")
        self.assertEqual(rows, 10)
        self.assertEqual(seats_per_row, 20)
        mock_print.assert_any_call("Invalid input. Please ensure rows and seats per row are positive integers.")

    @patch('builtins.input', side_effect=["  1  "])
    def test_menu_prompt_valid_choice(self, mock_input):
        """Test menu_prompt with a valid choice."""
        choice = self.ui.menu_prompt("Any Movie", 100, [])
        self.assertEqual(choice, 1)
        mock_input.assert_called_once()

    @patch('builtins.input', side_effect=["4", "abc", "2"])
    @patch('builtins.print')
    def test_menu_prompt_invalid_then_valid_choice(self, mock_print, mock_input):
        """Test menu_prompt with invalid then valid choices."""
        choice = self.ui.menu_prompt("Any Movie", 100, [])
        self.assertEqual(choice, 2)
        mock_print.assert_any_call("Invalid choice. Please enter 1, 2, or 3.")
        mock_print.assert_any_call("Invalid input. Please enter a number.")
        self.assertEqual(mock_input.call_count, 3)

    @patch('builtins.input', side_effect=["5"])
    @patch('builtins.print') # Keep print patched to capture map output
    def test_number_of_seats_to_book_prompt_valid(self, mock_print, mock_input):
        """Test number_of_seats_to_book_prompt with valid input."""
        seating_plan = [['O']]
        num_seats = self.ui.number_of_seats_to_book_prompt(seating_plan)
        self.assertEqual(num_seats, 5)
        # Verify that display_seating_map's output is part of mock_print's calls
        self.assertTrue(any("S C R E E N" in c[0] for c in mock_print.call_args_list if c.args), "Seating map not displayed")
        mock_input.assert_called_once()

    @patch('builtins.input', side_effect=["0", "-2", "abc", "3"])
    @patch('builtins.print') # Keep print patched to capture map output and error messages
    def test_number_of_seats_to_book_prompt_invalid_then_valid(self, mock_print, mock_input):
        """Test number_of_seats_to_book_prompt with invalid then valid input."""
        seating_plan = [['O']] # Example seating plan for display
        num_seats = self.ui.number_of_seats_to_book_prompt(seating_plan)
        self.assertEqual(num_seats, 3)

        # Count how many times the specific error message was printed
        error_message_count = sum(1 for call_arg in mock_print.call_args_list if call_arg.args and call_arg.args[0] == "Invalid input. Please enter a positive integer for the number of seats.")
        self.assertEqual(error_message_count, 3, "Error message for invalid seat number not printed correctly.")

        # Ensure display_seating_map was called for each prompt attempt
        # We look for a pattern in the printed output that indicates the map was drawn
        map_display_count = sum(1 for call_arg in mock_print.call_args_list if call_arg.args and "S C R E E N" in call_arg.args[0])
        self.assertEqual(map_display_count, 4, "Seating map not displayed the correct number of times.")

        self.assertEqual(mock_input.call_count, 4)


    @patch('builtins.print')
    def test_display_seating_map_typical(self, mock_print):
        """Test display_seating_map with a typical seating arrangement."""
        seating_map = [
            ['O', 'O', 'X'],
            ['O', 'X', 'O']
        ]
        self.ui.display_seating_map(seating_map)

        printed_output = [call.args[0] for call in mock_print.call_args_list if call.args]

        # Calculate expected footer width based on the logic in display_seating_map
        num_cols = len(seating_map[0])
        # Each column takes 3 chars ('1  ', '10 ')
        # Plus 3 spaces for the row label offset ("   ")
        expected_footer_width = 3 + (num_cols * 3)

        expected_screen_header_line = "\nS C R E E N" # based on (12 - 11) // 2 = 0 padding
        expected_separator_line = "-" * expected_footer_width # "------------" for 3 columns

        # Assertion for screen header and separator
        self.assertTrue(expected_screen_header_line in printed_output, "SCREEN header line not found or incorrect format.")
        self.assertTrue(expected_separator_line in printed_output, "Separator line not found or incorrect length.")

        # Check for row displays (these should be exact matches)
        self.assertTrue("B .  .  #  " in printed_output, "Row B display incorrect")
        self.assertTrue("A .  #  .  " in printed_output, "Row A display incorrect")

        # Check for column numbers (this should be an exact match)
        self.assertTrue("  1  2  3  " in printed_output, "Column numbers display incorrect")


    @patch('builtins.print')
    def test_display_seating_map_empty(self, mock_print):
        """Test display_seating_map with an empty seating map."""
        self.ui.display_seating_map([])
        mock_print.assert_called_once_with("\nSeating plan is empty.")

    @patch('builtins.print')
    def test_display_seating_map_empty_row(self, mock_print):
        """Test display_seating_map with a seating map containing an empty row."""
        self.ui.display_seating_map([[]])
        mock_print.assert_called_once_with("\nSeating plan is empty.")

    @patch('builtins.input', return_value="confirm")
    def test_confirm_proposed_seating_map_prompt_confirm(self, mock_input):
        """Test confirm_proposed_seating_map_prompt with 'confirm' input."""
        response = self.ui.confirm_proposed_seating_map_prompt()
        self.assertEqual(response, "confirm")
        mock_input.assert_called_once()

    @patch('builtins.input', return_value="")
    def test_confirm_proposed_seating_map_prompt_decline(self, mock_input):
        """Test confirm_proposed_seating_map_prompt with empty input (decline)."""
        response = self.ui.confirm_proposed_seating_map_prompt()
        self.assertEqual(response, "")
        mock_input.assert_called_once()

    @patch('builtins.input', return_value="anything else")
    def test_confirm_proposed_seating_map_prompt_other_input(self, mock_input):
        """Test confirm_proposed_seating_map_prompt with other input."""
        response = self.ui.confirm_proposed_seating_map_prompt()
        self.assertEqual(response, "anything else")
        mock_input.assert_called_once()

    @patch('builtins.print')
    def test_display_message(self, mock_print):
        """Test display_message."""
        self.ui.display_message("Hello World!")
        mock_print.assert_called_once_with("\nHello World!")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)