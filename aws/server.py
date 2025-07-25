import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServerConfig:
    """Server configuration parameters."""
    host: str = '127.0.0.1'
    port: int = 65432
    heartbeat_interval: float = 5.0  # Reduced from 1 second for better performance
    log_level: str = 'INFO'

class AsyncServer:
    """Optimized async server with proper resource management."""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        self.config = config or ServerConfig()
        self.shutdown_event = asyncio.Event()
        self.tasks = set()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging level based on config."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)
    
    def _signal_handler(self, sig_num: int) -> None:
        """Handle shutdown signals gracefully."""
        signal_name = signal.Signals(sig_num).name
        logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")
        self.shutdown_event.set()
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        if sys.platform != 'win32':

            # Unix signals
            for sig in [signal.SIGTERM, signal.SIGINT]:
                signal.signal(sig, lambda s, f: self._signal_handler(s))
        else:
            # Windows signals
            signal.signal(signal.SIGINT, lambda s, f: self._signal_handler(s))
    
    async def _heartbeat_loop(self) -> None:
        """Optimized heartbeat loop with configurable interval."""
        logger.info("Server heartbeat started")
        last_log_time = datetime.now()
        
        try:
            while not self.shutdown_event.is_set():
                try:
                    # Use wait_for with timeout for responsive shutdown
                    await asyncio.wait_for(
                        self.shutdown_event.wait(), 
                        timeout=self.config.heartbeat_interval
                    )
                    break  # Shutdown event was set
                except asyncio.TimeoutError:
                    # Normal heartbeat - only log periodically to reduce noise
                    current_time = datetime.now()
                    if (current_time - last_log_time).total_seconds() >= 30:  # Log every 30 seconds
                        logger.info(f"Server is running - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        last_log_time = current_time
                
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")
        finally:
            logger.info("Heartbeat loop terminated")
    
    async def _cleanup_tasks(self) -> None:
        """Clean up running tasks gracefully."""
        if self.tasks:
            logger.info(f"Cancelling {len(self.tasks)} running tasks...")
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            await asyncio.gather(*self.tasks, return_exceptions=True)
            logger.info("All tasks cancelled successfully")
    
    async def start(self) -> None:
        """Start the server with proper error handling and resource management."""
        logger.info(f"Starting server on {self.config.host}:{self.config.port}")
        self._setup_signal_handlers()
        
        try:
            # Create and track the heartbeat task
            heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self.tasks.add(heartbeat_task)
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in server: {e}")
        finally:
            logger.info("Shutting down server...")
            await self._cleanup_tasks()
            logger.info("Server shutdown complete")

async def main():
    """Main entry point with error handling."""
    try:
        config = ServerConfig(
            host='127.0.0.1',
            port=65432,
            heartbeat_interval=5.0,
            log_level='INFO'
        )
        
        server = AsyncServer(config)
        await server.start()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)