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
            user_input: str = input("\nPlease define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n> ").strip()
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
                choice = int(input("Please enter your selection (1-3):\n> ").strip())
                if choice in [1, 2, 3]:
                    return choice
                print("\nInvalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("\nInvalid input. Please enter a number.")

    def prompt_for_number_of_seats_to_book(self, seating_plan: SeatingPlan) -> Optional[int]:
        """
        Prompts user for the number of seats they want to book.
        Validates availability constraints.
        Returns:
            int | None: Number of seats requested, or None if canceled.
        """
        # self.display_seating_map(seating_plan)
        available_seats = seating_plan.available_seats_count
        while True:
            user_input: str = input("\nEnter number of tickets to book, or enter blank to go back to main menu:\n> ").strip()
            if user_input == '':
                return None

            try:
                num_seats:int = int(user_input)
                if num_seats <= 0:
                    print("Please enter a positive number.")
                    continue
                if num_seats > available_seats:
                    print(f"\nSorry, there are only {available_seats} available.")
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

        print(f"\nBooking id: {seating_plan.booking_id}")
        print("Selected seats:")

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

        footer_labels = [" "] + [str(col + 1).ljust(col_width) for col in range(num_cols)]
        print(" ".join(footer_labels))

    def prompt_for_booking_confirmation(self) -> str:
        """
        Asks user to confirm or modify seat selection.
        Returns:
            str: 'confirm' if accepted, or new seating position.
        """
        return input("\nEnter blank to accept seat selection, or enter new seating position:\n> ").strip().lower()

    def prompt_for_booking_id(self) -> str:
        """
        Prompts user for a booking ID.
        Returns:
            str: Booking ID or empty string to return to menu.
        """
        return input("\nEnter booking id, or enter blank to back to main menu:\n> ").strip()

    def display_exit_message(self) -> None:
        app_name = self._config.get("application:name", default="Movie Booking System")
        print(f"\nThank you for using {app_name} system. Bye!")
