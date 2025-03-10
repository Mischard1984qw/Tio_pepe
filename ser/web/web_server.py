"""Flask web server for the Tío Pepe system."""

from flask import Flask, render_template, jsonify, request, abort
import logging
import os
from config.config import get_config
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import traceback
from core.orchestrator import Orchestrator
from agents.agent_zero import AgentZero

def create_app(orchestrator=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    CORS(app)
    config = get_config()
    logger = logging.getLogger(__name__)

    # If no orchestrator is provided, create one
    if orchestrator is None:
        orchestrator = Orchestrator()

    # Create the main coordinating agent
    agent_zero = AgentZero()

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors by rendering the 404 template."""
        logger.warning(f"404 error: {request.path}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors by rendering the 500 template."""
        logger.error(f"500 error: {str(e)}\\n{traceback.format_exc()}")
        return render_template('500.html'), 500

    @app.errorhandler(Exception)
    def handle_error(error):
        """Handle all other exceptions."""
        logger.error(f"Error: {error}\\n{traceback.format_exc()}")
        if isinstance(error, HTTPException):
            return jsonify({'error': str(error)}), error.code
        return render_template('500.html'), 500

    # Configure the app
    app.config.update(
        SECRET_KEY=config.get('api', {}).get('secret_key', 'dev-key'),
        DEBUG=config.get('api', {}).get('debug', True)
    )

    # Register routes
    @app.route('/')
    def index():
        """Render the main dashboard page."""
        return render_template('index.html')

    @app.route('/tasks')
    def tasks():
        """Display task management interface."""
        return render_template('tasks.html')

    @app.route('/agents')
    def agents():
        """Display agent management interface."""
        return render_template('agents.html')

    @app.route('/chat')
    def chat():
        """Display chat interface."""
        return render_template('chat.html')

    @app.route('/settings')
    def settings():
        """Display settings interface."""
        return render_template('settings.html')

    # API endpoint for chat
    @app.route('/api/chat', methods=['POST'])
    def process_chat():
        """Process chat messages and return responses."""
        if not orchestrator:
            return jsonify({'error': 'Orchestrator not available'}), 503
        
        data = request.get_json()
        if not data or 'message' not in data or 'agent' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        try:
            # Create a task for the chat message
            task_data = {
                'type': 'chat',
                'agent': data['agent'],
                'message': data['message']
            }
            
            # Create a task using agent_zero
            task = agent_zero.create_task('chat', task_data)
            
            # For simple responses, return immediately
            initial_response = f"I'll process your request using the {data['agent']} agent."
            
            return jsonify({
                'response': initial_response,
                'task_id': task.id
            })
        except Exception as e:
            logger.error(f"Error processing chat: {e}\\n{traceback.format_exc()}")
            return jsonify({'error': 'Failed to process chat message'}), 500

    # API endpoints for dashboard
    @app.route('/api/dashboard/metrics', methods=['GET'])
    def get_dashboard_metrics():
        """Get metrics for the dashboard."""
        try:
            if orchestrator:
                metrics = {
                    'active_tasks': len([t for t in agent_zero.tasks if t.status == 'pending']),
                    'active_agents': len(agent_zero.specialized_agents),
                    'system_status': 'healthy'  # This would be determined by system health checks
                }
                return jsonify(metrics)
            return jsonify({
                'active_tasks': 0,
                'active_agents': 0,
                'system_status': 'unknown'
            })
        except Exception as e:
            logger.error(f"Error fetching dashboard metrics: {e}\\n{traceback.format_exc()}")
            return jsonify({'error': 'Failed to fetch metrics'}), 500

    @app.route('/api/activity', methods=['GET'])
    def get_activity():
        """Get recent system activity."""
        try:
            # In a real implementation, this would be loaded from a database or log
            activities = [
                {
                    'timestamp': 1709956800,  # Example timestamp
                    'description': 'System started'
                },
                {
                    'timestamp': 1709956830,
                    'description': 'Agents initialized'
                },
                {
                    'timestamp': 1709956860,
                    'description': 'Web server started'
                }
            ]
            return jsonify({'activities': activities})
        except Exception as e:
            logger.error(f"Error fetching activities: {e}\\n{traceback.format_exc()}")
            return jsonify({'error': 'Failed to fetch activities'}), 500

    # Configure static file serving
    app.static_folder = 'static'
    app.static_url_path = '/static'

    # Register blueprints
    from web.routes import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Pass the orchestrator to the blueprint
    api_blueprint.orchestrator = orchestrator

    return app

def start_server():
    """Start the Flask web server."""
    try:
        # Create a single orchestrator instance to be used throughout the app
        orchestrator = Orchestrator()
        app = create_app(orchestrator)
        
        # Ensure template and static directories exist
        os.makedirs('web/templates', exist_ok=True)
        os.makedirs('web/static/css', exist_ok=True)
        os.makedirs('web/static/js', exist_ok=True)
        
        config = get_config()
        host = config['api']['base_url'].split('://')[1].split(':')[0]
        port = int(config['api']['base_url'].split(':')[-1])
        
        logger = logging.getLogger(__name__)
        logger.info(f"Starting Tío Pepe web server at {host}:{port}")
        
        app.run(host=host, port=port)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to start web server: {str(e)}\\n{traceback.format_exc()}")
        raise

if __name__ == '__main__':
    start_server()