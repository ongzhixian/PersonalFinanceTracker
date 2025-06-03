# Test Specification: `test_booking_repository.py`

## Summary

This module unit tests for the `BookingRepository` class, ensuring that booking-related operations behave correctly. It uses an in-memory SQLite database for testing purposes, validating booking creation, deletion, retrieval, and edge cases like duplicate bookings or empty seat lists.

## Classes and Methods Overview

### **TestBookingRepository (unittest.TestCase)**
Tests the functionality of `BookingRepository`.

#### **`setUpClass(cls)`**
Initializes an in-memory SQLite database for all test cases.

#### **`tearDownClass(cls)`**
Closes the SQLite database connection after all tests.

#### **`setUp(self)`**
Clears all bookings before each test execution.

#### **`test_save_booking_success(self)`**
Verifies that a valid booking can be saved and retrieved correctly.

#### **`test_save_booking_empty_seats(self)`**
Ensures that attempting to save a booking with an empty seat list raises a `ValueError`.

#### **`test_save_duplicate_booking(self)`**
Checks that saving a duplicate booking raises a `BookingRepositoryError`.

#### **`test_delete_booking_success(self)`**
Confirms that deleting an existing booking works as expected.

#### **`test_delete_nonexistent_booking(self)`**
Validates that deleting a nonexistent booking raises a `BookingRepositoryError`.

#### **`test_load_all_bookings(self)`**
Tests loading multiple bookings to ensure correct retrieval.

#### **`test_booking_exists(self)`**
Checks whether a booking exists in the system.

#### **`test_clear_all_bookings(self)`**
Verifies that all bookings are cleared successfully.

---

This test suite ensures robust verification of the `BookingRepository` class, handling expected edge cases and maintaining data integrity.
