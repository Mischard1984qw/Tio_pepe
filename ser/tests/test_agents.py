"""Test suite for specialized agents in Tío Pepe system."""

import unittest
from unittest.mock import Mock, patch
from agents.specialized_agents.code_agent import CodeAgent
from agents.specialized_agents.nlp_agent import NLPAgent
from agents.specialized_agents.vision_agent import VisionAgent
from agents.specialized_agents.data_agent import DataAgent
from agents.specialized_agents.planning_agent import PlanningAgent

class TestSpecializedAgents(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.code_agent = CodeAgent()
        self.nlp_agent = NLPAgent()
        self.vision_agent = VisionAgent()
        self.data_agent = DataAgent()
        self.planning_agent = PlanningAgent()

    def test_code_agent(self):
        """Test code agent functionality."""
        test_code = 'def test(): return True'
        result = self.code_agent.process_task({
            'code_type': 'analyze',
            'code': test_code,
            'language': 'python'
        })
        self.assertIsNotNone(result)

    def test_nlp_agent(self):
        """Test NLP agent functionality."""
        test_text = 'This is a test sentence.'
        result = self.nlp_agent.process_task({
            'nlp_type': 'analyze',
            'text': test_text
        })
        self.assertIsNotNone(result)

    @patch('agents.specialized_agents.vision_agent.VisionAgent.process_image')
    def test_vision_agent(self, mock_process_image):
        """Test vision agent functionality."""
        mock_process_image.return_value = {'objects': ['test_object']}
        result = self.vision_agent.process_task({
            'vision_type': 'detect_objects',
            'image_path': 'test_image.jpg'
        })
        self.assertIsNotNone(result)
        mock_process_image.assert_called_once()

    def test_data_agent(self):
        """Test data agent functionality."""
        test_data = [1, 2, 3, 4, 5]
        result = self.data_agent.process_task({
            'data_type': 'analyze',
            'data': test_data
        })
        self.assertIsNotNone(result)

    def test_planning_agent(self):
        """Test planning agent functionality."""
        test_workflow = {
            'tasks': [
                {'id': 1, 'name': 'Task 1'},
                {'id': 2, 'name': 'Task 2'}
            ]
        }
        result = self.planning_agent.process_task({
            'planning_type': 'create_workflow',
            'workflow': test_workflow
        })
        self.assertIsNotNone(result)

    def test_agent_error_handling(self):
        """Test error handling in agents."""
        with self.assertRaises(ValueError):
            self.code_agent.process_task({
                'invalid_key': 'invalid_value'
            })

        with self.assertRaises(ValueError):
            self.nlp_agent.process_task({
                'invalid_key': 'invalid_value'
            })

if __name__ == '__main__':
    unittest.main()