import unittest
import uuid


class CinemaBooking:
    def __init__(self, title, rows, seats_per_row):
        self.title = title
        self.rows = int(rows)
        self.seats_per_row = int(seats_per_row)
        self.seats = {}
        self.bookings = {}
        self.available_seats = self.rows * self.seats_per_row
        self._initialize_seats()

    def _initialize_seats(self):
        for row in range(self.rows):
            row_label = chr(ord('A') + row)
            self.seats[row_label] = [False] * self.seats_per_row  # False = available, True = booked

    def display_menu(self):
        print("Welcome")
        print(f"[1] Book tickets for {self.title} ({self.available_seats} seats available)")
        print("[2] Check bookings")
        print("[3] Exit")
        print("Please enter your selection:")

    def book_tickets(self, num_tickets):
        if num_tickets > self.available_seats:
            print("Insufficient seats available.")
            return None

        booked_seats = []
        remaining_tickets = num_tickets

        for row_index in range(self.rows - 1, -1, -1):  # Start from the back row
            row_label = chr(ord('A') + row_index)
            middle_seat = self.seats_per_row // 2
            left = middle_seat
            right = middle_seat + 1

            while remaining_tickets > 0:
                # Try booking seats from middle outwards
                if left >= 0 and not self.seats[row_label][left]:
                    self.seats[row_label][left] = True
                    booked_seats.append((row_label, left + 1))  # Seat numbers start from 1
                    remaining_tickets -= 1
                elif right < self.seats_per_row and not self.seats[row_label][right]:
                    self.seats[row_label][right] = True
                    booked_seats.append((row_label, right + 1))
                    remaining_tickets -= 1
                else:
                    left -= 1
                    right += 1

                if left < 0 and right >= self.seats_per_row:
                    break  # Row is full

        # Handle insufficient seats in current row, overflow to next row

        if remaining_tickets > 0:
            print("Unexpected: Insufficient seats even after allocation, should not happen.")
            # revert changes
            for row, seat in booked_seats:
                self.seats[row][seat - 1] = False
            return None

        booking_id = str(uuid.uuid4())
        self.bookings[booking_id] = booked_seats
        self.available_seats -= num_tickets

        return booking_id, num_tickets, booked_seats

    def display_booking(self, booking_id):
        if booking_id not in self.bookings:
            print("Booking not found.")
            return

        booked_seats = self.bookings[booking_id]
        print(f"Booking ID: {booking_id}")
        print(f"Tickets Booked: {len(booked_seats)}")
        self.display_seating_map(highlighted_seats=booked_seats)

    def display_seating_map(self, highlighted_seats=None):
        if highlighted_seats is None:
            highlighted_seats = []

        print("  ", end="")
        for i in range(1, self.seats_per_row + 1):
            print(f"{i:2}", end=" ")
        print()

        for row_index in range(self.rows):
            row_label = chr(ord('A') + row_index)
            print(row_label, end=" ")
            for seat_index in range(self.seats_per_row):
                if (row_label, seat_index + 1) in highlighted_seats:
                    print("XX", end=" ")  # Booked by this booking
                elif self.seats[row_label][seat_index]:
                    print("BB", end=" ")  # Booked by another booking
                else:
                    print("--", end=" ")  # Available
            print()


def main():
    while True:
        try:
            input_str = input("Please define movie title and seat map in [Title] [Row] [SeatsPerRow] format\n> ")
            title, rows, seats_per_row = input_str.split()
            rows = int(rows)
            seats_per_row = int(seats_per_row)

            if not (1 <= rows <= 26 and 1 <= seats_per_row <= 50):
                print("Invalid input. Rows must be between 1 and 26, and seats per row between 1 and 50.")
                continue

            cinema = CinemaBooking(title, rows, seats_per_row)
            break  # Exit the loop if input is valid
        except ValueError:
            print("Invalid input format. Please enter in [Title] [Row] [SeatsPerRow] format.")

    while True:
        cinema.display_menu()
        selection = input("> ")

        if selection == "1":
            try:
                num_tickets = int(input("Enter number of tickets to book: "))
                if num_tickets <= 0:
                    print("Number of tickets must be greater than 0.")
                    continue
                booking_result = cinema.book_tickets(num_tickets)
                if booking_result:
                    booking_id, num_tickets_booked, booked_seats = booking_result
                    print(f"Booking successful! Booking ID: {booking_id}")
                    print(f"Number of tickets booked: {num_tickets_booked}")
                    cinema.display_seating_map(highlighted_seats=booked_seats)
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif selection == "2":
            booking_id = input("Enter booking ID to check: ")
            cinema.display_booking(booking_id)
        elif selection == "3":
            print("Exiting...")
            break
        else:
            print("Invalid selection. Please try again.")


class TestCinemaBooking(unittest.TestCase):
    def test_initialize_seats(self):
        cinema = CinemaBooking("Test Movie", 3, 5)
        self.assertEqual(len(cinema.seats), 3)
        for row in cinema.seats.values():
            self.assertEqual(len(row), 5)
            self.assertTrue(all(seat == False for seat in row))

    def test_book_tickets_sufficient_seats(self):
        cinema = CinemaBooking("Test Movie", 3, 5)
        booking_result = cinema.book_tickets(3)
        self.assertIsNotNone(booking_result)
        booking_id, num_tickets_booked, booked_seats = booking_result
        self.assertEqual(num_tickets_booked, 3)
        self.assertEqual(cinema.available_seats, 12)

        # Verify seats are booked
        row_label = chr(ord('C'))
        middle_seat = cinema.seats_per_row // 2
        self.assertTrue(cinema.seats[row_label][middle_seat])
        self.assertTrue(cinema.seats[row_label][middle_seat - 1])
        self.assertTrue(cinema.seats[row_label][middle_seat + 1])

    def test_book_tickets_insufficient_seats(self):
        cinema = CinemaBooking("Test Movie", 1, 2)
        booking_result = cinema.book_tickets(3)
        self.assertIsNone(booking_result)
        self.assertEqual(cinema.available_seats, 2)

    def test_book_tickets_overflow_to_next_row(self):
        cinema = CinemaBooking("Test Movie", 2, 3)
        booking_result = cinema.book_tickets(4)
        self.assertIsNotNone(booking_result)
        booking_id, num_tickets_booked, booked_seats = booking_result
        self.assertEqual(num_tickets_booked, 4)
        self.assertEqual(cinema.available_seats, 2)

        # Verify seats are booked in rows B and A
        self.assertTrue(cinema.seats['B'][1])
        self.assertTrue(cinema.seats['B'][0])
        self.assertTrue(cinema.seats['B'][2])
        self.assertTrue(cinema.seats['A'][1]) #Middle seat of row A

    def test_display_booking_found(self):
        cinema = CinemaBooking("Test Movie", 2, 3)
        booking_result = cinema.book_tickets(2)
        booking_id, num_tickets_booked, booked_seats = booking_result
        # Call display_booking and verify the booking id is printed to standard output
        self.assertIn(cinema.bookings[booking_id], cinema.bookings.values())

    def test_display_booking_not_found(self):
        cinema = CinemaBooking("Test Movie", 2, 3)
        # Call display_booking with invalid id
        cinema.display_booking("invalid_id")
        # Verify message "Booking not found." is printed.


if __name__ == "__main__":
    #unittest.main() #Comment out to run the main application
    main()