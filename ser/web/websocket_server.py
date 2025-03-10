"""WebSocket server for real-time communication in Tío Pepe system."""

from flask_socketio import SocketIO, emit
from typing import Dict, Any
import logging
import json
from config.redis_config import RedisCache

logger = logging.getLogger(__name__)
socketio = SocketIO()
cache = RedisCache()

# Store active connections
active_connections: Dict[str, Any] = {}

@socketio.on('connect')
async def handle_connect():
    """Handle new WebSocket connections."""
    try:
        client_id = request.sid
        connection_data = {
            'connected_at': time.time(),
            'agent_subscriptions': [],
            'last_heartbeat': time.time(),
            'status': 'active',
            'client_info': request.headers.get('User-Agent', 'Unknown')
        }
        
        active_connections[client_id] = connection_data
        
        # Store connection info in Redis with 24h TTL
        await cache.set(
            f'connection:{client_id}',
            connection_data,
            ttl=86400  # 24 hours
        )
        
        await emit('connection_established', {
            'client_id': client_id,
            'server_time': time.time(),
            'heartbeat_interval': 30  # Send heartbeat every 30 seconds
        })
        
        logger.info(f'New WebSocket connection established: {client_id}')
    except Exception as e:
        logger.error(f'Connection error: {str(e)}\n{traceback.format_exc()}')
        await emit('connection_error', {
            'error': str(e),
            'code': 'CONNECTION_ERROR'
        })

@socketio.on('disconnect')
async def handle_disconnect():
    """Handle WebSocket disconnections."""
    try:
        client_id = request.sid
        if client_id in active_connections:
            # Clean up Redis cache
            await cache.delete(f'connection:{client_id}')
            del active_connections[client_id]
            
        logger.info(f'WebSocket disconnected: {client_id}')
    except Exception as e:
        logger.error(f'Error in handle_disconnect: {str(e)}')

@socketio.on('subscribe_agent')
def handle_agent_subscription(data):
    """Handle agent subscription requests."""
    try:
        client_id = request.sid
        agent_id = data.get('agent_id')
        
        if not agent_id:
            emit('subscription_error', {'error': 'No agent_id provided'})
            return
            
        if client_id in active_connections:
            if agent_id not in active_connections[client_id]['agent_subscriptions']:
                active_connections[client_id]['agent_subscriptions'].append(agent_id)
                emit('subscription_success', {
                    'agent_id': agent_id,
                    'message': f'Successfully subscribed to agent {agent_id}'
                })
    except Exception as e:
        logger.error(f'Error in handle_agent_subscription: {str(e)}')
        emit('subscription_error', {'error': str(e)})

async def broadcast_agent_update(agent_id: str, update_data: Dict[str, Any]):
    """Broadcast agent updates to subscribed clients."""
    try:
        # Cache the update data
        cache_key = f'agent_update:{agent_id}:{time.time()}'
        await cache.set(cache_key, update_data, ttl=300)  # Cache for 5 minutes
        
        for client_id, connection in active_connections.items():
            if agent_id in connection['agent_subscriptions']:
                try:
                    await emit('agent_update', {
                        'agent_id': agent_id,
                        'data': update_data,
                        'timestamp': time.time()
                    }, room=client_id)
                except Exception as client_error:
                    logger.error(f'Error broadcasting to client {client_id}: {str(client_error)}')
                    continue
    except Exception as e:
        logger.error(f'Error in broadcast_agent_update: {str(e)}')

@socketio.on('unsubscribe_agent')
def handle_agent_unsubscription(data):
    """Handle agent unsubscription requests."""
    try:
        client_id = request.sid
        agent_id = data.get('agent_id')
        
        if not agent_id:
            emit('unsubscription_error', {'error': 'No agent_id provided'})
            return
            
        if client_id in active_connections:
            if agent_id in active_connections[client_id]['agent_subscriptions']:
                active_connections[client_id]['agent_subscriptions'].remove(agent_id)
                emit('unsubscription_success', {
                    'agent_id': agent_id,
                    'message': f'Successfully unsubscribed from agent {agent_id}'
                })
    except Exception as e:
        logger.error(f'Error in handle_agent_unsubscription: {str(e)}')
        emit('unsubscription_error', {'error': str(e)})

async def broadcast_agent_update(agent_id: str, update_data: Dict[str, Any]):
    """Broadcast agent updates to subscribed clients."""
    try:
        # Cache the update data
        cache_key = f'agent_update:{agent_id}:{time.time()}'
        await cache.set(cache_key, update_data, ttl=300)  # Cache for 5 minutes
        
        for client_id, connection in active_connections.items():
            if agent_id in connection['agent_subscriptions']:
                try:
                    await emit('agent_update', {
                        'agent_id': agent_id,
                        'data': update_data,
                        'timestamp': time.time()
                    }, room=client_id)
                except Exception as client_error:
                    logger.error(f'Error broadcasting to client {client_id}: {str(client_error)}')
                    continue
    except Exception as e:
        logger.error(f'Error in broadcast_agent_update: {str(e)}')

def broadcast_task_update(task_id: str, update_data: Dict[str, Any]):
    """Broadcast task updates to all connected clients."""
    try:
        emit('task_update', {
            'task_id': task_id,
            'data': update_data
        }, broadcast=True)
    except Exception as e:
        logger.error(f'Error in broadcast_task_update: {str(e)}')

def initialize_websocket(app):
    """Initialize WebSocket server with Flask app."""
    try:
        socketio.init_app(
            app,
            cors_allowed_origins="*",
            async_mode='gevent',
            logger=True,
            engineio_logger=True
        )
        logger.info('WebSocket server initialized successfully')
        return socketio
    except Exception as e:
        logger.error(f'Error initializing WebSocket server: {str(e)}')
        raise