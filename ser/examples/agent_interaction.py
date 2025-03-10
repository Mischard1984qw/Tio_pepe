"""Example script demonstrating how to interact with Tío Pepe system agents."""

from agents.agent_zero import AgentZero, Task
from agents.specialized_agents.code_agent import CodeAgent
from agents.specialized_agents.vision_agent import VisionAgent
from agents.specialized_agents.nlp_agent import NLPAgent
from agents.specialized_agents.data_agent import DataAgent
from agents.specialized_agents.planning_agent import PlanningAgent

def main():
    # Initialize the main coordinating agent
    agent_zero = AgentZero()
    
    # Register specialized agents
    agent_zero.register_agent('code', CodeAgent())
    agent_zero.register_agent('vision', VisionAgent())
    agent_zero.register_agent('nlp', NLPAgent())
    agent_zero.register_agent('data', DataAgent())
    agent_zero.register_agent('planning', PlanningAgent())
    
    # Example 1: Code optimization task
    code_task = agent_zero.create_task(
        task_type='code',
        task_data={
            'code_type': 'optimize',
            'code': 'def hello_world():\n    print("Hello, World!")',
            'language': 'python'
        }
    )
    
    # Example 2: NLP sentiment analysis task
    nlp_task = agent_zero.create_task(
        task_type='nlp',
        task_data={
            'nlp_type': 'sentiment',
            'text': 'I love working with this amazing system!'
        }
    )
    
    # Example 3: Vision object detection task
    vision_task = agent_zero.create_task(
        task_type='vision',
        task_data={
            'vision_type': 'object_detection',
            'image_path': 'path/to/image.jpg'
        }
    )
    
    # Process all tasks
    agent_zero.process_tasks()
    
    # Check task statuses
    print(f"Code task status: {agent_zero.get_task_status(code_task.id)}")
    print(f"NLP task status: {agent_zero.get_task_status(nlp_task.id)}")
    print(f"Vision task status: {agent_zero.get_task_status(vision_task.id)}")

if __name__ == '__main__':
    main()