"""Trade bot
"""
import threading
import time
import sys
import signal # Import the signal module

# Global flag to control the execution of threads
running = True

def signal_handler(sig, frame):
    """
    Signal handler function for SIGINT (Ctrl+C).
    Sets the global 'running' flag to False to signal threads to stop.
    """
    global running
    print("\nCtrl+C (SIGINT) detected! Shutting down gracefully...")
    running = False

def worker_function(thread_id):
    """
    This function simulates a task being performed by a thread.
    It will continue to run as long as the 'running' flag is True.
    """
    global running
    print(f"Thread {thread_id}: Starting...")
    while running:
        # Simulate some work being done
        print(f"Thread {thread_id}: Working...")
        time.sleep(1) # Pause for 1 second to simulate work
    print(f"Thread {thread_id}: Stopping.")

def main():
    """
    Main function to set up and manage the threads.
    It registers a signal handler for graceful shutdown.
    """
    global running
    print("Multi-threaded Console Application Started.")
    print("Press Ctrl+C to stop the application.")

    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    threads = []
    num_threads = 3 # You can change the number of threads here

    # Create and start the worker threads
    for i in range(num_threads):
        thread = threading.Thread(target=worker_function, args=(i + 1,))
        threads.append(thread)
        thread.start()

    # Keep the main thread alive while worker threads are running.
    # The signal handler will set 'running' to False when Ctrl+C is pressed.
    while running:
        time.sleep(0.5) # Short sleep to avoid busy-waiting

    # Wait for all threads to complete their execution
    for thread in threads:
        thread.join()

    print("All threads have stopped.")
    print("Application terminated.")
    sys.exit(0) # Exit the application


if __name__ == "__main__":
    main()