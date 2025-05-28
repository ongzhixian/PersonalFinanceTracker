import unittest
from unittest.mock import patch
from main import main
#from console_ui import ConsoleUi
#from seating_map import SeatingMap

class TestMainFunction(unittest.TestCase):
    @patch('builtins.input', side_effect=[
        "Concert 10 20",  # Valid input for application_start_prompt
        "1",              # User selects option 1 from menu
        "5",              # Number of seats to book
        "confirm",        # Confirm seating map
        "3"               # Exit the application
    ])
    @patch('console_ui.ConsoleUi.menu_prompt', side_effect=[1, 3])
    @patch('console_ui.ConsoleUi.number_of_seats_to_book_prompt', return_value=5)
    @patch('console_ui.ConsoleUi.confirm_proposed_seating_map_prompt', return_value='confirm')
    @patch('console_ui.ConsoleUi.display_seating_map')
    @patch('seating_map.SeatingMap.get_confirmed_booking_map', return_value={})
    @patch('seating_map.SeatingMap.get_proposed_seating_map', return_value=("booking_id", {}))
    @patch('seating_map.SeatingMap.confirm_proposed_seating_map')
    def test_main_workflow(self, mock_confirm_map, mock_proposed_map, mock_confirmed_map, mock_display_map, mock_confirm_prompt, mock_seats_prompt, mock_menu_prompt, mock_input):
        # Run the main function
        with self.assertRaises(SystemExit):  # Expect SystemExit when user selects option 3
            main()

        # Assertions to verify the flow
        mock_input.assert_called()
        mock_menu_prompt.assert_called()
        mock_seats_prompt.assert_called()
        mock_confirm_prompt.assert_called()
        mock_display_map.assert_called()
        mock_confirm_map.assert_called()

    @patch('builtins.input', side_effect=[
        "Concert 30 60",  # Invalid input for application_start_prompt (rows out of range)
        "Concert 10 20",  # Valid input for application_start_prompt
        "2",              # User selects option 2 from menu
        "3"               # Exit the application
    ])
    @patch('console_ui.ConsoleUi.menu_prompt', side_effect=[2, 3])
    @patch('console_ui.ConsoleUi.display_seating_map')
    @patch('seating_map.SeatingMap.get_confirmed_booking_map', return_value={})
    def test_main_invalid_input(self, mock_confirmed_map, mock_display_map, mock_menu_prompt, mock_input):
        # Run the main function
        with self.assertRaises(SystemExit):  # Expect SystemExit when user selects option 3
            main()

        # Assertions to verify the flow
        mock_input.assert_called()
        mock_menu_prompt.assert_called()
        mock_display_map.assert_called()
        mock_confirmed_map.assert_called()

    @patch('builtins.input', side_effect=[
        "Concert 10 20",  # Valid input for application_start_prompt
        "3"               # Exit the application
    ])
    @patch('console_ui.ConsoleUi.menu_prompt', return_value=3)
    def test_main_exit(self, mock_menu_prompt, mock_input):
        # Run the main function
        with self.assertRaises(SystemExit):  # Expect SystemExit when user selects option 3
            main()

        # Assertions to verify the flow
        mock_input.assert_called()
        mock_menu_prompt.assert_called()

if __name__ == '__main__':
    unittest.main()