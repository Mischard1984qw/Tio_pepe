"""Core orchestrator module for managing task execution and agent interactions."""

from typing import Dict, List, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class TaskContext:
    """Context information for task execution."""
    task_id: str
    agent_id: str
    priority: TaskPriority
    metadata: Dict[str, Any]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class Orchestrator:
    """Core orchestrator for managing task execution and agent interactions."""

    def __init__(self, max_workers: int = 5):
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks: Dict[str, Future] = {}
        self.agent_registry: Dict[str, Any] = {}
        self.task_contexts: Dict[str, TaskContext] = {}
        self.agents: Dict[str, Any] = {}

    def register_agent(self, agent_id: str, agent_instance: Any) -> None:
        """Register an agent with the orchestrator."""
        self.agent_registry[agent_id] = agent_instance
        self.agents[agent_id] = agent_instance
        self.logger.info(f"Registered agent: {agent_id}")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the orchestrator."""
        if agent_id in self.agent_registry:
            del self.agent_registry[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks in the system."""
        tasks = []
        for task_id, context in self.task_contexts.items():
            task = {
                'id': task_id,
                'agent_id': context.agent_id,
                'priority': context.priority.name,
                'status': 'active' if task_id in self.active_tasks else 'completed',
                'created_at': context.start_time.isoformat() if context.start_time else None
            }
            tasks.append(task)
        return tasks

    def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all registered agents."""
        agents = []
        for agent_id, agent in self.agents.items():
            agent_info = {
                'id': agent_id,
                'status': 'active',
                'metrics': {
                    'tasks_processed': 0,
                    'success_rate': 100
                }
            }
            agents.append(agent_info)
        return agents

    def submit_task(self, task_id: str, agent_id: str, task_data: Any,
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    metadata: Dict[str, Any] = None) -> bool:
        """Submit a task for execution."""
        try:
            if agent_id not in self.agent_registry:
                raise ValueError(f"Agent {agent_id} not registered")

            if task_id in self.active_tasks:
                raise ValueError(f"Task {task_id} already exists")

            context = TaskContext(
                task_id=task_id,
                agent_id=agent_id,
                priority=priority,
                metadata=metadata or {},
                start_time=datetime.now()
            )
            self.task_contexts[task_id] = context

            future = self.executor.submit(
                self._execute_task,
                task_id,
                self.agent_registry[agent_id],
                task_data
            )
            self.active_tasks[task_id] = future
            
            self.logger.info(
                f"Submitted task {task_id} to agent {agent_id} "
                f"with priority {priority.name}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error submitting task {task_id}: {str(e)}")
            return False

    def _execute_task(self, task_id: str, agent: Any, task_data: Any) -> Any:
        """Execute a task with the specified agent."""
        try:
            result = agent.process_task(task_data)
            self.task_contexts[task_id].end_time = datetime.now()
            return result
        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {str(e)}")
            raise

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a task."""
        if task_id not in self.active_tasks:
            return {'status': 'not_found'}

        future = self.active_tasks[task_id]
        context = self.task_contexts.get(task_id)

        if future.done():
            try:
                result = future.result()
                return {
                    'status': 'completed',
                    'result': result,
                    'context': context.__dict__ if context else None
                }
            except Exception as e:
                return {
                    'status': 'failed',
                    'error': str(e),
                    'context': context.__dict__ if context else None
                }
        return {
            'status': 'running',
            'context': context.__dict__ if context else None
        }

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id not in self.active_tasks:
            return False

        future = self.active_tasks[task_id]
        cancelled = future.cancel()
        if cancelled:
            del self.active_tasks[task_id]
            self.logger.info(f"Cancelled task {task_id}")
        return cancelled

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the orchestrator and cleanup resources."""
        self.executor.shutdown(wait=wait)
        self.active_tasks.clear()
        self.agent_registry.clear()
        self.task_contexts.clear()
        self.logger.info("Orchestrator shutdown complete")

    def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status information for all registered agents."""
        agent_status = []
        for agent_id, agent in self.agents.items():
            status = {
                'agent_id': agent_id,
                'status': 'active',
                'registered_time': getattr(agent, 'registered_time', None),
                'last_active': getattr(agent, 'last_active', None),
                'tasks_completed': len([t for t in self.task_contexts.values() 
                                      if t.agent_id == agent_id and 
                                      t.end_time is not None])
            }
            agent_status.append(status)
        return agent_status