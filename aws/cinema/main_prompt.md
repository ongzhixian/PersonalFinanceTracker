You are a world class software engineer.
Given Python code:

```app_configuration
AppConfiguration: Thread-safe singleton class providing access to application configuration.
AppConfiguration.__init__: Initializes the application configuration using a file or dictionary.
AppConfiguration.reload: Reloads configuration if loaded from a file.
AppConfiguration.get: Retrieves a configuration value using a colon-separated path.
AppConfiguration.contains: Checks if a configuration key exists.
AppConfiguration.reset_instance: Resets the singleton instance.
```

```console_ui
ConsoleUi: Manages console-based user interactions for booking movie tickets.
ConsoleUi.__init__: Initializes console UI with application configuration and seat status.
ConsoleUi.prompt_for_application_start_details: Collects and validates movie title and seating map details.
ConsoleUi.display_menu: Shows main menu options and retrieves user selection.
ConsoleUi.prompt_for_number_of_seats_to_book: Prompts user for seat booking quantity and validates availability.
ConsoleUi.display_seating_map: Displays the current seating map with labeled rows and columns.
ConsoleUi.propmpt_for_booking_confirmation: Asks user to confirm or modify seat selection.
ConsoleUi.prompt_for_booking_id: Collects booking ID from the user.
```

```seating_plan
SeatingPlanner – Handles seat booking, seat status updates, and seating arrangements.
SeatingPlanner.__init__ – Initializes the seating plan with configurations and loads existing bookings.
SeatingPlanner._initialize_seating_plan – Creates an initial seating plan with all seats marked as available.
SeatingPlanner._apply_bookings_to_plan – Updates the seating plan based on confirmed bookings.
SeatingPlanner.get_seating_plan – Retrieves the current seating plan, optionally marking specific seats as proposed.
SeatingPlanner._seat_label_to_indices – Converts a seat label (e.g., 'A1') into row and column indices.
SeatingPlanner.book_seats – Books a number of available seats and assigns a unique booking ID.
SeatingPlanner.cancel_booking – Cancels an existing booking and frees up the previously occupied seats.

```

```main.py
from app_configuration import AppConfiguration
from console_ui import ConsoleUi
from seating_planner import SeatingPlanner

def main():
    """
    Main function to run the seating planner application.
   Orchestrates interactions between ConsoleUi and SeatingPlanner.
    """
    app_configuration = AppConfiguration('./app_configuration.json')
    console_ui = ConsoleUi(app_configuration)

    (title, number_of_rows, seats_per_row) = console_ui.prompt_for_application_start_details()
    seating_planner = SeatingPlanner(title, number_of_rows, seats_per_row)
    while True:
        seating_plan = seating_planner.get_seating_plan()
        #console_ui.display_seating_map(seating_plan)
        user_selection = console_ui.display_menu(seating_plan)

        if user_selection == 1:
            print(seating_plan)
            number_of_seats_to_book = console_ui.prompt_for_number_of_seats_to_book(seating_plan)
            if number_of_seats_to_book is None:
                continue
            start_seat = None
            while True:
                booking_id = seating_planner.book_seats(number_of_seats_to_book, start_seat=start_seat)
                seating_plan = seating_planner.get_seating_plan(booking_id)

                console_ui.display_seating_map(seating_plan)
                response = console_ui.propmpt_for_booking_confirmation()
                if response == '':
                    print('booking_id', booking_id)
                    break
                start_seat = response
                seating_planner.cancel_booking(booking_id)
        if user_selection == 2:
            while True:
                booking_id = console_ui.prompt_for_booking_id()
                if len(booking_id.strip()) > 0:
                    seating_plan = seating_planner.get_seating_plan(booking_id)
                    if seating_plan is None:
                        print("booking_id cannot be found.")
                        continue
                    console_ui.display_seating_map(seating_plan)
                    break
                else:
                    break
        if user_selection == 3:
            exit(0)

if __name__ == '__main__':
    main()

```

You are an extremely picky code reviewer for main.py.
Review code and provide a fully refactored and optimized code.
Refactored code should not need further changes should you review it again.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Code should be easily testable using unittest.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.
Add any missing docstrings.


2.
Refactored code should not need further changes should you review it again.

3.
Generate unit tests using unittest.
