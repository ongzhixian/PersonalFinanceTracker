import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from console_ui import ConsoleUi
from seating_planner import SeatingPlanner
import main  # Import main to test the main function

class TestConsoleUi(unittest.TestCase):

    def setUp(self):
        self.ui = ConsoleUi()

    @patch('builtins.input', side_effect=['My Event', '3', '5'])
    def test_application_start_prompt(self, mock_input):
        title, rows, cols = self.ui.application_start_prompt()
        self.assertEqual(title, 'My Event')
        self.assertEqual(rows, 3)
        self.assertEqual(cols, 5)

    @patch('builtins.input', side_effect=['invalid', '3'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_application_start_prompt_invalid_rows(self, mock_stdout, mock_input):
        title, rows, cols = self.ui.application_start_prompt()
        self.assertIn("Invalid input. Please enter a positive integer for the number of rows.", mock_stdout.getvalue())
        self.assertEqual(rows, 3)

    @patch('builtins.input', side_effect=['invalid', '5'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_application_start_prompt_invalid_cols(self, mock_stdout, mock_input):
        with patch('builtins.input', side_effect=['Test', '2', 'invalid', '5']):
            title, rows, cols = self.ui.application_start_prompt()
            self.assertIn("Invalid input. Please enter a positive integer for the number of seats per row.",
                          mock_stdout.getvalue())
            self.assertEqual(cols, 5)

    @patch('builtins.input', side_effect=['1'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_menu_prompt_valid_input(self, mock_stdout, mock_input):
        seating_plan = [['O', 'O'], ['O', 'O']]
        choice = self.ui.menu_prompt(seating_plan)
        self.assertEqual(choice, 1)
        self.assertIn("--- Main Menu ---", mock_stdout.getvalue())

    @patch('builtins.input', side_effect=['invalid', '4', '2'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_menu_prompt_invalid_then_valid_input(self, mock_stdout, mock_input):
        seating_plan = [['O', 'O'], ['O', 'O']]
        choice = self.ui.menu_prompt(seating_plan)
        self.assertEqual(choice, 2)
        self.assertIn("Invalid input. Please enter a number.", mock_stdout.getvalue())
        self.assertIn("Invalid choice. Please enter 1, 2, or 3.", mock_stdout.getvalue())

    @patch('builtins.input', side_effect=['2'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_number_of_seats_to_book_prompt_valid(self, mock_stdout, mock_input):
        seating_plan = [['O', 'O'], ['O', 'O']]
        num_seats = self.ui.number_of_seats_to_book_prompt(seating_plan)
        self.assertEqual(num_seats, 2)

    @patch('builtins.input', side_effect=['invalid', '-1', '1'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_number_of_seats_to_book_prompt_invalid(self, mock_stdout, mock_input):
        seating_plan = [['O', 'O'], ['O', 'O']]
        num_seats = self.ui.number_of_seats_to_book_prompt(seating_plan)
        self.assertEqual(num_seats, 1)
        self.assertIn("Invalid input. Please enter a positive integer for the number of seats.", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_seating_map(self, mock_stdout):
        seating_map = [['O', 'X'], ['O', 'O']]
        self.ui.display_seating_map(seating_map)
        output = mock_stdout.getvalue()
        self.assertIn("--- Seating Map ---", output)
        self.assertIn("R A | O X", output)
        self.assertIn("R B | O O", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_seating_map_empty(self, mock_stdout):
        seating_map: List[List[str]] = []
        self.ui.display_seating_map(seating_map)
        output = mock_stdout.getvalue()
        self.assertIn("Seating plan is empty.", output)

    @patch('builtins.input', return_value='confirm')
    def test_confirm_proposed_seating_map_prompt_confirm(self, mock_input):
        response = self.ui.confirm_proposed_seating_map_prompt()
        self.assertEqual(response, 'confirm')

    @patch('builtins.input', return_value='')
    def test_confirm_proposed_seating_map_prompt_empty(self, mock_input):
        response = self.ui.confirm_proposed_seating_map_prompt()
        self.assertEqual(response, '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_message(self, mock_stdout):
        self.ui.display_message("Test message.")
        self.assertIn("Test message.", mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)