
# Test Specification: `test_console_ui.py`

## **Summary**
This unit test module verifies the functionality of a `ConsoleUi` class used in a movie booking system. It ensures proper interaction with user inputs, menu navigation, seating selection, and booking confirmations using the `unittest` framework and mocks for input handling.

## **Key Components**
- **Unit tests for Console UI behavior**
- **Mocked user inputs to simulate interactions**
- **Validation of user prompts and responses**
- **Structured testing using `unittest` framework**

## **Classes and Methods Overview**
### **TestConsoleUi (unittest.TestCase)**
Unit test class for validating `ConsoleUi` functionality.

- **`setUp()`** – Initializes configuration, seat statuses, and UI instance.
- **`test_prompt_for_application_start_details_valid()`** – Tests valid input for starting application.
- **`test_prompt_for_application_start_details_invalid()`** – Ensures correct handling of invalid inputs.
- **`test_display_menu_valid_selection()`** – Tests valid menu selection handling.
- **`test_display_menu_invalid_selection_then_valid()`** – Ensures invalid menu selections are retried until valid.
- **`test_prompt_for_number_of_seats_to_book_invalid_then_valid()`** – Tests retry mechanism for incorrect seat booking inputs.
- **`test_prompt_for_booking_confirmation()`** – Confirms correct handling of booking confirmation input.
- **`test_prompt_for_booking_id()`** – Ensures correct input for booking ID retrieval.
- **`test_prompt_for_application_start_details_prompt()`** – Validates the prompt message format for starting details.
- **`test_display_menu_prompt()`** – Ensures correct menu prompt formatting.
- **`test_prompt_for_number_of_seats_to_book_prompt_message()`** – Tests seat booking prompt correctness.
- **`test_prompt_for_booking_confirmation_prompt_message()`** – Checks formatting of seat confirmation prompt.
- **`test_display_seating_map()`** – Validates seat map display formatting.
- **`test_display_exit_message()`** – Confirms correct exit message display.

## **Design Considerations**
- **Mocking `input()`** to simulate user interactions and avoid manual testing.
- **Assertions** to validate expected outputs.
- **Structured test cases** covering multiple user input scenarios.

