from typing import List, Tuple, Dict, Any

class ConsoleUi:
    """
    Handles all interactions with the console, including
    displaying information and getting user input.
    Adheres to the Single Responsibility Principle.
    """

    def application_start_prompt(self) -> Tuple[str, int, int]:
        """
        Prompts the user for initial application details:
        title, number of rows, and seats per row.
        """
        print("\n--- Seating Planner Setup ---")
        title: str = input("Enter the title for the seating plan (e.g., 'Movie Theater', 'Concert Hall'): ")
        while True:
            try:
                number_of_rows: int = int(input("Enter the number of rows: "))
                if number_of_rows <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter a positive integer for the number of rows.")
        while True:
            try:
                seats_per_row: int = int(input("Enter the number of seats per row: "))
                if seats_per_row <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter a positive integer for the number of seats per row.")
        return title, number_of_rows, seats_per_row

    def menu_prompt(self, seating_plan: List[List[str]]) -> int:
        """
        Displays the main menu and prompts the user for their selection.
        """
        print("\n--- Main Menu ---")
        self.display_seating_map(seating_plan)
        print("1. Book seats")
        print("2. View current bookings")
        print("3. Exit")
        while True:
            try:
                choice: int = int(input("Enter your choice (1, 2, or 3): "))
                if choice in [1, 2, 3]:
                    return choice
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def number_of_seats_to_book_prompt(self, seating_plan: List[List[str]]) -> int:
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

    def display_seating_map(self, seating_map: List[List[str]]) -> None:
        """
        Displays the current seating map.
        'O' for available, 'X' for booked.
        """
        print("\n--- Seating Map ---")
        if not seating_map:
            print("Seating plan is empty.")
            return

        # Print column headers
        header = "    " + " ".join([str(i + 1) for i in range(len(seating_map[0]))])
        print(header)
        print("   " + "-" * (len(header) - 3))

        for i, row in enumerate(seating_map):
            row_str = f"R{chr(65 + i)} | " + " ".join(row)
            print(row_str)
        print("--------------------")


    def confirm_proposed_seating_map_prompt(self) -> str:
        """
        Asks the user to confirm or reject the proposed seating map.
        Returns 'confirm' or an empty string.
        """
        response: str = input("Confirm booking? (type 'confirm' to accept, or press Enter to decline and try again): ").strip().lower()
        return response

    def display_message(self, message: str) -> None:
        """
        Displays a generic message to the user.
        """
        print(f"\n{message}")