import uuid
import string
from typing import List, Tuple, Dict, Optional
from shared_data_models import Seat, ProposedBooking, SeatingPlan

class SeatingPlanner:
    """
    Manages the seating plan logic, including booking,
    proposing seats, and confirming bookings.
    Adheres to the Single Responsibility Principle.
    """

    def __init__(self, title: str, num_rows: int, seats_per_row: int):
        if not isinstance(title, str) or not title:
            raise ValueError("Title must be a non-empty string.")
        if not isinstance(num_rows, int) or num_rows <= 0:
            raise ValueError("Number of rows must be a positive integer.")
        if not isinstance(seats_per_row, int) or seats_per_row <= 0:
            raise ValueError("Seats per row must be a positive integer.")

        self.title: str = title
        self.num_rows: int = num_rows
        self.seats_per_row: int = seats_per_row
        self._seating_plan: List[List[Seat]] = [
            [Seat(r, c, 'O') for c in range(self.seats_per_row)] for r in range(self.num_rows)
        ]
        self._confirmed_bookings: Dict[str, List[Tuple[int, int]]] = {}  # booking_id -> list of (row, col)

    def get_seating_plan(self, booking_id: Optional[str] = None) -> SeatingPlan:
        """
        Returns the current state of the seating plan as a SeatingPlan dataclass.
        If booking_id is provided, seats for that booking are marked as 'P'.
        """
        current_plan_status = [[seat.status for seat in row] for row in self._seating_plan]
        available_count = sum(row.count('O') for row in current_plan_status)

        if booking_id:
            if booking_id not in self._confirmed_bookings:
                raise ValueError(f"Booking ID '{booking_id}' not found in confirmed bookings.")
            plan_with_proposed = [row[:] for row in current_plan_status]
            for r, c in self._confirmed_bookings[booking_id]:
                # Only mark as 'P' if not already booked (should not happen, but for safety)
                if plan_with_proposed[r][c] == 'X':
                    plan_with_proposed[r][c] = 'P'
            return SeatingPlan(title=self.title, plan=plan_with_proposed, available_seats_count=available_count)

        return SeatingPlan(title=self.title, plan=current_plan_status, available_seats_count=available_count)

    def _seat_label_to_indices(self, seat_label: str) -> Tuple[int, int]:
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

    def _find_centermost_available_seats(self, row: int, num_seats: int) -> List[Tuple[int, int]]:
        available = [c for c, seat in enumerate(self._seating_plan[row]) if seat.status == 'O']
        if len(available) < num_seats:
            return []
        center = self.seats_per_row // 2
        best_block = None
        min_dist = None
        for i in range(len(available) - num_seats + 1):
            block = available[i:i+num_seats]
            block_center = sum(block) / num_seats
            dist = abs(block_center - center)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                best_block = block
        if best_block is not None:
            return [(row, c) for c in best_block]
        return []

    def book_seats(self, number_of_seats: int, start_seat: Optional[str] = None) -> str:
        """
        Book seats on seating plan.

        Args:
            number_of_seats (int): number of seats to book on seating plan
            start_seat (str|None): If start_seat is not given, book centermost available seats in each row
                                   starting from the furthest from the screen. If given, start booking from
                                   start_seat, moving right in the same row, then continue as above if needed.

        Returns:
            booking_id (str): Booking id for the group of seats booked.
        """
        if number_of_seats <= 0:
            raise ValueError("Number of seats must be a positive integer.")

        seats_to_book: List[Tuple[int, int]] = []
        rows_order = list(range(self.num_rows - 1, -1, -1))  # Furthest from screen first

        if start_seat:
            row, col = self._seat_label_to_indices(start_seat)
            # Book as many as possible to the right in this row
            for c in range(col, self.seats_per_row):
                if self._seating_plan[row][c].status == 'O':
                    seats_to_book.append((row, c))
                    if len(seats_to_book) == number_of_seats:
                        break
                else:
                    break  # Stop at first unavailable seat
            # Remove this row from further consideration if not enough seats booked
            if row in rows_order:
                rows_order.remove(row)

        # If more seats needed, continue in other rows, centermost available seats
        seats_needed = number_of_seats - len(seats_to_book)
        for r in rows_order:
            if seats_needed <= 0:
                break
            centermost = self._find_centermost_available_seats(r, seats_needed)
            if centermost:
                seats_to_book.extend(centermost)
                seats_needed = number_of_seats - len(seats_to_book)

        if len(seats_to_book) < number_of_seats:
            raise ValueError("Not enough seats available to fulfill the booking.")

        # Book the seats
        for r, c in seats_to_book:
            self._seating_plan[r][c].status = 'X'

        booking_id = str(uuid.uuid4())
        self._confirmed_bookings[booking_id] = seats_to_book

        return booking_id

    def unbook_seats(self, booking_id: str) -> str:
        """
        Make seats for the given booking_id available again.

        Args:
            booking_id (str): Booking ID of seats to make available.

        Returns:
            str: The booking_id if successful.

        Raises:
            ValueError: If booking_id is not found.
        """
        if booking_id not in self._confirmed_bookings:
            raise ValueError(f"Booking ID '{booking_id}' not found.")

        seats_to_unbook = self._confirmed_bookings[booking_id]
        for row, col in seats_to_unbook:
            if 0 <= row < self.num_rows and 0 <= col < self.seats_per_row:
                if self._seating_plan[row][col].status == 'X':
                    self._seating_plan[row][col].status = 'O'
                # If seat is not 'X', we silently skip (could log if needed)
        del self._confirmed_bookings[booking_id]
        return booking_id
