"""Google Chat Host
"""
import os

from google import genai

from shared_app_utilities import (
    get_script_name,
    LoggerFactory,
    SecretsManager,
    AppConfiguration)

import pdb

MAIN_SCRIPT_NAME = get_script_name(__file__)

import asyncio
import sys
import signal

class ConsoleChatClient:
    """
    A simple console chat client demonstrating asyncio for asynchronous operations
    and graceful exit handling.

    Messages typed by the user are put into an internal queue and then processed
    by a separate asynchronous task. The client can be stopped by typing 'exit'
    or by sending an interrupt signal (e.g., Ctrl+C).
    """

    def __init__(self, prompt: str = "You: ", chat_client=None):
        """
        Initializes the ConsoleChatClient.

        Args:
            prompt: The prompt string to display to the user for input.
        """
        self.chat_client = chat_client
        self.prompt = prompt
        # An asyncio.Queue to hold messages for processing.
        self.message_queue = asyncio.Queue()
        # An asyncio.Event to signal whether the chat client is running.
        # This is used for graceful shutdown.
        self.running = asyncio.Event()
        # An asyncio.Event to signal when message processing is complete for the current turn.
        self.processing_done_event = asyncio.Event()
        # List to keep track of all active asyncio tasks.
        self.tasks = []
        # Reference to the running event loop, set when start() is called.
        self.loop = None

    async def _read_input(self):
        """
        Asynchronously reads input from the console.

        This function runs in a loop, continuously prompting the user for input.
        It uses `loop.run_in_executor` to run the blocking `input()` call in
        a separate thread, preventing it from blocking the main asyncio event loop.
        If the user types 'exit', it signals the client to stop.
        It now waits for the `processing_done_event` before prompting for the next input.
        """
        print("Chat client started. Type 'exit' to quit.")
        # Signal that processing is done initially so the first prompt appears.
        self.processing_done_event.set()

        while self.running.is_set():
            # Wait for the previous message to be processed before showing the next prompt.
            await self.processing_done_event.wait()

            try:
                # Run the blocking input() function in a default thread pool executor.
                # This prevents the main asyncio loop from freezing while waiting for input.
                user_input = await self.loop.run_in_executor(None, input, self.prompt)

                if user_input.lower() == 'exit':
                    print("Initiating graceful exit...")
                    self.running.clear()  # Signal all tasks to stop
                    break

                # Clear the event, indicating that processing for this input is now pending.
                self.processing_done_event.clear()
                # Put the user's message into the queue for processing.
                await self.message_queue.put(user_input)
            except Exception as e:
                # Catch any errors during input (e.g., stdin closed unexpectedly)
                print(f"Error reading input: {e}")
                self.running.clear()  # Signal to stop on error
                break

    async def _process_messages(self):
        """
        Asynchronously processes messages from the internal queue.

        This task continuously pulls messages from the `message_queue` and prints them.
        It includes a timeout when getting messages to ensure it can periodically
        check the `self.running` event and allow for graceful shutdown even if
        the queue is empty. It also ensures all messages are processed before exiting.
        After processing a message, it sets the `processing_done_event` to allow
        the next user prompt to appear.
        """
        # Continue processing as long as the client is running OR there are messages
        # left in the queue to ensure all pending messages are handled during shutdown.
        while self.running.is_set() or not self.message_queue.empty():
            try:
                # Wait for a message with a timeout. The timeout allows the loop
                # to periodically check `self.running.is_set()` for shutdown signals.
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)

                # Simulate some processing time
                if len(message) > 0:
                    print(f"Processing: {message}")
                    if self.chat_client is not None:
                        response_message = self.chat_client.get_chat_response(message)
                        print(f"Response: {response_message}")
                # Mark the task as done for the message in the queue.
                self.message_queue.task_done()
                # Signal that processing for this message is complete.
                self.processing_done_event.set()
            except asyncio.TimeoutError:
                # This exception is expected when no messages are in the queue
                # within the timeout period. The loop will continue and re-check
                # the `self.running` event.
                pass
            except Exception as e:
                # Catch any other unexpected errors during message processing.
                print(f"Error processing message: {e}")
                self.running.clear()  # Signal to stop on error
                break

    def _handle_exit_signal(self, signum, frame):
        """
        Callback function to handle operating system signals (e.g., SIGINT, SIGTERM).

        When a signal like Ctrl+C is received, this function is called to
        initiate the graceful shutdown process by clearing the `self.running` event.
        """
        print(f"\nSignal {signum} received. Initiating graceful shutdown...")
        self.running.clear()  # Signal all tasks to stop

    async def start(self):
        """
        Starts the console chat client.

        This method sets up signal handlers, creates and starts the asynchronous
        tasks for reading input and processing messages, and then waits for the
        client to be signaled to stop (either by 'exit' command or OS signal).
        It ensures all tasks complete before the method returns.
        """
        # Get the currently running event loop.
        self.loop = asyncio.get_running_loop()
        # Set the running flag to True, indicating the client is active.
        self.running.set()

        # Set up signal handlers for graceful exit (e.g., Ctrl+C).
        # These are not available on all platforms (e.g., Windows), so we use a try-except.
        try:
            self.loop.add_signal_handler(signal.SIGINT, self._handle_exit_signal, signal.SIGINT, None)
            self.loop.add_signal_handler(signal.SIGTERM, self._handle_exit_signal, signal.SIGTERM, None)
        except NotImplementedError:
            print("Warning: Cannot add signal handlers on this platform (e.g., Windows).")
            print("Graceful exit will only work by typing 'exit'.")
        except ValueError as e:
            # Catch cases where signal handler might already be set or other issues
            print(f"Warning: Could not set signal handler: {e}")


        # Create the asynchronous tasks.
        input_task = self.loop.create_task(self._read_input(), name="InputReader")
        process_task = self.loop.create_task(self._process_messages(), name="MessageProcessor")
        self.tasks.extend([input_task, process_task])

        # Wait for the `self.running` event to be cleared. This means the client
        # has been signaled to stop (either by user input or OS signal).
        await self.running.wait()

        # Once the running event is cleared, we wait for all tasks to complete.
        # `return_exceptions=True` prevents `gather` from stopping if one task raises an exception.
        print("Shutdown initiated. Waiting for all tasks to finish...")
        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("All chat client tasks have finished.")

    async def stop(self):
        """
        Manually stops the console chat client gracefully.

        This method can be called externally to initiate a clean shutdown.
        """
        if self.running.is_set():
            print("External stop requested. Stopping chat client...")
            self.running.clear()  # Signal tasks to stop
            # Wait for all tasks to complete before returning.
            await asyncio.gather(*self.tasks, return_exceptions=True)
            print("Chat client stopped gracefully.")
        else:
            print("Chat client is not currently running.")


