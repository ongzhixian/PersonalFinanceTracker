from console_ui import ConsoleUi
from seating_planner import SeatingPlanner

console_ui = ConsoleUi()

def main():
    """
    Main function to run the seating planner application.
   Orchestrates interactions between ConsoleUi and SeatingPlanner.
    """
    #(title, number_of_rows, seats_per_row) = console_ui.application_start_prompt()
    title = 'MI8'
    number_of_rows = 3
    seats_per_row = 6
    seating_planner = SeatingPlanner(title, number_of_rows, seats_per_row)
    while True:
        seating_plan = seating_planner.get_seating_plan()
        #console_ui.display_seating_map(seating_plan)
        user_selection = console_ui.menu_prompt(seating_plan)

        if user_selection == 1:
            number_of_seats_to_book = console_ui.number_of_seats_to_book_prompt(seating_plan)
            start_seat = None
            while True:
                booking_id = seating_planner.book_seats(number_of_seats_to_book, start_seat=start_seat)
                seating_plan = seating_planner.get_seating_plan(booking_id)
                console_ui.display_seating_map(seating_plan)
                response = console_ui.confirm_proposed_seating_map_prompt()
                if response == '':
                    print('booking_id', booking_id)
                    break
                start_seat = response
                seating_planner.unbook_seats(booking_id)

                # Original
                # (booking_id, proposed_seating_map) = seating_planner.get_proposed_seating_plan(number_of_seats_to_book,start_seat=None)
                # console_ui.display_seating_map(proposed_seating_map)
                # response = console_ui.confirm_proposed_seating_map_prompt()
                # if response == 'confirm':
                #     seating_planner.confirm_proposed_seating_map(booking_id, proposed_seating_map)
                #     break
                # if response == '':
                #     break
        if user_selection == 2:
            booking_id = console_ui.booking_id_prompt()
            if len(booking_id.strip()) > 0:
                seating_plan = seating_planner.get_seating_plan(booking_id)
                console_ui.display_seating_map(seating_plan)
        if user_selection == 3:
            exit(0)

if __name__ == '__main__':
    main()
