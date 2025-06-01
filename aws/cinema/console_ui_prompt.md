Given:

```shared_data_models
Seat – Represents a single seat with row, column, and status attributes.
Seat.is_available(seat_status) – Checks if a seat is available based on a given seat status.

SeatStatus – Holds seat status codes dynamically loaded from configuration.
SeatStatus.from_config(config) – Initializes seat statuses using a configuration object.

SeatingPlan – Represents a structured seating plan with a list of seats and available seat count.
SeatingPlan.__post_init__() – Ensures the seating plan has valid data integrity.
SeatingPlan.get_available_seats(seat_status) – Retrieves all seats marked as available.
```

```app_configuration
AppConfiguration: Thread-safe singleton class providing access to application configuration.
AppConfiguration.__init__: Initializes the application configuration using a file or dictionary.
AppConfiguration.reload: Reloads configuration if loaded from a file.
AppConfiguration.get: Retrieves a configuration value using a colon-separated path.
AppConfiguration.contains: Checks if a configuration key exists.
AppConfiguration.reset_instance: Resets the singleton instance.
```

```console_ui.py
from typing import Dict, List, Tuple, Optional

from app_configuration import AppConfiguration
from shared_data_models import Seat, SeatingPlan, SeatStatus

class ConsoleUi:
    """
    Handles user interactions through the console.
    Adheres to the Single Responsibility Principle.
    """

    MAX_ROWS = 26
    MAX_SEATS_PER_ROW = 50

    def __init__(self, config: AppConfiguration, seat_status: Optional[SeatStatus] = None) -> None:
        """
        Initializes the ConsoleUI with application configuration and seat status.
        """
        self._config = config
        self._seat_status = seat_status or SeatStatus.from_config(config)

    def prompt_for_application_start_details(self) -> Tuple[str, int, int] | None:
        """
        Prompts the user for initial application details in format: [Title] [Rows] [SeatsPerRow].
        Validates input constraints for rows (max 26) and seats per row (max 50).
        Returns:
            Tuple[str, int, int]: Movie title, number of rows, and seats per row.
        """
        while True:
            user_input: str = input("\nDefine movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n> ").strip()
            parts: List[str] = user_input.split()

            if len(parts) < 3:
                print("Invalid format. Please provide title, number of rows, and seats per row.")
                continue

            title_parts: List[str] = parts[:-2]
            title: str = " ".join(title_parts)

            try:
                number_of_rows_str: str = parts[-2]
                seats_per_row_str: str = parts[-1]

                number_of_rows: int = int(number_of_rows_str)
                seats_per_row: int = int(seats_per_row_str)

                if not title:
                    print("Invalid input. Title cannot be empty.")
                    continue
                if number_of_rows <= 0 or number_of_rows > self.MAX_ROWS:
                    print(f"Invalid input. Number of rows must be between 1 and {self.MAX_ROWS}.")
                    continue
                if seats_per_row <= 0 or seats_per_row > self.MAX_SEATS_PER_ROW:
                    print(f"Invalid input. Seats per row must be between 1 and {self.MAX_SEATS_PER_ROW}.")
                    continue

                return title, number_of_rows, seats_per_row
            except ValueError:
                print("Invalid input. Rows and seats per row must be positive integers.")
            except IndexError:
                print("Invalid format. Please ensure you provide a title, number of rows, and seats per row.")

    def display_menu(self, seating_plan: SeatingPlan) -> int:
        """
        Displays the main menu and prompts the user for their selection.
        Returns:
            int: User's selected menu option.
        """
        app_name = self._config.get("application:name", default="Movie Booking System")
        movie_title = seating_plan.title
        available_seats = seating_plan.available_seats_count

        print(f"\nWelcome to {app_name}")
        print(f"1. Book tickets for {movie_title} ({available_seats} seats available)")
        print("2. Check bookings")
        print("3. Exit")

        while True:
            try:
                choice = int(input("Enter selection (1-3):\n> ").strip())
                if choice in [1, 2, 3]:
                    return choice
                print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def prompt_for_number_of_seats_to_book(self, seating_plan: SeatingPlan) -> Optional[int]:
        """
        Prompts user for the number of seats they want to book.
        Validates availability constraints.
        Returns:
            int | None: Number of seats requested, or None if canceled.
        """
        self.display_seating_map(seating_plan)
        available_seats = seating_plan.available_seats_count
        while True:
            user_input: str = input("Enter number of seats to book (or press Enter to cancel): ").strip()
            if user_input == '':
                return None

            try:
                num_seats:int = int(user_input)
                if num_seats <= 0:
                    print("Please enter a positive number.")
                    continue
                if num_seats > available_seats:
                    print(f"Cannot book {num_seats} seats. Only {available_seats} seats available.")
                    continue
                return num_seats
            except ValueError:
                print("Invalid input. Please enter a positive integer.")

    def display_seating_map(self, seating_plan: SeatingPlan) -> None:
        """
        Displays current seating map with labeled rows and columns.
        """
        seating_map: List[List[Seat]] = seating_plan.plan
        if not seating_map or not seating_map[0]:
            print("\nSeating plan is empty.")
            return

        num_rows: int = len(seating_map)
        num_cols: int = len(seating_map[0])

        col_width: int = max(len(str(num_cols)), 2)
        total_width: int = 2 + num_cols * (col_width + 1) - 1
        screen_header: str = "S C R E E N"
        screen_padding: int = max((total_width - len(screen_header)) // 2, 0)
        print("\n" + " " * screen_padding + screen_header)
        print("-" * total_width)

        status_symbols: Dict[str, str] = self._config.get("seat_status_symbols", default={})
        status = self._seat_status

        status_map = {
            status.AVAILABLE: "AVAILABLE",
            status.BOOKED: "BOOKED",
            status.PROPOSED: "PROPOSED",
        }

        def format_seat(seat: Seat) -> str:
            """Formats seat display using configured symbols."""
            return status_symbols.get(status_map.get(seat.status, str(seat)), str(seat)).ljust(col_width)

        def get_row_label(index: int) -> str:
            """Returns A-Z row label (reversed, so Z is first)."""
            return chr(ord('A') + (num_rows - 1 - index))

        for i, row in enumerate(seating_map):
            print(f"{get_row_label(i)} " + " ".join(format_seat(seat) for seat in row))

        footer_labels = ["  "] + [str(col + 1).ljust(col_width) for col in range(num_cols)]
        print(" ".join(footer_labels))

    def propmpt_for_booking_confirmation(self) -> str:
        """
        Asks user to confirm or modify seat selection.
        Returns:
            str: 'confirm' if accepted, or new seating position.
        """
        return input("Press Enter to confirm selection or enter new position: ").strip().lower()

    def prompt_for_booking_id(self) -> str:
        """
        Prompts user for a booking ID.
        Returns:
            str: Booking ID or empty string to return to menu.
        """
        return input("\nEnter booking ID (or press Enter to cancel):\n> ").strip()

```

Generate unit tests using unittest.

You are an extremely picky code reviewer.
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

Update display_seating_map function as follows:

Reverse the order of row labels only.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs if any.
