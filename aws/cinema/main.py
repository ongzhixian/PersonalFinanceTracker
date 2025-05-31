from app_configuration import AppConfiguration
from console_ui import ConsoleUi
from seating_planner import SeatingPlanner

def main():
    """
    Main function to run the seating planner application.
   Orchestrates interactions between ConsoleUi and SeatingPlanner.
    """
    app_configuration = AppConfiguration('./app_configuration.json')
    console_ui = ConsoleUi(app_configuration)

    (title, number_of_rows, seats_per_row) = console_ui.prompt_for_application_start_details()
    seating_planner = SeatingPlanner(title, number_of_rows, seats_per_row)
    while True:
        seating_plan = seating_planner.get_seating_plan()
        #console_ui.display_seating_map(seating_plan)
        user_selection = console_ui.display_menu(seating_plan)

        if user_selection == 1:
            print(seating_plan)
            number_of_seats_to_book = console_ui.prompt_for_number_of_seats_to_book(seating_plan)
            if number_of_seats_to_book is None:
                continue
            start_seat = None
            while True:
                booking_id = seating_planner.book_seats(number_of_seats_to_book, start_seat=start_seat)
                seating_plan = seating_planner.get_seating_plan(booking_id)

                console_ui.display_seating_map(seating_plan)
                response = console_ui.propmpt_for_booking_confirmation()
                if response == '':
                    print('booking_id', booking_id)
                    break
                start_seat = response
                seating_planner.cancel_booking(booking_id)
        if user_selection == 2:
            while True:
                booking_id = console_ui.prompt_for_booking_id()
                if len(booking_id.strip()) > 0:
                    seating_plan = seating_planner.get_seating_plan(booking_id)
                    if seating_plan is None:
                        print("booking_id cannot be found.")
                        continue
                    console_ui.display_seating_map(seating_plan)
                    break
                else:
                    break
        if user_selection == 3:
            exit(0)

if __name__ == '__main__':
    main()
