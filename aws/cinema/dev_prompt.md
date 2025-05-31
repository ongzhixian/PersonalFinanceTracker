# Prompts

Purpose 

1. Making changes
2. Code Review
3. Explain
4. Grading

## Making changes

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


## Code Review

```text
Perform a code review to refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file using unittest.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.


his is now an enterprise-grade, scalable, and future-proof configuration management system using pure Python
```

## Grading

```txt
Review code.

Give description of what code does.
Description of code must be clear and concise such that other can read the description without referring to actual code.
Grade the code in terms of readability and maintainability.
Indicate if code code follows all SOLID principles if applicable.
```

## Documentation

```txt
Generate class diagram using PlantUML.
Diagram should have title and caption.
```











----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- 
# Reference

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