class GoogleChatClient(object):
    def __init__(self):
        self.logger = LoggerFactory.get_logger(MAIN_SCRIPT_NAME)
        self.app_configuration = AppConfiguration(main_script_name=MAIN_SCRIPT_NAME)

        # Retrieve API key from secrets.

        secrets_file_path = self.app_configuration.get('secrets:file-path')
        self.secrets_manager = SecretsManager(
            main_script_name=MAIN_SCRIPT_NAME,
            secrets_file_path=secrets_file_path)
        secrets = self.secrets_manager.get_secrets()

        gemini_ai_api_secret_key = self.app_configuration.get('secrets:gemini-ai-api-secret-key')
        if gemini_ai_api_secret_key not in secrets:
            self.logger.error("Secret key is not defined in secrets. Exiting...")
            exit(1)
        gemini_ai_api_key = secrets[gemini_ai_api_secret_key]

        # Initialize client

        self.client = genai.Client(api_key=gemini_ai_api_key)
        gemini_model = self.app_configuration.get('secrets:gemini-model')
        self.client_model = gemini_model
        self.client_model = 'gemini-2.0-flash'
        self.client_model = 'gemini-2.5-flash-preview-05-20'
        self.client_model = 'gemini-2.0-flash-lite'

    def get_chat_response(self, message:str="Explain how AI works in a few words"):
        response = self.client.models.generate_content(
            model=self.client_model,
            contents=message)
        print(response.text)
        return response.text

    def get_models(self, display_supported_actions=False):
        for model in self.client.models.list():
            if '2.5' not in model.name:
                continue
            if 'generateContent' in model.supported_actions:
                print(f"[{model.name}]", model.display_name)
            if display_supported_actions:
                for action in model.supported_actions:
                    print('  supported_actions', action)


# Example Usage:
async def main():
    """Main asynchronous function to demonstrate the ConsoleChatClient.
    """
    google_chat_client = GoogleChatClient()
    # google_chat_client.get_models()
    # google_chat_client.get_chat_response()

    chat_client = ConsoleChatClient(chat_client=google_chat_client)
    await chat_client.start()
    print("Application finished.")

if __name__ == "__main__":
    # Run the main asynchronous function.
    # asyncio.run() handles the event loop creation and management.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # This will catch Ctrl+C if signal handlers couldn't be set or
        # if the program exits before the graceful shutdown fully completes.
        print("\nProgram interrupted by user (KeyboardInterrupt). Exiting.")

