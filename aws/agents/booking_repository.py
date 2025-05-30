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

