import signal
import sys
import threading
import time
from datetime import datetime

class WorkerApplication:
    def __init__(self):
        self.running = True
        self.worker_thread = None
        
    def signal_handler(self, signum, frame):
        """Handle SIGINT (CTRL-C) gracefully"""
        print(f"\n[{datetime.now()}] Received signal {signum}. Shutting down gracefully...")
        self.running = False
        
    def worker_task(self):
        """Worker thread that performs some task over time"""
        counter = 0
        while self.running:
            counter += 1
            print(f"[{datetime.now()}] Worker task iteration {counter}")
            
            # Simulate some work
            time.sleep(2)
            
            # Check if we should stop
            if not self.running:
                break
                
        print(f"[{datetime.now()}] Worker thread stopped")
        
    def start(self):
        """Start the application"""
        # Register signal handler for CTRL-C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print(f"[{datetime.now()}] Starting application...")
        print("Press CTRL-C to stop")
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self.worker_task, daemon=True)
        self.worker_thread.start()
        
        try:
            # Main loop - keep the program running
            while self.running:
                time.sleep(0.1)  # Small sleep to prevent busy waiting
                
        except KeyboardInterrupt:
            # Fallback in case signal handler doesn't work
            print(f"\n[{datetime.now()}] KeyboardInterrupt caught")
            self.running = False
            
        # Wait for worker thread to finish
        if self.worker_thread and self.worker_thread.is_alive():
            print(f"[{datetime.now()}] Waiting for worker thread to finish...")
            self.worker_thread.join(timeout=5)  # Wait up to 5 seconds
            
        print(f"[{datetime.now()}] Application stopped")

if __name__ == "__main__":
    app = WorkerApplication()
    app.start()