#\"""Task scheduler module for managing scheduled task execution."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from core.task_manager import TaskManager
from core.event_bus import EventBus, Event, EventPriority

class ScheduleType(Enum):
    """Types of task schedules supported by the system."""
    ONE_TIME = 'one_time'
    RECURRING = 'recurring'
    CRON = 'cron'

@dataclass
class ScheduleConfig:
    """Configuration for task scheduling."""
    schedule_type: ScheduleType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    interval: Optional[timedelta] = None
    cron_expression: Optional[str] = None
    retry_on_failure: bool = True
    max_retries: int = 3
    retry_delay: timedelta = timedelta(minutes=5)

class TaskScheduler:
    """Manages scheduled task execution."""

    def __init__(self, task_manager: TaskManager, event_bus: EventBus):
        self.logger = logging.getLogger(__name__)
        self.task_manager = task_manager
        self.event_bus = event_bus
        self.scheduler = BackgroundScheduler()
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.offline_tasks: List[Dict[str, Any]] = []
        self.scheduler.start()

    def schedule_task(self, task_id: str, task_data: Any, schedule_config: ScheduleConfig,
                     agent_id: str, priority: int = 1) -> bool:
        """Schedule a task for execution."""
        try:
            if task_id in self.scheduled_tasks:
                self.logger.error(f"Task {task_id} already scheduled")
                return False

            trigger = self._create_trigger(schedule_config)
            if not trigger:
                return False

            job = self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                args=[task_id, task_data, agent_id, priority, schedule_config],
                id=task_id
            )

            self.scheduled_tasks[task_id] = {
                'job': job,
                'config': schedule_config.__dict__,
                'agent_id': agent_id,
                'priority': priority,
                'retry_count': 0
            }

            self.event_bus.publish(Event(
                type='task_scheduled',
                data={
                    'task_id': task_id,
                    'schedule_type': schedule_config.schedule_type.value
                },
                priority=EventPriority.NORMAL
            ))

            self.logger.info(f"Task {task_id} scheduled successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to schedule task {task_id}: {str(e)}")
            return False

    def _create_trigger(self, config: ScheduleConfig) -> Optional[Any]:
        """Create an appropriate scheduler trigger based on schedule configuration."""
        try:
            if config.schedule_type == ScheduleType.ONE_TIME:
                if not config.start_date:
                    raise ValueError("Start date required for one-time schedule")
                return DateTrigger(run_date=config.start_date)

            elif config.schedule_type == ScheduleType.RECURRING:
                if not config.interval:
                    raise ValueError("Interval required for recurring schedule")
                return IntervalTrigger(
                    seconds=int(config.interval.total_seconds()),
                    start_date=config.start_date,
                    end_date=config.end_date
                )

            elif config.schedule_type == ScheduleType.CRON:
                if not config.cron_expression:
                    raise ValueError("Cron expression required for cron schedule")
                return CronTrigger.from_crontab(config.cron_expression)

            else:
                raise ValueError(f"Unsupported schedule type: {config.schedule_type}")

        except Exception as e:
            self.logger.error(f"Failed to create trigger: {str(e)}")
            return None

    async def _execute_task(self, task_id: str, task_data: Any, agent_id: str,
                          priority: int, config: ScheduleConfig) -> None:
        """Execute a scheduled task with retry support."""
        try:
            result = await self.task_manager.execute_task(task_id, task_data, agent_id, priority)
            
            if not result.get('success', False) and config.retry_on_failure:
                task_info = self.scheduled_tasks.get(task_id)
                if task_info and task_info['retry_count'] < config.max_retries:
                    task_info['retry_count'] += 1
                    self.scheduler.add_job(
                        func=self._execute_task,
                        trigger=DateTrigger(run_date=datetime.now() + config.retry_delay),
                        args=[task_id, task_data, agent_id, priority, config],
                        id=f"{task_id}_retry_{task_info['retry_count']}"
                    )
                    self.logger.info(f"Scheduled retry {task_info['retry_count']} for task {task_id}")
                    return

            self.event_bus.publish(Event(
                type='task_executed',
                data={
                    'task_id': task_id,
                    'success': result.get('success', False),
                    'result': result
                },
                priority=EventPriority.HIGH
            ))

        except Exception as e:
            self.logger.error(f"Task execution error for {task_id}: {str(e)}")
            if not self.task_manager.is_connected():
                self._queue_offline_task(task_id, task_data, agent_id, priority, config)

    def _queue_offline_task(self, task_id: str, task_data: Any, agent_id: str,
                          priority: int, config: ScheduleConfig) -> None:
        """Queue a task for execution when system is back online."""
        self.offline_tasks.append({
            'task_id': task_id,
            'task_data': task_data,
            'agent_id': agent_id,
            'priority': priority,
            'config': config.__dict__,
            'queued_at': datetime.now().isoformat()
        })
        self.logger.info(f"Task {task_id} queued for offline execution")

    def process_offline_tasks(self) -> None:
        """Process queued tasks when system is back online."""
        if not self.task_manager.is_connected():
            return

        queued_tasks = self.offline_tasks.copy()
        self.offline_tasks.clear()

        for task in queued_tasks:
            try:
                self.schedule_task(
                    task['task_id'],
                    task['task_data'],
                    ScheduleConfig(**task['config']),
                    task['agent_id'],
                    task['priority']
                )
            except Exception as e:
                self.logger.error(f"Failed to process offline task: {str(e)}")
                self.offline_tasks.append(task)

    def cleanup(self) -> None:
        """Cleanup scheduler resources."""
        self.scheduler.shutdown()
        self.scheduled_tasks.clear()
        self.logger.info("Task scheduler cleaned up")

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        try:
            if task_id not in self.scheduled_tasks:
                self.logger.error(f"Task {task_id} not found in scheduled tasks")
                return False

            self.scheduler.remove_job(task_id)
            del self.scheduled_tasks[task_id]
            self.logger.info(f"Task {task_id} cancelled successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False

    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get all scheduled tasks."""
        tasks = []
        for task_id, task_info in self.scheduled_tasks.items():
            next_run = task_info['job'].next_run_time
            tasks.append({
                'task_id': task_id,
                'agent_id': task_info['agent_id'],
                'priority': task_info['priority'],
                'schedule_config': task_info['config'],
                'next_run': next_run.isoformat() if next_run else None
            })
        return tasks

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        self.logger.info("Task scheduler shutdown complete")