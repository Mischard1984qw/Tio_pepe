"""Test suite for WebSocket server functionality."""

import unittest
from unittest.mock import Mock, patch
from web.websocket_server import initialize_websocket, handle_connect, handle_disconnect
from web.websocket_server import handle_agent_subscription, handle_agent_unsubscription
from web.websocket_server import broadcast_agent_update, broadcast_task_update
from flask import Flask
from flask_socketio import SocketIO

class TestWebSocketServer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.socketio = initialize_websocket(self.app)
        self.client = self.socketio.test_client(self.app)

    def tearDown(self):
        """Clean up after each test method."""
        self.client.disconnect()

    def test_connection_handling(self):
        """Test WebSocket connection and disconnection."""
        client = self.socketio.test_client(self.app)
        self.assertTrue(client.is_connected())
        
        client.disconnect()
        self.assertFalse(client.is_connected())

    def test_agent_subscription(self):
        """Test agent subscription functionality."""
        client = self.socketio.test_client(self.app)
        
        # Test successful subscription
        client.emit('subscribe_agent', {'agent_id': 'test_agent'})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'subscription_success')
        
        # Test subscription without agent_id
        client.emit('subscribe_agent', {})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'subscription_error')

    def test_agent_unsubscription(self):
        """Test agent unsubscription functionality."""
        client = self.socketio.test_client(self.app)
        
        # Subscribe first
        client.emit('subscribe_agent', {'agent_id': 'test_agent'})
        client.get_received()
        
        # Test successful unsubscription
        client.emit('unsubscribe_agent', {'agent_id': 'test_agent'})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'unsubscription_success')
        
        # Test unsubscription without agent_id
        client.emit('unsubscribe_agent', {})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'unsubscription_error')

    @patch('web.websocket_server.emit')
    def test_broadcast_agent_update(self, mock_emit):
        """Test broadcasting agent updates."""
        update_data = {'status': 'processing'}
        broadcast_agent_update('test_agent', update_data)
        mock_emit.assert_called_with(
            'agent_update',
            {
                'agent_id': 'test_agent',
                'data': update_data,
                'timestamp': unittest.mock.ANY
            },
            room=unittest.mock.ANY
        )

    @patch('web.websocket_server.emit')
    def test_broadcast_task_update(self, mock_emit):
        """Test broadcasting task updates."""
        update_data = {'status': 'completed'}
        broadcast_task_update('test_task', update_data)
        mock_emit.assert_called_with(
            'task_update',
            {
                'task_id': 'test_task',
                'data': update_data
            },
            broadcast=True
        )

    def test_error_handling(self):
        """Test error handling in WebSocket operations."""
        client = self.socketio.test_client(self.app)
        
        # Test invalid subscription data
        client.emit('subscribe_agent', {'invalid_key': 'value'})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'subscription_error')

if __name__ == '__main__':
    unittest.main()