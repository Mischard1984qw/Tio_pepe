"""Route definitions for the Tío Pepe web interface."""

from flask import Blueprint, jsonify, request, current_app
import logging
import traceback
from core.task_manager import TaskManager
import time
from agents.agent_manager import AgentManager
from agents.specialized_agents.nlp_agent import NLPAgent
from agents.specialized_agents.vision_agent import VisionAgent
from agents.specialized_agents.web_agent import WebAgent
from agents.specialized_agents.data_agent import DataAgent
from agents.specialized_agents.code_agent import CodeAgent
from agents.specialized_agents.planning_agent import PlanningAgent

# Create blueprint with a more specific name to avoid confusion
api_blueprint = Blueprint('api', __name__)

# Initialize managers
task_manager = TaskManager()
agent_manager = AgentManager()

# The orchestrator will be set when the blueprint is registered
# This avoids creating multiple instances

@api_blueprint.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

@api_blueprint.route('/tasks', methods=['GET'])
def list_tasks():
    """Get all tasks in the system."""
    try:
        tasks = task_manager.get_all_tasks()
        return jsonify({'tasks': tasks})
    except Exception as e:
        logging.error(f"Error fetching tasks: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@api_blueprint.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get details of a specific task."""
    try:
        task = task_manager.get_task(task_id)
        if task:
            return jsonify(task)
        return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        logging.error(f"Error fetching task {task_id}: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@api_blueprint.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    try:
        task_data = request.json
        if not task_data:
            return jsonify({'error': 'No task data provided'}), 400
        
        task = task_manager.create_task(task_data)
        # Use the orchestrator that was set when the blueprint was registered
        api_blueprint.orchestrator.schedule_task(task)
        return jsonify(task), 201
    except Exception as e:
        logging.error(f"Error creating task: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@api_blueprint.route('/agents', methods=['GET'])
def list_agents():
    """Get status of all agents."""
    try:
        agents = []
        # Get all registered agents from agent_manager
        for agent_id, agent in agent_manager.agents.items():
            agent_info = {
                'id': agent_id,
                'type': agent.__class__.__name__,
                'status': 'active' if hasattr(agent, 'is_active') and agent.is_active else 'inactive',
                'tasks_processed': 0,  # This would be tracked in a real implementation
                'success_rate': 0      # This would be tracked in a real implementation
            }
            agents.append(agent_info)
        
        return jsonify({'agents': agents})
    except Exception as e:
        logging.error(f"Error fetching agents: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@api_blueprint.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get details of a specific agent."""
    try:
        agent = agent_manager.get_agent(agent_id)
        if agent:
            agent_info = {
                'id': agent_id,
                'type': agent.__class__.__name__,
                'status': 'active' if hasattr(agent, 'is_active') and agent.is_active else 'inactive',
                'config': getattr(agent, 'config', {}),
                'tasks_processed': 0,  # This would be tracked in a real implementation
                'success_rate': 0      # This would be tracked in a real implementation
            }
            return jsonify(agent_info)
        return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        logging.error(f"Error fetching agent {agent_id}: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@api_blueprint.route('/agents/<agent_id>/activate', methods=['POST'])
def activate_agent(agent_id):
    """Activate an agent."""
    try:
        agent = agent_manager.get_agent(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
            
        # Set the agent as active
        if hasattr(agent, 'is_active'):
            agent.is_active = True
            return jsonify({'success': True})
        return jsonify({'error': 'Agent does not support activation'}), 400
    except Exception as e:
        logging.error(f"Error activating agent {agent_id}: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@api_blueprint.route('/agents/<agent_id>/deactivate', methods=['POST'])
def deactivate_agent(agent_id):
    """Deactivate an agent."""
    try:
        agent = agent_manager.get_agent(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
            
        # Set the agent as inactive
        if hasattr(agent, 'is_active'):
            agent.is_active = False
            return jsonify({'success': True})
        return jsonify({'error': 'Agent does not support deactivation'}), 400
    except Exception as e:
        logging.error(f"Error deactivating agent {agent_id}: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@api_blueprint.route('/chat', methods=['POST'])
def process_chat():
    """Process a chat message using the appropriate agent."""
    try:
        data = request.json
        if not data or 'message' not in data or 'agent' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        message = data['message']
        agent_type = data['agent']
        
        # Get the appropriate agent
        agent = None
        if agent_type == 'nlp':
            agent = agent_manager.get_agent('nlp')
        elif agent_type == 'code':
            agent = agent_manager.get_agent('code')
        elif agent_type == 'vision':
            agent = agent_manager.get_agent('vision')
        elif agent_type == 'web':
            agent = agent_manager.get_agent('web')
        elif agent_type == 'data':
            agent = agent_manager.get_agent('data')
        elif agent_type == 'planning':
            agent = agent_manager.get_agent('planning')
        
        if not agent:
            return jsonify({'error': f'Agent {agent_type} not available'}), 404
            
        # Create a task for the agent
        task_data = {
            'id': f'chat_{int(time.time())}',
            'task_type': 'chat',
            'data': {
                'message': message,
                'agent_type': agent_type
            },
            'status': 'pending'
        }
        
        # In a real implementation, this would be processed asynchronously
        # For now, we'll just return a simulated response
        response = f"I'll process your request using the {agent_type} agent. Your message: {message}"
        
        return jsonify({
            'response': response,
            'task_id': task_data['id']
        })
    except Exception as e:
        logging.error(f"Error processing chat: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@api_blueprint.route('/settings', methods=['GET'])
def get_settings():
    """Get system settings."""
    try:
        # In a real implementation, these would be loaded from a database or config file
        settings = {
            'general': {
                'system_name': 'Tío Pepe',
                'log_level': 'info'
            },
            'api': {
                'url': 'http://localhost:5000',
                'key': '••••••••••••••••'  # Masked for security
            },
            'agents': {
                'timeout': 30,
                'max_concurrent': 5
            }
        }
        return jsonify(settings)
    except Exception as e:
        logging.error(f"Error fetching settings: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

def initialize_agents():
    """Initialize all specialized agents."""
    try:
        # Create and register all specialized agents
        nlp_agent = NLPAgent()
        agent_manager.register_agent('nlp', nlp_agent)
        
        vision_agent = VisionAgent()
        agent_manager.register_agent('vision', vision_agent)
        
        web_agent = WebAgent()
        agent_manager.register_agent('web', web_agent)
        
        data_agent = DataAgent()
        agent_manager.register_agent('data', data_agent)
        
        code_agent = CodeAgent()
        agent_manager.register_agent('code', code_agent)
        
        planning_agent = PlanningAgent()
        agent_manager.register_agent('planning', planning_agent)
        
        logging.info("All specialized agents initialized")
    except Exception as e:
        logging.error(f"Error initializing agents: {str(e)}\\n{traceback.format_exc()}")

# Initialize agents when the blueprint is loaded
initialize_agents()