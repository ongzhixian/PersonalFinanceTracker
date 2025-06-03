# Test Specification: `test_shared_data_models.py`

## **Overview**
This module contains unit tests for validating the functionality of shared seating data models. It ensures that the `SeatStatus`, `Seat`, and `SeatingPlan` classes behave as expected, particularly in terms of seat availability and seating plan consistency.

## **Classes and Methods**

### **TestSeatStatus**
Tests the `SeatStatus` class, which defines possible seat states (e.g., available, booked, proposed).
- `test_factory_method_from_config()`: Verifies that seat statuses are correctly loaded from configuration.
- `test_factory_method_with_defaults()`: Ensures default seat statuses are used when no configuration is provided.

### **TestSeat**
Tests the `Seat` class, which represents individual seats with attributes for position and status.
- `setUp()`: Initializes common test objects for seat status.
- `test_seat_availability()`: Checks whether seats correctly report availability.

### **TestSeatingPlan**
Tests the `SeatingPlan` class, which manages seat arrangements and enforces plan consistency.
- `setUp()`: Initializes common objects, including a valid seating plan.
- `test_seating_plan_validation()`: Ensures seating plans maintain row consistency and prevent empty plans.
- `test_available_seats()`: Validates retrieval of available seats within a seating plan.

## **Execution**
To run the tests, execute:

```sh
python test_shared_data_models.py
