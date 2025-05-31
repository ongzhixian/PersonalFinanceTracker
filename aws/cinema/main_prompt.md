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

```main.py
from app_configuration import AppConfiguration
from console_ui import ConsoleUi
# from seating_planner import SeatingPlanner

def main():
    """
    Main function to run the seating planner application.
   Orchestrates interactions between ConsoleUi and SeatingPlanner.
    """
    app_configuration = AppConfiguration('./app_configuration.json')
    console_ui = ConsoleUi(app_configuration)

if __name__ == '__main__':
    main()

```

You are an extremely picky code reviewer.
Review code and provide a fully refactored and optimized code.
Refactored code should not need further changes should you review it again.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Refactored code should prefer Protocol over ABC unless there is good reason
Code should be easily testable using unittest.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.
Add any missing docstrings.

If code Final, Polished Code (No Further Review Needed)

---






















Given:

```seating_planner.py
import uuid
import string
from typing import List, Tuple, Dict, Optional
from shared_data_models import Seat, SeatingPlan, SeatStatus
from booking_repository import BookingRepository
from app_configuration import AppConfiguration

class SeatingPlanner:
    """
    Manages the seating plan logic, including booking,
    proposing seats, and confirming bookings.
    Each instance is associated with a specific seating plan title.
    """

    def __init__(
        self,
        title: str,
        num_rows: int,
        seats_per_row: int,
        db_path: str = "seating_planner.db",
        config: Optional[AppConfiguration] = None
    ):
        if not isinstance(title, str) or not title:
            raise ValueError("Title must be a non-empty string.")
        if not isinstance(num_rows, int) or num_rows <= 0:
            raise ValueError("Number of rows must be a positive integer.")
        if not isinstance(seats_per_row, int) or seats_per_row <= 0:
            raise ValueError("Seats per row must be a positive integer.")

        self.title: str = title
        self.num_rows: int = num_rows
        self.seats_per_row: int = seats_per_row
        self.config = config or AppConfiguration()
        self.status = SeatStatus(self.config)

        self._seating_plan: List[List[Seat]] = [
            [Seat(r, c, self.status.AVAILABLE) for c in range(self.seats_per_row)] for r in range(self.num_rows)
        ]
        self._db = BookingRepository(db_path)
        self._confirmed_bookings: Dict[str, List[Tuple[int, int]]] = self._db.load_all_bookings(self.title)
        self._apply_bookings_to_plan()

    def _apply_bookings_to_plan(self) -> None:
        """
        Apply all confirmed bookings to the seating plan.
        """
        for seats in self._confirmed_bookings.values():
            for row, col in seats:
                if 0 <= row < self.num_rows and 0 <= col < self.seats_per_row:
                    self._seating_plan[row][col].status = self.status.BOOKED

    def get_seating_plan(self, booking_id: Optional[str] = None) -> Optional[SeatingPlan]:
        """
        Returns the current seating plan.
        If booking_id is provided, marks those seats as 'proposed' (self.status.PROPOSED).
        If booking_id does not exist, returns None.
        """
        current_plan_status = [[seat.status for seat in row] for row in self._seating_plan]
        available_count = sum(row.count(self.status.AVAILABLE) for row in current_plan_status)

        if booking_id:
            if booking_id not in self._confirmed_bookings:
                return None
            plan_with_proposed = [row[:] for row in current_plan_status]
            for r, c in self._confirmed_bookings[booking_id]:
                if plan_with_proposed[r][c] == self.status.BOOKED:
                    plan_with_proposed[r][c] = self.status.PROPOSED
            return SeatingPlan(title=self.title, plan=plan_with_proposed, available_seats_count=available_count)

        return SeatingPlan(title=self.title, plan=current_plan_status, available_seats_count=available_count)

    def _seat_label_to_indices(self, seat_label: str) -> Tuple[int, int]:
        """
        Convert a seat label (e.g., 'A1') to (row, col) indices.
        """
        if not seat_label or len(seat_label) < 2:
            raise ValueError("Invalid seat label format.")
        row_char = seat_label[0].upper()
        if row_char not in string.ascii_uppercase:
            raise ValueError("Invalid row character in seat label.")
        row = ord(row_char) - ord('A')
        try:
            col = int(seat_label[1:]) - 1
        except ValueError:
            raise ValueError("Invalid column number in seat label.")
        if not (0 <= row < self.num_rows and 0 <= col < self.seats_per_row):
            raise ValueError("Seat label out of range.")
        return row, col

    def book_seats(self, number_of_seats: int, start_seat: Optional[str] = None) -> str:
        """
        Book a number of seats, optionally starting from a specific seat.
        Returns the booking ID.
        """
        if not isinstance(number_of_seats, int) or number_of_seats <= 0:
            raise ValueError("Number of seats must be a positive integer.")

        seats_to_book: List[Tuple[int, int]] = []
        rows_order: List[int] = list(range(self.num_rows - 1, -1, -1))  # Furthest from screen first

        if start_seat:
            row, col = self._seat_label_to_indices(start_seat)
            for c in range(col, self.seats_per_row):
                if self._seating_plan[row][c].status == self.status.AVAILABLE:
                    seats_to_book.append((row, c))
                    if len(seats_to_book) == number_of_seats:
                        break
                else:
                    break
            if row in rows_order:
                rows_order.remove(row)

        seats_needed = number_of_seats - len(seats_to_book)
        for r in rows_order:
            if seats_needed <= 0:
                break
            available = [c for c, seat in enumerate(self._seating_plan[r]) if seat.status == self.status.AVAILABLE]
            while seats_needed > 0 and available:
                max_block_size = min(seats_needed, len(available))
                found_block = False
                for block_size in range(max_block_size, 0, -1):
                    best_block = None
                    min_dist = None
                    for i in range(len(available) - block_size + 1):
                        block = available[i:i + block_size]
                        block_center = sum(block) / block_size
                        center = self.seats_per_row / 2 - 0.5
                        dist = abs(block_center - center)
                        if min_dist is None or dist < min_dist:
                            min_dist = dist
                            best_block = block
                    if best_block:
                        for c in best_block:
                            seats_to_book.append((r, c))
                            available.remove(c)
                        seats_needed = number_of_seats - len(seats_to_book)
                        found_block = True
                        break
                if not found_block:
                    break

        if len(seats_to_book) < number_of_seats:
            raise ValueError("Not enough seats available to fulfill the booking.")

        for r, c in seats_to_book:
            self._seating_plan[r][c].status = self.status.BOOKED

        booking_id = str(uuid.uuid4())
        self._confirmed_bookings[booking_id] = seats_to_book
        self._db.save_booking(self.title, booking_id, seats_to_book)
        return booking_id

    def unbook_seats(self, booking_id: str) -> str:
        """
        Cancel a booking by booking ID.
        """
        if booking_id not in self._confirmed_bookings:
            raise ValueError(f"Booking ID '{booking_id}' not found.")

        seats_to_unbook = self._confirmed_bookings[booking_id]
        for row, col in seats_to_unbook:
            if 0 <= row < self.num_rows and 0 <= col < self.seats_per_row:
                if self._seating_plan[row][col].status == self.status.BOOKED:
                    self._seating_plan[row][col].status = self.status.AVAILABLE
        del self._confirmed_bookings[booking_id]
        self._db.delete_booking(self.title, booking_id)
        return booking_id
```

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
        Row labels are reversed (first row is Z, last is A), but seat data is not reversed.
        """
        seating_map: List[List[str]] = seating_plan.plan
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

        status_value_to_config_key = {
            status.AVAILABLE: "AVAILABLE",
            status.BOOKED: "BOOKED",
            status.PROPOSED: "PROPOSED",
        }

        def format_seat_symbol(seat: str) -> str:
            config_key = status_value_to_config_key.get(seat, str(seat))
            symbol = status_symbols.get(config_key, str(seat))
            return symbol.ljust(col_width)

        def get_reversed_row_label(index: int) -> str:
            """Returns the row label (A-Z), with Z for index 0, A for index num_rows-1."""
            return chr(ord('A') + (num_rows - 1 - index))

        # Print each row in order, but with reversed row labels
        for i, row in enumerate(seating_map):
            row_label: str = get_reversed_row_label(i)
            seat_symbols: List[str] = [format_seat_symbol(seat) for seat in row]
            row_display: str = f"{row_label} " + " ".join(seat_symbols)
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

```main.py
from app_configuration import AppConfiguration
from console_ui import ConsoleUi
from seating_planner import SeatingPlanner

def main():
    """
    Main function to run the seating planner application.
   Orchestrates interactions between ConsoleUi and SeatingPlanner.
    """
    app_configuration = AppConfiguration()
    console_ui = ConsoleUi(app_configuration)

    (title, number_of_rows, seats_per_row) = console_ui.application_start_prompt()
    seating_planner = SeatingPlanner(title, number_of_rows, seats_per_row)
    while True:
        seating_plan = seating_planner.get_seating_plan()
        #console_ui.display_seating_map(seating_plan)
        user_selection = console_ui.menu_prompt(seating_plan)

        if user_selection == 1:
            print(seating_plan)
            number_of_seats_to_book = console_ui.number_of_seats_to_book_prompt(seating_plan)
            if number_of_seats_to_book is None:
                continue
            start_seat = None
            while True:
                booking_id = seating_planner.book_seats(number_of_seats_to_book, start_seat=start_seat)
                seating_plan = seating_planner.get_seating_plan(booking_id)

                console_ui.display_seating_map(seating_plan)
                response = console_ui.confirm_seating_map_prompt()
                if response == '':
                    print('booking_id', booking_id)
                    break
                start_seat = response
                seating_planner.unbook_seats(booking_id)
        if user_selection == 2:
            while True:
                booking_id = console_ui.booking_id_prompt()
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

Perform a code review to refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.
