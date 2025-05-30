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



## Useful prompts?

```text 
Perform a code review to refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.

```

```text
Perform a code review to refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.

```


```text

Update get function as follows:

1. Retrieve nested configurations using colon-separated string.
For example: 
get("booking_settings:booking_id_prefix")
will return "BK"

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs if any.

```


```text

Update confirm_seating_map_prompt function as follows:

1. Take a SeatingMap argument.
2. Validate user input as follows:
   1. 


Update ConsoleUi class as follows:

1. Store a reference to AppConfiguration.
2. Welcome message in menu_prompt function should display value "application:name" setting retrieved from AppConfiguration.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.



Perform a code review to refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.

Update number_of_seats_to_book_prompt function as follows:

Prompts the user for the number of seats they wish to book.

Input validation rules:

1. If the number of seats is greater than the number of available seats for booking, 
pinpoint error and prompt user again.
2. User can input empty string to end prompt.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs if any.

```

```text
The current code uses the following for seat status.

'O' for available, 'X' for booked, 'P' for proposed.

Update code as follows:

1. Change statuses to reflect:
'O' for available
'B' for booked
'P' for booked by specified booking id.

2. Statuses are configurable from by reading configuration file.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs if any.

1. Filename for sqlite database should be configured from a JSON configuration file.
2. Booking id should be in the format of <PREFIX><RUNNING_NUMBER> with prefix defined from JSON configuration file.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs if any.

1. Persist bookings to sqlite3 database.

Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.

1. Booking id should be in the format of <PREFIX><RUNNING_NUMBER>
2. <PREFIX> is defined a separate JSON file.


Perform a code review to refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
Prioritize readability and maintainability.
Identify illogical constructs if any.
```