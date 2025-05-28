Write Python code that will make the following code run.
_prompt() methods are prompt user to input values in console.

Code should have typing and follow SOLID principles.

Write unit tests for all code and main() function in a separate file.

```
from console_ui import ConsoleUi
from seating_planner import SeatingPlanner

console_ui = ConsoleUi()

def main():
    (title, number_of_rows, seats_per_row) = console_ui.application_start_prompt()
    seating_planner = SeatingPlanner(title, number_of_rows, seats_per_row)
    while True:
        seating_plan = seating_planner.get_seating_plan()
        user_selection = console_ui.menu_prompt(seating_plan)
        if user_selection == 1:
            number_of_seats_to_book = console_ui.number_of_seats_to_book_prompt(seating_plan)
            while True:
                (booking_id, proposed_seating_map) = seating_planner.get_proposed_seating_plan(number_of_seats_to_book,start_seat=None)
                console_ui.display_seating_map(proposed_seating_map)
                response = console_ui.confirm_proposed_seating_map_prompt()
                if response == 'confirm':
                    seating_planner.confirm_proposed_seating_map(booking_id, proposed_seating_map)
                    break
                if response == '':
                    break
        if user_selection == 2:
            confirmed_booking_map = seating_planner.get_seating_plan()
            console_ui.display_seating_map(confirmed_booking_map)
        if user_selection == 3:
            exit(0)

if __name__ == '__main__':
    main()
```