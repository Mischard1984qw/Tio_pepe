"""Memory management module for temporary data storage and context handling in Tío Pepe."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import threading
import logging
from pathlib import Path
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MemoryManager:
    """Manages temporary data storage and context handling."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.data_store: Dict[str, Dict[str, Any]] = {}
        self.context_store: Dict[str, Dict[str, Any]] = {}
        self.expiration_store: Dict[str, datetime] = {}
        self._lock = threading.Lock()
        self.executor = ThreadPoolExecutor()
        
        # Configure memory limits
        self.max_memory_size = self.config.get('max_memory_size', 1024 * 1024 * 100)  # 100MB default
        self.default_ttl = self.config.get('default_ttl', 3600)  # 1 hour default
        self.cleanup_interval = self.config.get('cleanup_interval', 300)  # 5 minutes default
        
        # Start cleanup task
        self._start_cleanup_task()

    def store(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store data with optional time-to-live."""
        try:
            with self._lock:
                if self._check_memory_limit(value):
                    self.data_store[key] = {
                        'value': value,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    if ttl is not None:
                        self.expiration_store[key] = datetime.now() + timedelta(seconds=ttl)
                    elif self.default_ttl > 0:
                        self.expiration_store[key] = datetime.now() + timedelta(seconds=self.default_ttl)
                    
                    self.logger.debug(f"Stored data with key: {key}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error storing data: {str(e)}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data by key."""
        try:
            with self._lock:
                if key in self.data_store:
                    if self._is_expired(key):
                        self._remove_key(key)
                        return None
                    return self.data_store[key]['value']
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving data: {str(e)}")
            return None

    def set_context(self, context_id: str, context_data: Dict[str, Any]) -> bool:
        """Set context information."""
        try:
            with self._lock:
                self.context_store[context_id] = {
                    'data': context_data,
                    'updated_at': datetime.now().isoformat()
                }
                return True
        except Exception as e:
            self.logger.error(f"Error setting context: {str(e)}")
            return False

    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get context information by ID."""
        try:
            with self._lock:
                if context_id in self.context_store:
                    return self.context_store[context_id]['data']
                return None
        except Exception as e:
            self.logger.error(f"Error getting context: {str(e)}")
            return None

    async def store_async(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Asynchronously store data."""
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, self.store, key, value, ttl
        )

    async def retrieve_async(self, key: str) -> Optional[Any]:
        """Asynchronously retrieve data."""
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, self.retrieve, key
        )

    def remove(self, key: str) -> bool:
        """Remove data by key."""
        try:
            with self._lock:
                return self._remove_key(key)
        except Exception as e:
            self.logger.error(f"Error removing data: {str(e)}")
            return False

    def clear(self) -> bool:
        """Clear all stored data and contexts."""
        try:
            with self._lock:
                self.data_store.clear()
                self.context_store.clear()
                self.expiration_store.clear()
                return True
        except Exception as e:
            self.logger.error(f"Error clearing memory: {str(e)}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        with self._lock:
            return {
                'data_entries': len(self.data_store),
                'context_entries': len(self.context_store),
                'expired_entries': sum(1 for k in self.data_store if self._is_expired(k))
            }

    def _check_memory_limit(self, value: Any) -> bool:
        """Check if storing the value would exceed memory limits."""
        try:
            current_size = sum(len(str(v)) for v in self.data_store.values())
            new_size = len(str(value))
            return (current_size + new_size) <= self.max_memory_size
        except:
            return False

    def _is_expired(self, key: str) -> bool:
        """Check if a key has expired."""
        if key in self.expiration_store:
            return datetime.now() > self.expiration_store[key]
        return False

    def _remove_key(self, key: str) -> bool:
        """Remove a key and its associated data."""
        if key in self.data_store:
            del self.data_store[key]
        if key in self.expiration_store:
            del self.expiration_store[key]
        return True

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        with self._lock:
            expired_keys = [k for k in self.data_store if self._is_expired(k)]
            for key in expired_keys:
                self._remove_key(key)

    def _start_cleanup_task(self) -> None:
        """Start the periodic cleanup task."""
        def cleanup_task():
            while True:
                try:
                    self._cleanup_expired()
                except Exception as e:
                    self.logger.error(f"Error in cleanup task: {str(e)}")
                finally:
                    threading.Event().wait(self.cleanup_interval)

        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()