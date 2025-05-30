Given:

```booking_repository.py
import sqlite3
from typing import Sequence, Tuple, Dict, Iterator, List
from contextlib import contextmanager
from abc import ABC, abstractmethod

DEFAULT_DB_PATH = "seating_planner.db"


class BookingRepositoryError(Exception):
    """Custom exception for BookingRepository errors."""


class IBookingRepository(ABC):
    """Repository interface for bookings."""

    @abstractmethod
    def save_booking(self, seating_plan_title: str, booking_id: str, seats: Sequence[Tuple[int, int]]) -> None:
        pass

    @abstractmethod
    def delete_booking(self, seating_plan_title: str, booking_id: str) -> None:
        pass

    @abstractmethod
    def load_all_bookings(self, seating_plan_title: str) -> Dict[str, List[Tuple[int, int]]]:
        pass

    @abstractmethod
    def booking_exists(self, seating_plan_title: str, booking_id: str) -> bool:
        pass

    @abstractmethod
    def clear_all_bookings(self) -> None:
        pass


class BookingRepository(IBookingRepository):
    """
    Handles persistence of bookings to a SQLite3 database.
    Responsible for all DB operations.
    Bookings are associated with a seating plan title.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self._db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.DatabaseError as e:
            raise BookingRepositoryError(f"Database error: {e}") from e
        finally:
            if conn is not None:
                conn.close()

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    seating_plan_title TEXT NOT NULL,
                    booking_id TEXT NOT NULL,
                    row INTEGER NOT NULL,
                    col INTEGER NOT NULL,
                    PRIMARY KEY (seating_plan_title, booking_id, row, col)
                )
            """)
            conn.commit()

    def save_booking(
        self,
        seating_plan_title: str,
        booking_id: str,
        seats: Sequence[Tuple[int, int]]
    ) -> None:
        """
        Save a booking for a given seating plan title.
        Raises BookingRepositoryError on failure.
        """
        if not seats:
            raise ValueError("Seats list cannot be empty.")

        try:
            with self._get_connection() as conn:
                conn.executemany(
                    """
                    INSERT INTO bookings (seating_plan_title, booking_id, row, col)
                    VALUES (?, ?, ?, ?)
                    """,
                    [(seating_plan_title, booking_id, row, col) for row, col in seats]
                )
                conn.commit()
        except sqlite3.IntegrityError as e:
            raise BookingRepositoryError(f"Booking already exists or constraint failed: {e}") from e
        except sqlite3.DatabaseError as e:
            raise BookingRepositoryError(f"Database error: {e}") from e

    def delete_booking(self, seating_plan_title: str, booking_id: str) -> None:
        """
        Delete a booking for a given seating plan title.
        Raises BookingRepositoryError if booking does not exist.
        """
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    """
                    DELETE FROM bookings
                    WHERE seating_plan_title = ? AND booking_id = ?
                    """,
                    (seating_plan_title, booking_id)
                )
                conn.commit()
                if cur.rowcount == 0:
                    raise BookingRepositoryError("No such booking to delete.")
        except sqlite3.DatabaseError as e:
            raise BookingRepositoryError(f"Database error: {e}") from e

    def load_all_bookings(self, seating_plan_title: str) -> Dict[str, List[Tuple[int, int]]]:
        """
        Load all bookings for a given seating plan title.
        Returns a dict mapping booking_id to list of (row, col).
        Raises BookingRepositoryError on failure.
        """
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT booking_id, row, col
                    FROM bookings
                    WHERE seating_plan_title = ?
                    """,
                    (seating_plan_title,)
                ).fetchall()
        except sqlite3.DatabaseError as e:
            raise BookingRepositoryError(f"Database error: {e}") from e

        bookings: Dict[str, List[Tuple[int, int]]] = {}
        for row in rows:
            bookings.setdefault(row["booking_id"], []).append((row["row"], row["col"]))
        return bookings

    def booking_exists(self, seating_plan_title: str, booking_id: str) -> bool:
        """
        Check if a booking exists for the given seating plan title and booking_id.
        """
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT 1 FROM bookings
                    WHERE seating_plan_title = ? AND booking_id = ?
                    LIMIT 1
                    """,
                    (seating_plan_title, booking_id)
                )
                return cur.fetchone() is not None
        except sqlite3.DatabaseError as e:
            raise BookingRepositoryError(f"Database error: {e}") from e

    def clear_all_bookings(self) -> None:
        """
        Utility method for tests: clear all bookings.
        """
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM bookings")
                conn.commit()
        except sqlite3.DatabaseError as e:
            raise BookingRepositoryError(f"Database error: {e}") from e

```

