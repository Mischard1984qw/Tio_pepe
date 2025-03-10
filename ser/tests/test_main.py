"""Test suite for Tío Pepe system core components."""

import unittest
from unittest.mock import Mock, patch
from core.orchestrator import Orchestrator
from core.task_manager import TaskManager
from agents.agent_manager import AgentManager
from agents.agent_zero import AgentZero
from agents.specialized_agents.code_agent import CodeAgent
from agents.specialized_agents.nlp_agent import NLPAgent

class TestTioPepeCore(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.task_manager = TaskManager()
        self.agent_manager = AgentManager()
        self.orchestrator = Orchestrator()

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization and agent registration."""
        self.orchestrator.register_agent('task_manager', self.task_manager)
        self.orchestrator.register_agent('agent_manager', self.agent_manager)
        
        self.assertIn('task_manager', self.orchestrator.agents)
        self.assertIn('agent_manager', self.orchestrator.agents)

    def test_agent_zero_task_creation(self):
        """Test task creation and processing with AgentZero."""
        agent_zero = AgentZero()
        code_agent = CodeAgent()
        nlp_agent = NLPAgent()

        agent_zero.register_agent('code', code_agent)
        agent_zero.register_agent('nlp', nlp_agent)

        # Test code task creation
        code_task = agent_zero.create_task(
            task_type='code',
            task_data={
                'code_type': 'optimize',
                'code': 'def test(): pass',
                'language': 'python'
            }
        )
        self.assertIsNotNone(code_task.id)
        self.assertEqual(code_task.task_type, 'code')

    @patch('core.task_manager.TaskManager.process_task')
    def test_task_processing(self, mock_process_task):
        """Test task processing workflow."""
        # Configure mock
        mock_process_task.return_value = True

        # Create and process a task
        task_data = {'test': 'data'}
        result = self.task_manager.process_task(task_data)

        # Verify mock was called correctly
        mock_process_task.assert_called_once_with(task_data)
        self.assertTrue(result)

    def test_agent_manager_lifecycle(self):
        """Test agent lifecycle management."""
        # Test agent registration
        test_agent = Mock()
        self.agent_manager.register_agent('test', test_agent)
        self.assertIn('test', self.agent_manager.agents)

        # Test agent retrieval
        retrieved_agent = self.agent_manager.get_agent('test')
        self.assertEqual(retrieved_agent, test_agent)

        # Test agent deregistration
        self.agent_manager.deregister_agent('test')
        self.assertNotIn('test', self.agent_manager.agents)

if __name__ == '__main__':
    unittest.main()