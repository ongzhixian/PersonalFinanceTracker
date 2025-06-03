# Seating Planner Application Design Specification

## Overview
The Seating Planner Application is a Python-based console application that manages seat bookings for a movie or event. It interacts with users via a console-based UI, allowing them to book seats, view their bookings, and exit the application.

## Design Summary
The application consists of several components:
- **SeatingApp**: The core application logic and user interaction handler.
- **ConsoleUi**: The user interface component for displaying menus and collecting inputs.
- **SeatingPlanner**: Manages seat allocation, booking, and retrieval.
- **AppConfiguration**: Loads application-specific configurations.
- **MenuOption Enum**: Represents available user actions.

## Class Descriptions

### `MenuOption`
An enumeration that defines three menu options: seat booking, booking viewing, and exiting the application.

### `SeatingApp`
Manages the interaction between the console UI and the seating planner, handling user input and business logic.

#### Methods:
- **`__init__(config_path: str)`** – Initializes the app with configuration and UI components.
- **`start()`** – Begins the application and sets up user interactions.
- **`_run_event_loop()`** – Runs the main loop to continuously handle user inputs.
- **`_process_user_selection()`** – Manages user selection between booking seats, viewing bookings, or exiting.
- **`_handle_booking()`** – Handles seat booking, including confirmation and cancellations.
- **`_handle_view_booking()`** – Allows users to view seating plans based on booking ID.
- **`_exit_application()`** – Exits the application cleanly.

## Flow of Execution
1. The application initializes using configurations.
2. It prompts the user for seating plan details and starts the planner.
3. The user interacts with the menu to book seats, view bookings, or exit.
4. Seat bookings involve selection, confirmation, and the possibility of rebooking.
5. The application remains active until the user decides to exit.

