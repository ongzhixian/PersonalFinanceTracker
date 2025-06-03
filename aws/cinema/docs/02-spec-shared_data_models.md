# Seating Plan Data Model

## Summary
This module defines a structured seating plan using data classes to represent seat statuses, individual seats, and seating arrangements. It allows dynamic seat status configurations, seat availability checks, and retrieval of available seats.

## Design Specification

### Classes

#### `SeatStatus`
Defines seat status codes (`AVAILABLE`, `BOOKED`, `PROPOSED`). Statuses are loaded dynamically from a configuration source.

- **`from_config(config: AppConfiguration) -> SeatStatus`**  
  Factory method to initialize seat statuses using external configuration.

#### `Seat`
Represents a single seat with row, column, and status attributes.

- **`is_available(seat_status: SeatStatus) -> bool`**  
  Checks if the seat is available based on a given seat status.

#### `SeatingPlan`
Represents a structured seating arrangement containing multiple seats.

- **`__post_init__()`**  
  Validates data integrity by ensuring non-empty seating plans and consistent row sizes.

- **`get_available_seats(seat_status: SeatStatus) -> List[Seat]`**  
  Retrieves all available seats based on the provided seat status.

## Features
- Supports dynamic configuration of seat statuses.
- Ensures data integrity with validation checks.
- Provides an intuitive way to check and retrieve available seats.

