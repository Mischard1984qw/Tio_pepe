"""Main coordinating agent for the Tío Pepe system."""

from typing import Dict, List, Any
from dataclasses import dataclass
import logging

@dataclass
class Task:
    """Represents a task to be processed by the system."""
    id: str
    task_type: str
    data: Dict[str, Any]
    status: str = 'pending'

class AgentZero:
    """Main coordinating agent that manages task distribution and execution."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tasks: List[Task] = []
        self.specialized_agents = {}

    def register_agent(self, agent_type: str, agent_instance: Any) -> None:
        """Register a specialized agent with the system."""
        self.specialized_agents[agent_type] = agent_instance
        self.logger.info(f"Registered {agent_type} agent")

    def create_task(self, task_type: str, task_data: Dict[str, Any]) -> Task:
        """Create a new task in the system."""
        task = Task(
            id=f"task_{len(self.tasks) + 1}",
            task_type=task_type,
            data=task_data
        )
        self.tasks.append(task)
        return task

    def route_task(self, task: Task) -> bool:
        """Route a task to the appropriate specialized agent."""
        if task.type not in self.specialized_agents:
            self.logger.error(f"No agent available for task type: {task.type}")
            return False

        agent = self.specialized_agents[task.type]
        try:
            agent.process_task(task)
            task.status = 'completed'
            return True
        except Exception as e:
            self.logger.error(f"Error processing task {task.id}: {str(e)}")
            task.status = 'failed'
            return False

    def get_task_status(self, task_id: str) -> str:
        """Get the current status of a task."""
        for task in self.tasks:
            if task.id == task_id:
                return task.status
        return 'not_found'

    def process_tasks(self) -> None:
        """Process all pending tasks in the system."""
        for task in self.tasks:
            if task.status == 'pending':
                self.route_task(task)