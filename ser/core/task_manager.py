"""Task management module for handling task queues and state transitions."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json
from pathlib import Path
from enum import Enum

class TaskState(Enum):
    """Possible states for a task."""
    PENDING = 'pending'
    QUEUED = 'queued'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

@dataclass
class TaskMetadata:
    """Metadata for task tracking and management."""
    created_at: datetime
    updated_at: datetime
    agent_id: str
    priority: int
    retries: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None

class TaskManager:
    """Manages task queues, states, and persistence."""

    def __init__(self, storage_dir: Path = None):
        self.logger = logging.getLogger(__name__)
        self.storage_dir = storage_dir or Path.cwd() / 'task_storage'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.task_queues: Dict[str, List[str]] = {
            'high': [],
            'medium': [],
            'low': []
        }
        self._load_persisted_tasks()

    def create_task(self, task_id: str, task_data: Any, agent_id: str,
                    priority: int = 1) -> bool:
        """Create a new task with the given parameters."""
        if task_id in self.tasks:
            self.logger.error(f"Task {task_id} already exists")
            return False

        now = datetime.now()
        metadata = TaskMetadata(
            created_at=now,
            updated_at=now,
            agent_id=agent_id,
            priority=priority
        )

        task = {
            'id': task_id,
            'data': task_data,
            'state': TaskState.PENDING.value,
            'metadata': metadata.__dict__
        }

        self.tasks[task_id] = task
        self._add_to_queue(task_id, priority)
        self._persist_task(task_id)
        return True

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next task from the highest priority non-empty queue."""
        for queue in ['high', 'medium', 'low']:
            if self.task_queues[queue]:
                task_id = self.task_queues[queue][0]
                if self.update_task_state(task_id, TaskState.RUNNING):
                    self.task_queues[queue].pop(0)
                    return self.tasks[task_id]
        return None

    def update_task_state(self, task_id: str, new_state: TaskState,
                         error_message: str = None) -> bool:
        """Update the state of a task."""
        if task_id not in self.tasks:
            self.logger.error(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]
        task['state'] = new_state.value
        task['metadata']['updated_at'] = datetime.now()

        if error_message:
            task['metadata']['error_message'] = error_message
            if new_state == TaskState.FAILED:
                return self._handle_task_failure(task_id)

        self._persist_task(task_id)
        return True

    def _handle_task_failure(self, task_id: str) -> bool:
        """Handle task failure and implement retry logic."""
        task = self.tasks[task_id]
        metadata = task['metadata']

        if metadata['retries'] < metadata['max_retries']:
            metadata['retries'] += 1
            task['state'] = TaskState.PENDING.value
            self._add_to_queue(task_id, metadata['priority'])
            self.logger.info(f"Retrying task {task_id} (attempt {metadata['retries']})")
            return True

        self.logger.error(f"Task {task_id} failed after {metadata['retries']} retries")
        return False

    def _add_to_queue(self, task_id: str, priority: int) -> None:
        """Add a task to the appropriate priority queue."""
        queue_name = 'high' if priority > 1 else 'low' if priority < 1 else 'medium'
        self.task_queues[queue_name].append(task_id)

    def _persist_task(self, task_id: str) -> None:
        """Persist task data to storage."""
        try:
            task_file = self.storage_dir / f"{task_id}.json"
            with task_file.open('w') as f:
                json.dump(self.tasks[task_id], f)
        except Exception as e:
            self.logger.error(f"Error persisting task {task_id}: {str(e)}")

    def _load_persisted_tasks(self) -> None:
        """Load persisted tasks from storage."""
        try:
            for task_file in self.storage_dir.glob('*.json'):
                with task_file.open('r') as f:
                    task = json.load(f)
                    task_id = task['id']
                    self.tasks[task_id] = task
                    if task['state'] == TaskState.PENDING.value:
                        self._add_to_queue(task_id, task['metadata']['priority'])
        except Exception as e:
            self.logger.error(f"Error loading persisted tasks: {str(e)}")

    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific task."""
        return self.tasks.get(task_id)

    def get_queue_status(self) -> Dict[str, int]:
        """Get the current status of all task queues."""
        return {
            queue: len(tasks) for queue, tasks in self.task_queues.items()
        }

    def cleanup_completed_tasks(self, max_age_days: int = 7) -> int:
        """Remove completed tasks older than the specified age."""
        cleanup_count = 0
        cutoff_date = datetime.now().timestamp() - (max_age_days * 86400)

        for task_id, task in list(self.tasks.items()):
            if task['state'] in [TaskState.COMPLETED.value, TaskState.CANCELLED.value]:
                completed_at = datetime.fromisoformat(task['metadata']['updated_at']).timestamp()
                if completed_at < cutoff_date:
                    del self.tasks[task_id]
                    (self.storage_dir / f"{task_id}.json").unlink(missing_ok=True)
                    cleanup_count += 1

        return cleanup_count

    def process_task(self, task_data: Any) -> bool:
        """Process a task with the given data."""
        try:
            # Basic task processing implementation for testing
            return True
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return False

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks in the system."""
        return [{
            'id': task['id'],
            'type': task['data'].get('type', 'unknown'),
            'status': task['state'],
            'created_at': task['metadata']['created_at'].isoformat(),
            'result': task.get('result', None)
        } for task in self.tasks.values()]