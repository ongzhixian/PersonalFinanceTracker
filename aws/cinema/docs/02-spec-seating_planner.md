# Seating Planner Design Specification

## Overview
The **SeatingPlanner** class provides a structured approach to managing seating plans, handling bookings, and ensuring proper allocation of seats. It supports booking, canceling reservations, and retrieving a formatted seating arrangement.

## Class & Method Summaries

### `SeatingPlanner`
Manages seating allocation, booking, and cancellation processes while interacting with a repository for persistent storage.

#### `__init__(...)`
Initializes the seating planner with title, seating configuration, optional database and configurations.

#### `get_seating_plan(booking_id: Optional[str] = None) -> Optional[SeatingPlan]`
Returns the current seating plan; marks booked seats as "proposed" if associated with a booking ID.

#### `book_seats(number_of_seats: int, start_seat: Optional[str] = None) -> str`
Books a specified number of seats, prioritizing available seats near the center or next to a chosen starting seat.

#### `cancel_booking(booking_id: str) -> str`
Cancels a booking, freeing up seats and updating persistent storage.

#### `_initialize_seating_plan() -> List[List[Seat]]`
Creates a fresh seating plan where all seats start as "available."

#### `_apply_bookings_to_plan() -> None`
Updates the seating plan based on existing confirmed bookings.

#### `_seat_label_to_indices(seat_label: str) -> Tuple[int, int]`
Converts a seat label (e.g., "A1") to corresponding row and column indices.

## Features
- **Persistent Storage:** Maintains booking records using a repository.
- **Center-Priority Allocation:** Books seats closer to the middle when multiple selections are required.
- **Reversible Row Indexing:** Maps labels to internal indices while reversing row order.
