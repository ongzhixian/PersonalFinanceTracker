Given:

```booking_repository.py
import sqlite3
from typing import Sequence, Tuple, Dict, List, Iterator, Protocol
from contextlib import contextmanager

DEFAULT_DB_PATH = "seating_planner.db"


class BookingRepositoryError(Exception):
    """Custom exception for BookingRepository errors."""


class IBookingRepository(Protocol):
    """Protocol interface for bookings."""

    def save_booking(self, seating_plan_title: str, booking_id: str, seats: Sequence[Tuple[int, int]]) -> None:
        ...

    def delete_booking(self, seating_plan_title: str, booking_id: str) -> None:
        ...

    def load_all_bookings(self, seating_plan_title: str) -> Dict[str, List[Tuple[int, int]]]:
        ...

    def booking_exists(self, seating_plan_title: str, booking_id: str) -> bool:
        ...

    def clear_all_bookings(self) -> None:
        ...


class BookingRepository(IBookingRepository):
    """Handles persistence of bookings in SQLite."""

    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the bookings table."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                seating_plan_title TEXT NOT NULL,
                booking_id TEXT NOT NULL,
                row INTEGER NOT NULL,
                col INTEGER NOT NULL,
                PRIMARY KEY (seating_plan_title, booking_id, row, col)
            )
        """)

    def save_booking(self, seating_plan_title: str, booking_id: str, seats: Sequence[Tuple[int, int]]) -> None:
        """Save a booking."""
        if not seats:
            raise ValueError("Seats list cannot be empty.")

        try:
            self._conn.executemany(
                """
                INSERT INTO bookings (seating_plan_title, booking_id, row, col)
                VALUES (?, ?, ?, ?)
                """,
                [(seating_plan_title, booking_id, row, col) for row, col in seats]
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise BookingRepositoryError("Booking already exists or constraint failed.")

    def delete_booking(self, seating_plan_title: str, booking_id: str) -> None:
        """Delete a booking."""
        cur = self._conn.execute(
            """
            DELETE FROM bookings WHERE seating_plan_title = ? AND booking_id = ?
            """,
            (seating_plan_title, booking_id)
        )
        self._conn.commit()
        if cur.rowcount == 0:
            raise BookingRepositoryError("No such booking to delete.")

    def load_all_bookings(self, seating_plan_title: str) -> Dict[str, List[Tuple[int, int]]]:
        """Load all bookings."""
        rows = self._conn.execute(
            """
            SELECT booking_id, row, col FROM bookings WHERE seating_plan_title = ?
            """,
            (seating_plan_title,)
        ).fetchall()

        bookings: Dict[str, List[Tuple[int, int]]] = {}
        for row in rows:
            bookings.setdefault(row["booking_id"], []).append((row["row"], row["col"]))
        return bookings

    def booking_exists(self, seating_plan_title: str, booking_id: str) -> bool:
        """Check if a booking exists."""
        return self._conn.execute(
            """
            SELECT 1 FROM bookings WHERE seating_plan_title = ? AND booking_id = ? LIMIT 1
            """,
            (seating_plan_title, booking_id)
        ).fetchone() is not None

    def clear_all_bookings(self) -> None:
        """Clear all bookings (for testing)."""
        self._conn.execute("DELETE FROM bookings")
        self._conn.commit()

```

Generate plantuml for class diagram.
Add title and caption.
