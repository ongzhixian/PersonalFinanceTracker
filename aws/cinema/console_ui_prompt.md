Given the following Python code:

```console_ui.py
from typing import Any, Dict, List, Tuple, Optional
from shared_data_models import SeatingPlan, SeatStatus
from app_configuration import AppConfiguration

class ConsoleUi:
    """
    Handles all interactions with the console, including
    displaying information and getting user input.
    Adheres to the Single Responsibility Principle.
    """

    def __init__(self, config: AppConfiguration, seat_status: Optional[SeatStatus] = None) -> None:
        """
        Initializes ConsoleUi with a reference to AppConfiguration and SeatStatus.
        """
        self._config = config
        self._seat_status = seat_status or SeatStatus(config)

    def application_start_prompt(self) -> Tuple[str, int, int]:
        """
        Prompts the user for initial application details in a specific format:
        [Title] [Row] [SeatsPerRow].
        Validates the input for maximum rows (26) and seats per row (50).
        Rows are labeled from A to Z with Z nearest to the screen.
        """
        while True:
            user_input: str = input(
                "\nPlease define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n> ").strip()
            parts: List[str] = user_input.split()

            if len(parts) < 3:
                print("Invalid format. Please ensure you provide a title, number of rows, and seats per row.")
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
                if number_of_rows <= 0 or number_of_rows > 26:
                    print("Invalid input. Number of rows must be a positive integer and not exceed 26 (A-Z).")
                    continue
                if seats_per_row <= 0 or seats_per_row > 50:
                    print("Invalid input. Number of seats per row must be a positive integer and not exceed 50.")
                    continue

                return title, number_of_rows, seats_per_row
            except ValueError:
                print("Invalid input. Please ensure rows and seats per row are positive integers.")
            except IndexError:
                print("Invalid format. Please ensure you provide a title, number of rows, and seats per row.")

    def menu_prompt(self, seating_plan: SeatingPlan) -> int:
        """
        Displays the main menu and prompts the user for their selection.
        Includes movie title and available seats in the booking option.
        Displays application name from configuration.
        """
        app_name: str = self._config.get("application:name", default="Application")
        movie_title: str = seating_plan.title
        available_seats: int = seating_plan.available_seats_count
        print(f"\nWelcome to {app_name}")
        print(f"1. Book tickets for {movie_title} ({available_seats} seats available)")
        print("2. Check bookings")
        print("3. Exit")
        while True:
            try:
                choice: int = int(input("Please enter your selection:\n> ").strip())
                if choice in [1, 2, 3]:
                    return choice
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def number_of_seats_to_book_prompt(self, seating_plan: SeatingPlan) -> Optional[int]:
        """
        Prompts the user for the number of seats they wish to book.
        Input validation rules:
        1. If the number of seats is greater than the number of available seats for booking,
           pinpoint error and prompt user again.
        2. User can input empty string to end prompt.
        Returns:
            int: Number of seats to book, or None if user cancels (inputs empty string).
        """
        self.display_seating_map(seating_plan)
        available_seats: int = seating_plan.available_seats_count
        while True:
            user_input: str = input("Enter the number of seats to book (or press Enter to cancel): ").strip()
            if user_input == "":
                return None  # User chose to cancel
            try:
                num_seats: int = int(user_input)
                if num_seats <= 0:
                    print("Invalid input. Please enter a positive integer for the number of seats.")
                    continue
                if num_seats > available_seats:
                    print(f"Cannot book {num_seats} seats. Only {available_seats} seats are available.")
                    continue
                return num_seats
            except ValueError:
                print("Invalid input. Please enter a positive integer for the number of seats.")

    def display_seating_map(self, seating_plan: SeatingPlan) -> None:
        """
        Displays the current seating map with each seat symbol aligned
        with the first digit of its corresponding footer column number.
        Rows are displayed in reverse order (Z nearest to the screen at the top).
        """
        seating_map: List[List[str]] = seating_plan.plan
        if not seating_map or not seating_map[0]:
            print("\nSeating plan is empty.")
            return

        num_rows: int = len(seating_map)
        num_cols: int = len(seating_map[0])

        # Determine the width for each seat column (max 2 digits for column numbers)
        col_width: int = max(len(str(num_cols)), 2)

        # Center "S C R E E N" above the seating map
        total_width: int = 2 + num_cols * (col_width + 1) - 1  # 2 for row label, +1 for space between seats
        screen_header: str = "S C R E E N"
        screen_padding: int = max((total_width - len(screen_header)) // 2, 0)
        print("\n" + " " * screen_padding + screen_header)
        print("-" * total_width)

        # Fetch status-symbol mapping from config
        status_symbols: Dict[str, str] = self._config.get("seat_status_symbols", default={})
        status = self._seat_status

        # Map status values to config keys
        status_value_to_config_key = {
            status.AVAILABLE: "AVAILABLE",
            status.BOOKED: "BOOKED",
            status.PROPOSED: "PROPOSED",
        }

        def format_seat_symbol(seat: str) -> str:
            config_key = status_value_to_config_key.get(seat, str(seat))
            symbol = status_symbols.get(config_key, str(seat))
            return symbol.ljust(col_width)

        # Helper to get row label for reversed order
        def get_row_label(index: int) -> str:
            """Returns the row label (A-Z), with Z at index 0, A at index num_rows-1."""
            return chr(65 + (num_rows - 1 - index))

        # Print each row in reverse order
        for i in range(num_rows):
            row_index = num_rows - 1 - i  # reversed index
            row = seating_map[row_index]
            row_label: str = get_row_label(i)
            row_display: str = f"{row_label} "
            seat_symbols = [format_seat_symbol(seat) for seat in row]
            row_display += " ".join(seat_symbols)
            print(row_display)

        # Print column numbers (footer), aligned with seat symbols
        footer = "  "  # 2 spaces for row label
        footer_numbers = [
            str(col_num + 1).ljust(col_width) for col_num in range(num_cols)
        ]
        footer += " ".join(footer_numbers)
        print(footer)

    def confirm_seating_map_prompt(self) -> str:
        """
        Asks the user to confirm or reject the proposed seating map.
        Returns 'confirm' or an empty string or a seating position.
        """
        response: str = input(
            "Enter blank to accept seat selection, or enter new seating position: ").strip().lower()
        return response

    def booking_id_prompt(self) -> str:
        """
        Prompts the user for a booking ID.
        Returns the user's input.
        """
        booking_id: str = input("\nEnter booking id, or enter blank to go back to main menu:\n> ").strip()
        return booking_id

```


Update display_seating_map function as follows:

Reverse the order of row labels only.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs if any.
