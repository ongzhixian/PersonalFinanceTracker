# Overview

Design document for this application.

## Data design

We represent the graphical using a list of lists as follows:
[['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'B', 'O', 'O', 'O'], ['B', 'B', 'B', 'B', 'B', 'B']]
First list represents the row nearest to screen.



# How to run

1. Console
2. Web



# Files / Modules

1. app_configuration.py
2. shared_data_models.py
3. booking_repository.py
4. main.py
5. seating_planner.py


---- 

1. console_ui.py (console_ui_test.py : unit tests for console_ui.py)

Module that hold classes and functions for console interactions.

2. main.py (main_test.py : unit tests for main.py)

Application script that orchestrate console UI interactions with user and business logic.
 
3. seating_planner.py (seating_planner_test.py : unit tests for seating_planner.py)

Controls logic for allocating seats.

4. shared_data_models.py

Shared data models used to represent seating plan data.
Referenced by console_ui.py and seating_planner.py. 


# Selection

Use the following rules for default seat selection:

1. Start from the furthest row from screen.
2. Start from the middle-most possible seat.
3. When a row is not enough to accommodate the number of tickets, it should overflow to the next row closer to screen.

User can choose seating position by specifying the starting position of the seats.
Seating assignment should follow this rule:
1. Starting from specified position, fill up all the empty seats in the same row all the way to the right of the cinema hall.
2. When there is not enough seats available, it should overflow to the next row closer to the screen.
3. Seat allocation for overflow follows the rules for default seat allocation.


