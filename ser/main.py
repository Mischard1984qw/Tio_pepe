"""Main entry point for the Tío Pepe system."""

from flask import Flask
import logging
import asyncio
from core.orchestrator import Orchestrator
from core.task_manager import TaskManager
from core.scheduler import TaskScheduler
from core.notifications import NotificationManager
from core.data_export import DataExporter
from core.event_bus import EventBus
from web.web_server import create_app
from tools.logging_manager import setup_logging
from agents.agent_manager import AgentManager

def initialize_system():
    """Initialize core system components."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Initializing Tío Pepe system...")

    # Initialize core components
    event_bus = EventBus()
    task_manager = TaskManager()
    agent_manager = AgentManager()
    notification_manager = NotificationManager()
    task_scheduler = TaskScheduler(task_manager, event_bus)
    data_exporter = DataExporter()
    orchestrator = Orchestrator()
    
    # Register managers with orchestrator
    orchestrator.register_agent('task_manager', task_manager)
    orchestrator.register_agent('agent_manager', agent_manager)
    orchestrator.register_agent('notification_manager', notification_manager)
    orchestrator.register_agent('task_scheduler', task_scheduler)
    orchestrator.register_agent('data_exporter', data_exporter)

    return orchestrator

def main():
    """Main entry point for the system."""
    try:
        # Initialize system components
        orchestrator = initialize_system()

        # Create and configure Flask application
        app = create_app(orchestrator)

        # Start the web server
        app.run(host='0.0.0.0', port=5000, debug=False)

    except Exception as e:
        logging.error(f"System initialization failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()