```shared_data_models.py
# shared_data_models.py

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Any

from app_configuration import AppConfiguration


class MenuOption(Enum):
    BOOK_SEATS = auto()
    VIEW_BOOKING = auto()
    EXIT = auto()


class SeatStatus:
    """
    Encapsulates seat status codes, loaded from configuration.
    """
    AVAILABLE: str = "O"
    BOOKED: str = "B"
    PROPOSED: str = "P"

    @staticmethod
    def from_config(config: AppConfiguration) -> "SeatStatus":
        statuses: Dict[str, Any] = config.get("seat_statuses", {})
        status = SeatStatus()
        status.AVAILABLE = statuses.get("available", "O")
        status.BOOKED = statuses.get("booked", "B")
        status.PROPOSED = statuses.get("proposed", "P")
        return status


@dataclass(frozen=True)
class Seat:
    """
    Represents a single seat in the seating plan.
    """
    row: int
    col: int
    status: str


@dataclass(frozen=True)
class SeatingPlan:
    """
    Represents the complete seating plan with a title and the seat statuses.
    Includes the number of available seats.
    """
    title: str
    plan: List[List[Seat]]
    available_seats_count: int

```

```seating_planner.py
# seating_planner.py

import uuid
import string
from typing import List, Tuple, Dict, Optional
from shared_data_models import Seat, SeatingPlan, SeatStatus
from booking_repository import IBookingRepository, BookingRepository, BookingRepositoryError
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
        self.status = SeatStatus.from_config(self.config)

        self._seating_plan: List[List[Seat]] = self._initialize_seating_plan()
        self._repository: IBookingRepository = repository or BookingRepository(db_path)
        self._confirmed_bookings: Dict[str, List[Tuple[int, int]]] = self._repository.load_all_bookings(self.title)
        self._apply_bookings_to_plan()

    def _initialize_seating_plan(self) -> List[List[Seat]]:
        return [
            [Seat(r, c, self.status.AVAILABLE) for c in range(self.seats_per_row)]
            for r in range(self.num_rows)
        ]

    def _apply_bookings_to_plan(self) -> None:
        """
        Apply all confirmed bookings to the seating plan.
        """
        for seats in self._confirmed_bookings.values():
            for row, col in seats:
                if 0 <= row < self.num_rows and 0 <= col < self.seats_per_row:
                    self._seating_plan[row][col] = Seat(row, col, self.status.BOOKED)

    def get_seating_plan(self, booking_id: Optional[str] = None) -> Optional[SeatingPlan]:
        """
        Returns the current seating plan.
        If booking_id is provided, marks those seats as 'proposed' (self.status.PROPOSED).
        If booking_id does not exist, returns None.
        """
        plan_copy: List[List[Seat]] = [
            [Seat(seat.row, seat.col, seat.status) for seat in row]
            for row in self._seating_plan
        ]
        available_count = sum(
            seat.status == self.status.AVAILABLE
            for row in plan_copy for seat in row
        )

        if booking_id:
            if booking_id not in self._confirmed_bookings:
                return None
            for r, c in self._confirmed_bookings[booking_id]:
                seat = plan_copy[r][c]
                if seat.status == self.status.BOOKED:
                    plan_copy[r][c] = Seat(r, c, self.status.PROPOSED)
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

        # Update in-memory plan
        for r, c in seats_to_book:
            self._seating_plan[r][c] = Seat(r, c, self.status.BOOKED)

        booking_id = str(uuid.uuid4())
        self._confirmed_bookings[booking_id] = seats_to_book
        try:
            self._repository.save_booking(self.title, booking_id, seats_to_book)
        except BookingRepositoryError as e:
            # Rollback in-memory state
            for r, c in seats_to_book:
                self._seating_plan[r][c] = Seat(r, c, self.status.AVAILABLE)
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
                if self._seating_plan[row][col].status == self.status.BOOKED:
                    self._seating_plan[row][col] = Seat(row, col, self.status.AVAILABLE)
        del self._confirmed_bookings[booking_id]
        try:
            self._repository.delete_booking(self.title, booking_id)
        except BookingRepositoryError as e:
            # Rollback in-memory state
            for row, col in seats_to_unbook:
                self._seating_plan[row][col] = Seat(row, col, self.status.BOOKED)
            self._confirmed_bookings[booking_id] = seats_to_unbook
            raise e
        return booking_id

```

Perform a code review to fix and refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file using unittest.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.



Update get_seating_plan function as follows:

If booking_id is provided, return None if booking_id does not exist.


Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.


----
Perform a code review to fix and refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file using unittest.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.
