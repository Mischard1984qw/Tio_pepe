"""Agent lifecycle management for the Tío Pepe system."""

from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for a specialized agent."""
    type: str
    name: str
    enabled: bool = True
    config: Dict[str, Any] = None

class AgentManager:
    """Manages the lifecycle of specialized agents in the system."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, Any] = {}
        self.configs: Dict[str, AgentConfig] = {}

    def register_agent_config(self, config: AgentConfig) -> None:
        """Register configuration for a specialized agent."""
        self.configs[config.type] = config
        self.logger.info(f"Registered config for {config.type} agent")

    def initialize_agent(self, agent_type: str) -> Optional[Any]:
        """Initialize a specialized agent based on its configuration."""
        if agent_type not in self.configs:
            self.logger.error(f"No configuration found for agent type: {agent_type}")
            return None

        config = self.configs[agent_type]
        if not config.enabled:
            self.logger.warning(f"Agent {agent_type} is disabled")
            return None

        try:
            # Import the appropriate agent class dynamically
            module_path = f"specialized_agents.{agent_type.lower()}_agent"
            agent_module = __import__(module_path, fromlist=[''])
            agent_class = getattr(agent_module, f"{agent_type}Agent")
            
            # Initialize the agent with its configuration
            agent = agent_class(config.config)
            self.agents[agent_type] = agent
            self.logger.info(f"Initialized {agent_type} agent")
            return agent

        except Exception as e:
            self.logger.error(f"Failed to initialize {agent_type} agent: {str(e)}")
            return None

    def get_agent(self, agent_type: str) -> Optional[Any]:
        """Get an initialized agent instance."""
        if agent_type not in self.agents:
            return self.initialize_agent(agent_type)
        return self.agents.get(agent_type)

    def shutdown_agent(self, agent_type: str) -> bool:
        """Shutdown and cleanup a specialized agent."""
        if agent_type not in self.agents:
            return False

        try:
            agent = self.agents[agent_type]
            if hasattr(agent, 'cleanup'):
                agent.cleanup()
            del self.agents[agent_type]
            self.logger.info(f"Shutdown {agent_type} agent")
            return True
        except Exception as e:
            self.logger.error(f"Error shutting down {agent_type} agent: {str(e)}")
            return False

    def shutdown_all(self) -> None:
        """Shutdown all active agents."""
        for agent_type in list(self.agents.keys()):
            self.shutdown_agent(agent_type)

    def register_agent(self, agent_id: str, agent_instance: Any) -> None:
        """Register an agent with the system."""
        self.agents[agent_id] = agent_instance
        self.logger.info(f"Registered agent: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get a registered agent by ID."""
        return self.agents.get(agent_id)

    def deregister_agent(self, agent_id: str) -> None:
        """Remove an agent from the system."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Deregistered agent: {agent_id}")