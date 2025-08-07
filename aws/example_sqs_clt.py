import signal
import sys
import threading
import time
from datetime import datetime
import os

terminate_event = threading.Event()

def signal_handler(signum, frame):
    """Handle SIGINT (CTRL-C) gracefully"""
    print(f"\n[{datetime.now()}] Received signal {signum}. Shutting down gracefully...")
    terminate_event.set()
    print("Exiting application...")


def worker_thread():
    print("Worker: Starting file system monitoring...")
    
    # Directory to watch (current directory by default, change as needed)
    watch_directory = os.path.join(os.path.dirname(__file__), "watched_files")
    
    # Create the watch directory if it doesn't exist
    if not os.path.exists(watch_directory):
        os.makedirs(watch_directory)
        print(f"Created watch directory: {watch_directory}")
    
    print(f"Watching directory: {watch_directory}")
    
    # Store file states for comparison
    file_states = {}
    
    def scan_directory():
        current_files = {}
        try:
            for root, dirs, files in os.walk(watch_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        current_files[file_path] = {
                            'mtime': stat.st_mtime,
                            'size': stat.st_size
                        }
                    except OSError:
                        continue
        except OSError:
            pass
        return current_files
    
    # Initial scan
    file_states = scan_directory()
    
    counter = 0
    while not terminate_event.is_set():
        counter += 1
        print(f"[{datetime.now()}] Worker monitoring iteration {counter}")
        
        # Scan for changes
        current_files = scan_directory()
        
        # Check for new or modified files
        for file_path, file_info in current_files.items():
            if file_path not in file_states:
                print(f"[{datetime.now()}] File created: {file_path}")
            elif (file_states[file_path]['mtime'] != file_info['mtime'] or 
                  file_states[file_path]['size'] != file_info['size']):
                print(f"[{datetime.now()}] File modified: {file_path}")
        
        # Check for deleted files
        for file_path in file_states:
            if file_path not in current_files:
                print(f"[{datetime.now()}] File deleted: {file_path}")
        
        # Update file states
        file_states = current_files
        
        time.sleep(2)  # Poll every 2 seconds

def main_thread():
    print("Main: Initializing resources...")
    counter = 100
    while not terminate_event.is_set():
        print(f"[{datetime.now()}] Main task iteration {counter}")
        time.sleep(5)
        counter = counter+1
    # time.sleep(2)  # Simulate resource initialization
    # print("Main: Resources initialized. Setting the event.")
    # event.set()  # Signal the worker thread


if __name__ == "__main__":
    print("Application started. Press CTRL-C to exit.\n")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    worker = threading.Thread(target=worker_thread)
    main = threading.Thread(target=main_thread)

    worker.start()
    main.start()

    while not terminate_event.is_set():
        time.sleep(0.1)

    print("Waiting for threads to complete...")
    worker.join(timeout=30)
    main.join(timeout=30)
