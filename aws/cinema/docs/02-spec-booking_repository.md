# Booking Repository Design Specification

## Summary
This Python module provides an SQLite-based persistence layer for managing seat bookings in a seating plan. It defines an interface `IBookingRepository`, a concrete implementation `BookingRepository`, and a custom exception `BookingRepositoryError`.

## Classes and Methods Overview

### `BookingRepositoryError`
- **Custom exception for BookingRepository errors.** Raised when constraints are violated.

### `IBookingRepository`
- **Protocol defining the repository interface.** Ensures consistency across implementations.

#### `save_booking(seating_plan_title: str, booking_id: str, seats: Sequence[Tuple[int, int]]) -> None`
- **Saves a booking with specified seats.** Raises an error if the booking already exists.

#### `delete_booking(seating_plan_title: str, booking_id: str) -> None`
- **Deletes a booking by its ID.** Raises an error if no such booking exists.

#### `load_all_bookings(seating_plan_title: str) -> Dict[str, List[Tuple[int, int]]]`
- **Retrieves all bookings for a given seating plan.** Returns a dictionary mapping booking IDs to seat positions.

#### `booking_exists(seating_plan_title: str, booking_id: str) -> bool`
- **Checks if a booking exists.** Returns `True` if found, `False` otherwise.

#### `clear_all_bookings() -> None`
- **Deletes all bookings from the database.** Primarily useful for testing.

### `BookingRepository`
- **Concrete implementation handling SQLite persistence.** Stores, retrieves, and manages bookings.

#### `__init__(db_path: str = ":memory:")`
- **Initializes the repository with an SQLite connection.** Defaults to in-memory storage.

#### `_init_db() -> None`
- **Creates the bookings table if it does not exist.** Ensures data persistence.

#### `save_booking(seating_plan_title: str, booking_id: str, seats: Sequence[Tuple[int, int]]) -> None`
- **Inserts a booking into the database.** Enforces constraints.

#### `delete_booking(seating_plan_title: str, booking_id: str) -> None`
- **Removes a booking.** Ensures integrity by checking if the booking exists.

#### `load_all_bookings(seating_plan_title: str) -> Dict[str, List[Tuple[int, int]]]`
- **Retrieves bookings from the database.** Structures results as a dictionary.

#### `booking_exists(seating_plan_title: str, booking_id: str) -> bool`
- **Verifies booking existence.** Uses efficient querying.

#### `clear_all_bookings() -> None`
- **Wipes all stored bookings.** Helps reset data for testing.

## Database Design
- **Table Name:** `bookings`
- **Columns:** 
  - `seating_plan_title` (TEXT, NOT NULL)
  - `booking_id` (TEXT, NOT NULL)
  - `row` (INTEGER, NOT NULL)
  - `col` (INTEGER, NOT NULL)
- **Primary Key:** `(seating_plan_title, booking_id, row, col)`
- **Constraints:** Prevent duplicate entries.

## Usage Scenarios
- Storing and retrieving bookings efficiently.
- Enforcing constraints to avoid duplicate bookings.
- Supporting testing with in-memory storage.

