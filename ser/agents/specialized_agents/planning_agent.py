"""Planning and workflow management agent for the Tío Pepe system."""

from typing import Dict, Any, List, Optional
import logging
import networkx as nx
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WorkflowTask:
    """Represents a task in a workflow."""
    id: str
    name: str
    dependencies: List[str]
    status: str = 'pending'
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    config: Dict[str, Any] = None

class PlanningAgent:
    """Specialized agent for planning and workflow management."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.workflows: Dict[str, nx.DiGraph] = {}
        self.tasks: Dict[str, WorkflowTask] = {}

    def create_workflow(self, workflow_id: str) -> bool:
        """Create a new workflow."""
        try:
            if workflow_id in self.workflows:
                raise ValueError(f"Workflow {workflow_id} already exists")
            
            self.workflows[workflow_id] = nx.DiGraph()
            self.logger.info(f"Created workflow: {workflow_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating workflow: {str(e)}")
            return False

    def add_task(self, workflow_id: str, task: WorkflowTask) -> bool:
        """Add a task to a workflow."""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} does not exist")

            graph = self.workflows[workflow_id]
            graph.add_node(task.id, task=task)
            
            # Add dependencies
            for dep_id in task.dependencies:
                if dep_id not in graph.nodes:
                    raise ValueError(f"Dependency {dep_id} not found in workflow")
                graph.add_edge(dep_id, task.id)

            # Check for cycles
            if not nx.is_directed_acyclic_graph(graph):
                graph.remove_node(task.id)
                raise ValueError("Adding this task would create a cycle in the workflow")

            self.tasks[task.id] = task
            self.logger.info(f"Added task {task.id} to workflow {workflow_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding task: {str(e)}")
            return False

    def get_ready_tasks(self, workflow_id: str) -> List[WorkflowTask]:
        """Get tasks that are ready to be executed (all dependencies completed)."""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} does not exist")

            graph = self.workflows[workflow_id]
            ready_tasks = []

            for node in graph.nodes:
                task = graph.nodes[node]['task']
                if task.status != 'pending':
                    continue

                dependencies = list(graph.predecessors(node))
                if all(self.tasks[dep_id].status == 'completed' for dep_id in dependencies):
                    ready_tasks.append(task)

            return ready_tasks

        except Exception as e:
            self.logger.error(f"Error getting ready tasks: {str(e)}")
            return []

    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update the status of a task."""
        try:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")

            task = self.tasks[task_id]
            task.status = status

            if status == 'in_progress':
                task.start_time = datetime.now()
            elif status in ['completed', 'failed']:
                task.end_time = datetime.now()

            self.logger.info(f"Updated task {task_id} status to {status}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating task status: {str(e)}")
            return False

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow."""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} does not exist")

            graph = self.workflows[workflow_id]
            total_tasks = len(graph.nodes)
            completed_tasks = sum(1 for node in graph.nodes 
                                if graph.nodes[node]['task'].status == 'completed')
            failed_tasks = sum(1 for node in graph.nodes 
                             if graph.nodes[node]['task'].status == 'failed')

            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'in_progress_tasks': sum(1 for node in graph.nodes 
                                       if graph.nodes[node]['task'].status == 'in_progress'),
                'pending_tasks': total_tasks - completed_tasks - failed_tasks,
                'is_completed': completed_tasks == total_tasks,
                'has_failures': failed_tasks > 0
            }

        except Exception as e:
            self.logger.error(f"Error getting workflow status: {str(e)}")
            return {}

    def cleanup(self) -> None:
        """Cleanup resources used by the agent."""
        self.workflows.clear()
        self.tasks.clear()
        self.logger.info("Planning agent cleaned up")