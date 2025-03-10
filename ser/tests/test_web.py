"""Test suite for Tío Pepe system web interface."""

import unittest
from flask import url_for
from web.web_server import create_app
from core.orchestrator import Orchestrator

class TestWebInterface(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.orchestrator = Orchestrator()
        self.app = create_app(self.orchestrator)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after each test method."""
        self.app_context.pop()

    def test_index_page(self):
        """Test dashboard page rendering."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'System Dashboard', response.data)
        self.assertIn(b'Active Tasks', response.data)
        self.assertIn(b'Active Agents', response.data)

    def test_tasks_page(self):
        """Test tasks page rendering."""
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task Management', response.data)
        self.assertIn(b'New Task', response.data)

    def test_agents_page(self):
        """Test agents page rendering."""
        response = self.client.get('/agents')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Agent Management', response.data)
        self.assertIn(b'NLP Agent', response.data)
        self.assertIn(b'Vision Agent', response.data)

    def test_chat_page(self):
        """Test chat interface page rendering."""
        response = self.client.get('/chat')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Chat Interface', response.data)

    def test_navigation_links(self):
        """Test navigation links between pages."""
        response = self.client.get('/')
        self.assertIn(b'/tasks', response.data)
        self.assertIn(b'/agents', response.data)
        self.assertIn(b'/chat', response.data)

if __name__ == '__main__':
    unittest.main()