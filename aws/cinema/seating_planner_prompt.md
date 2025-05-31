Given:

```app_configuration
AppConfiguration: Thread-safe singleton class providing access to application configuration.
AppConfiguration.__init__: Initializes the application configuration using a file or dictionary.
AppConfiguration.reload: Reloads configuration if loaded from a file.
AppConfiguration.get: Retrieves a configuration value using a colon-separated path.
AppConfiguration.contains: Checks if a configuration key exists.
AppConfiguration.reset_instance: Resets the singleton instance.
```

```booking_repository
BookingRepositoryError: Custom exception for booking-related errors.

IBookingRepository: Protocol interface defining booking operations.

BookingRepository: Implements booking persistence in an SQLite database.
BookingRepository._init_db(): Initializes the bookings table in the database.
BookingRepository.save_booking(): Saves a booking with a list of seat coordinates.
BookingRepository.delete_booking(): Deletes a booking by its ID.
BookingRepository.load_all_bookings(): Loads all bookings for a specific seating plan.
BookingRepository.booking_exists(): Checks if a booking exists in the database.
BookingRepository.clear_all_bookings(): Removes all bookings, mainly for testing purposes.
```

```shared_data_models
SeatStatus – Holds seat status codes dynamically loaded from configuration.
SeatStatus.from_config(config) – Initializes seat statuses using a configuration object.

Seat – Represents a single seat with row, column, and status attributes.
Seat.is_available(seat_status) – Checks if a seat is available based on a given seat status.

SeatingPlan – Represents a structured seating plan with a list of seats and available seat count.
SeatingPlan.__post_init__() – Ensures the seating plan has valid data integrity.
SeatingPlan.get_available_seats(seat_status) – Retrieves all seats marked as available.
```

```seating_planner.py
import string
import uuid
from typing import List, Tuple, Dict, Optional

from app_configuration import AppConfiguration
from booking_repository import IBookingRepository, BookingRepository, BookingRepositoryError
from shared_data_models import Seat, SeatingPlan, SeatStatus


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
        config: Optional[AppConfiguration] = None,
        repository: Optional[IBookingRepository] = None
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
        self.status_map = SeatStatus.from_config(self.config)

        self._seating_plan: List[List[Seat]] = self._initialize_seating_plan()
        self._repository: IBookingRepository = repository or BookingRepository(db_path)
        self._confirmed_bookings: Dict[str, List[Tuple[int, int]]] = self._repository.load_all_bookings(self.title)
        self._apply_bookings_to_plan()

    def _initialize_seating_plan(self) -> List[List[Seat]]:
        return [
            [Seat(r, c, self.status_map["AVAILABLE"]) for c in range(self.seats_per_row)]
            for r in range(self.num_rows)
        ]

    def _apply_bookings_to_plan(self) -> None:
        """
        Apply all confirmed bookings to the seating plan.
        """
        for seats in self._confirmed_bookings.values():
            for row, col in seats:
                if 0 <= row < self.num_rows and 0 <= col < self.seats_per_row:
                    self._seating_plan[row][col] = Seat(row, col, self.status_map["BOOKED"])

    def get_seating_plan(self, booking_id: Optional[str] = None) -> Optional[SeatingPlan]:
        """
        Returns the current seating plan.
        If booking_id is provided, marks those seats as 'proposed' (self.status_map["PROPOSED"]).
        If booking_id does not exist, returns None.
        """
        plan_copy: List[List[Seat]] = [
            [Seat(seat.row, seat.col, seat.status) for seat in row]
            for row in self._seating_plan
        ]
        available_count = sum(
            seat.status == self.status_map["AVAILABLE"]
            for row in plan_copy for seat in row
        )

        if booking_id:
            if booking_id not in self._confirmed_bookings:
                return None
            for r, c in self._confirmed_bookings[booking_id]:
                seat = plan_copy[r][c]
                if seat.status == self.status_map["BOOKED"]:
                    plan_copy[r][c] = Seat(r, c, self.status_map["PROPOSED"])
            return SeatingPlan(title=self.title, plan=plan_copy, available_seats_count=available_count)

        return SeatingPlan(title=self.title, plan=plan_copy, available_seats_count=available_count)

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
                if self._seating_plan[row][c].status == self.status_map["AVAILABLE"]:
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
            available = [c for c, seat in enumerate(self._seating_plan[r]) if seat.status == self.status_map["AVAILABLE"]]
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

        # Update in-memory plan
        for r, c in seats_to_book:
            self._seating_plan[r][c] = Seat(r, c, self.status_map["BOOKED"])

        booking_id = str(uuid.uuid4())
        self._confirmed_bookings[booking_id] = seats_to_book
        try:
            self._repository.add_booking(self.title, booking_id, seats_to_book)
        except BookingRepositoryError as e:
            # Rollback in-memory state
            for r, c in seats_to_book:
                self._seating_plan[r][c] = Seat(r, c, self.status_map["AVAILABLE"])
            del self._confirmed_bookings[booking_id]
            raise e
        return booking_id

    def cancel_booking(self, booking_id: str) -> str:
        """
        Cancel a booking by booking ID.
        """
        if booking_id not in self._confirmed_bookings:
            raise ValueError(f"Booking ID '{booking_id}' not found.")

        seats_to_unbook = self._confirmed_bookings[booking_id]
        for row, col in seats_to_unbook:
            if 0 <= row < self.num_rows and 0 <= col < self.seats_per_row:
                if self._seating_plan[row][col].status == self.status_map["BOOKED"]:
                    self._seating_plan[row][col] = Seat(row, col, self.status_map["AVAILABLE"])
        del self._confirmed_bookings[booking_id]
        try:
            self._repository.delete_booking(self.title, booking_id)
        except BookingRepositoryError as e:
            # Rollback in-memory state
            for row, col in seats_to_unbook:
                self._seating_plan[row][col] = Seat(row, col, self.status_map["BOOKED"])
            self._confirmed_bookings[booking_id] = seats_to_unbook
            raise e
        return booking_id

```


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
Review code.
Generate unit tests using unittest.
All unit tests must be runnable.
All unit tests must pass.