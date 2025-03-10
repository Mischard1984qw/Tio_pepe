"""Event bus module for implementing a publish-subscribe messaging system."""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio
from enum import Enum
from queue import Queue
from threading import Lock

class EventPriority(Enum):
    """Priority levels for event processing."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Event:
    """Represents an event in the system."""
    type: str
    data: Any
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = None
    source: str = None
    id: str = None

class EventBus:
    """Implements a publish-subscribe messaging system."""

    def __init__(self, max_queue_size: int = 1000):
        self.logger = logging.getLogger(__name__)
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue: Queue = Queue(maxsize=max_queue_size)
        self.lock = Lock()
        self._running = False
        self._event_loop = None

    def subscribe(self, event_type: str, callback: Callable) -> bool:
        """Subscribe to a specific event type."""
        try:
            with self.lock:
                if event_type not in self.subscribers:
                    self.subscribers[event_type] = []
                if callback not in self.subscribers[event_type]:
                    self.subscribers[event_type].append(callback)
                    self.logger.info(f"Subscribed to event type: {event_type}")
                return True
        except Exception as e:
            self.logger.error(f"Error subscribing to event: {str(e)}")
            return False

    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """Unsubscribe from a specific event type."""
        try:
            with self.lock:
                if event_type in self.subscribers and callback in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(callback)
                    if not self.subscribers[event_type]:
                        del self.subscribers[event_type]
                    self.logger.info(f"Unsubscribed from event type: {event_type}")
                return True
        except Exception as e:
            self.logger.error(f"Error unsubscribing from event: {str(e)}")
            return False

    def publish(self, event: Event) -> bool:
        """Publish an event to all subscribers."""
        try:
            if not event.timestamp:
                event.timestamp = datetime.now()

            self.event_queue.put(event)
            self.logger.debug(f"Published event: {event.type}")
            return True
        except Exception as e:
            self.logger.error(f"Error publishing event: {str(e)}")
            return False

    async def _process_event(self, event: Event) -> None:
        """Process a single event by notifying all subscribers."""
        if event.type not in self.subscribers:
            return

        for callback in self.subscribers[event.type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                self.logger.error(f"Error in event handler: {str(e)}")

    async def _event_processor(self) -> None:
        """Main event processing loop."""
        while self._running:
            try:
                event = self.event_queue.get_nowait()
                await self._process_event(event)
                self.event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.1)

    def start(self) -> None:
        """Start the event processing loop."""
        if self._running:
            return

        self._running = True
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.create_task(self._event_processor())
        self.logger.info("Event bus started")

    def stop(self) -> None:
        """Stop the event processing loop."""
        self._running = False
        if self._event_loop:
            self._event_loop.stop()
            self._event_loop.close()
            self._event_loop = None
        self.logger.info("Event bus stopped")

    def get_subscriber_count(self, event_type: str) -> int:
        """Get the number of subscribers for a specific event type."""
        return len(self.subscribers.get(event_type, []))

    def get_queue_size(self) -> int:
        """Get the current size of the event queue."""
        return self.event_queue.qsize()

    def clear_queue(self) -> None:
        """Clear all pending events from the queue."""
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
                self.event_queue.task_done()
            except:
                pass
        self.logger.info("Event queue cleared")