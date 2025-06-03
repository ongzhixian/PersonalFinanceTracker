# Console UI Design Specification

## Summary
The `ConsoleUi` class provides a console-based user interface for a movie booking system. It enables users to define seating arrangements, interact with menus, book seats, view seating maps, and manage bookings.

## Class Overview

### `ConsoleUi`
Handles user interactions through the console while adhering to the Single Responsibility Principle.

## Methods Overview

- **`__init__(config, seat_status=None)`**  
  Initializes the Console UI with application configuration and seat status.

- **`prompt_for_application_start_details()`**  
  Prompts user to input movie title, number of rows, and seats per row, ensuring valid constraints.

- **`display_menu(seating_plan)`**  
  Shows the main menu and gets the user's selection.

- **`prompt_for_number_of_seats_to_book(seating_plan)`**  
  Asks user for the number of seats they wish to book, checking availability.

- **`display_seating_map(seating_plan)`**  
  Prints the seating plan with labeled rows and columns.

- **`prompt_for_booking_confirmation()`**  
  Asks user to confirm seat selection or modify their choice.

- **`prompt_for_booking_id()`**  
  Requests a booking ID from the user.

- **`display_exit_message()`**  
  Displays an exit message thanking the user for using the system.
