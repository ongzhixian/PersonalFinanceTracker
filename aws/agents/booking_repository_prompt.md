Given:

```booking_repository.py
import sqlite3
from typing import Sequence, Tuple, Dict, Optional, Any
from contextlib import contextmanager


class BookingRepositoryError(Exception):
    """Custom exception for BookingRepository errors."""


class BookingRepository:
    """
    Handles persistence of bookings to a SQLite3 database.
    Responsible for all DB operations.
    Bookings are associated with a seating plan title.
    """

    def __init__(self, db_path: str = "seating_planner.db"):
        self._db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Any:
        try:
            conn = sqlite3.connect(self._db_path)
            yield conn
        except sqlite3.DatabaseError as e:
            raise BookingRepositoryError(f"Database error: {e}") from e
        finally:
            if 'conn' in locals():
                conn.close()

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("""
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
                c = conn.cursor()
                c.executemany(
                    """
                    INSERT INTO bookings (seating_plan_title, booking_id, row, col)
                    VALUES (?, ?, ?, ?)
                    """,
                    [(seating_plan_title, booking_id, row, col) for row, col in seats]
                )
                conn.commit()
        except sqlite3.IntegrityError as e:
            raise BookingRepositoryError(f"Booking already exists or constraint failed: {e}") from e

    def delete_booking(self, seating_plan_title: str, booking_id: str) -> None:
        """
        Delete a booking for a given seating plan title.
        Raises BookingRepositoryError on failure.
        """
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                DELETE FROM bookings
                WHERE seating_plan_title = ? AND booking_id = ?
                """,
                (seating_plan_title, booking_id)
            )
            conn.commit()

    def load_all_bookings(self, seating_plan_title: str) -> Dict[str, Sequence[Tuple[int, int]]]:
        """
        Load all bookings for a given seating plan title.
        Returns a dict mapping booking_id to list of (row, col).
        Raises BookingRepositoryError on failure.
        """
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT booking_id, row, col
                FROM bookings
                WHERE seating_plan_title = ?
                """,
                (seating_plan_title,)
            )
            rows = c.fetchall()

        bookings: Dict[str, list[Tuple[int, int]]] = {}
        for booking_id, row, col in rows:
            bookings.setdefault(booking_id, []).append((row, col))
        return bookings

    def booking_exists(self, seating_plan_title: str, booking_id: str) -> bool:
        """
        Check if a booking exists for the given seating plan title and booking_id.
        """
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT 1 FROM bookings
                WHERE seating_plan_title = ? AND booking_id = ?
                LIMIT 1
                """,
                (seating_plan_title, booking_id)
            )
            return c.fetchone() is not None

    def clear_all(self) -> None:
        """
        Utility method for tests: clear all bookings.
        """
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM bookings")
            conn.commit()
```

Perform a code review to refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file using unittest.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.
