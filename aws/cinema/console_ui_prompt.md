Given the following Python code:

```shared_data_models.py
# console_ui.py
from typing import List, Tuple, Dict, Any
from shared_data_models import SeatingPlan # Import SeatingPlan

class ConsoleUi:
    """
    Handles all interactions with the console, including
    displaying information and getting user input.
    Adheres to the Single Responsibility Principle.
    """

    def application_start_prompt(self) -> Tuple[str, int, int]:
        """
        Prompts the user for initial application details in a specific format:
        [Title] [Row] [SeatsPerRow].
        Validates the input for maximum rows (26) and seats per row (50).
        Rows are labeled from A to Z with Z nearest to the screen.
        """
        print("\n--- Seating Planner Setup ---")
        while True:
            user_input: str = input(
                "\nPlease define movie title and seating map in [Title] [Row] [SeatsPerRow] format:\n> ").strip()
            parts: List[str] = user_input.split()

            if len(parts) < 3:
                print("Invalid format. Please ensure you provide a title, number of rows, and seats per row.")
                continue

            title_parts: List[str] = parts[:-2]
            title: str = " ".join(title_parts)

            try:
                number_of_rows_str: str = parts[-2]
                seats_per_row_str: str = parts[-1]

                number_of_rows: int = int(number_of_rows_str)
                seats_per_row: int = int(seats_per_row_str)

                if not title:
                    print("Invalid input. Title cannot be empty.")
                    continue
                if number_of_rows <= 0 or number_of_rows > 26:
                    print("Invalid input. Number of rows must be a positive integer and not exceed 26 (A-Z).")
                    continue
                if seats_per_row <= 0 or seats_per_row > 50:
                    print("Invalid input. Number of seats per row must be a positive integer and not exceed 50.")
                    continue

                return title, number_of_rows, seats_per_row
            except ValueError:
                print("Invalid input. Please ensure rows and seats per row are positive integers.")
            except IndexError:
                print("Invalid format. Please ensure you provide a title, number of rows, and seats per row.")

    def menu_prompt(self, movie_title: str, available_seats: int, seating_plan: List[List[str]]) -> int:
        """
        Displays the main menu and prompts the user for their selection.
        Includes movie title and available seats in the booking option.
        """
        print("\nWelcome")
        print(f"1. Book tickets for {movie_title} ({available_seats} seats available)")
        print("2. Check bookings")
        print("3. Exit")
        while True:
            try:
                choice: int = int(input("Please enter your selection:\n> ").strip())
                if choice in [1, 2, 3]:
                    return choice
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def number_of_seats_to_book_prompt(self, seating_plan: SeatingPlan) -> int:
        """
        Prompts the user for the number of seats they wish to book.
        """
        self.display_seating_map(seating_plan)
        while True:
            try:
                num_seats: int = int(input("Enter the number of seats to book: "))
                if num_seats <= 0:
                    raise ValueError
                return num_seats
            except ValueError:
                print("Invalid input. Please enter a positive integer for the number of seats.")

    def display_seating_map(self, seating_plan: SeatingPlan) -> None:
        """
        Displays the current seating map in the specified format.
        '.' for available, '#' for booked.
        """
        seating_map = seating_plan.plan
        if not seating_map or not seating_map[0]:
            print("\nSeating plan is empty.")
            return

        num_rows: int = len(seating_map)
        num_cols: int = len(seating_map[0])

        # Calculate footer width for centering "S C R E E N"
        # Each column takes 3 characters (e.g., '1  ', '10 ')
        # Add 3 for the row label part (e.g., 'A  ')
        footer_parts: List[str] = []
        for i in range(num_cols):
            footer_parts.append(str(i + 1).ljust(3))
        footer_str: str = "   " + "".join(footer_parts)  # 3 spaces for row label offset
        footer_width: int = len(footer_str)

        screen_header: str = "S C R E E N"
        screen_padding: int = (footer_width - len(screen_header)) // 2

        print("\n" + " " * screen_padding + screen_header)
        print("-" * footer_width)

        # Rows are labeled A to Z, with A nearest to the screen and Z furthest (as per the example)
        # The prompt says Z nearest to the screen, but the example shows A nearest to the screen.
        # Following the example (A nearest to the screen, Z nearest to the screen)
        for i in range(num_rows - 1, -1, -1):  # Iterate from last row (Z) to first row (A)
            row_label: str = chr(65 + i)  # A=0, B=1, ...
            row_display: str = f"{row_label} "
            for seat in seating_map[i]:
                if seat == 'O':
                    row_display += ".  "  # Available seat
                elif seat == 'X':
                    row_display += "#  "  # Booked seat
                elif seat == 'P':
                    row_display += "P  " # Proposed seat
                else:
                    row_display += f"{seat}  "  # For any other custom marker if implemented
            print(row_display)

        # Print column numbers (footer)
        print("  " + " ".join([str(i + 1).ljust(2) for i in range(num_cols)]))

        # Adjust footer to match the example's column spacing (each column 3 characters)
        footer_numbers = []
        for i in range(num_cols):
            footer_numbers.append(str(i + 1).ljust(3))  # Each number left-justified in 3 spaces


    def confirm_proposed_seating_map_prompt(self) -> str:
        """
        Asks the user to confirm or reject the proposed seating map.
        Returns 'confirm' or an empty string.
        """
        response: str = input(
            "Confirm booking? (type 'confirm' to accept, or press Enter to decline and try again): ").strip().lower()
        return response

    def display_message(self, message: str) -> None:
        """
        Displays a generic message to the user.
        """
        print(f"\n{message}")
```

Modify the menu_prompt function to :

menu_prompt(self, seating_plan: SeatingPlan) -> int:

Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
