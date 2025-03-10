# Tío Pepe System Documentation

## System Overview

Tío Pepe is a modular agent-based system designed for processing various types of tasks through specialized agents. The system architecture follows a microservices-like pattern where each agent handles specific types of tasks.

### Core Components

#### Agent Zero (Main Coordinator)
The central coordinator (`AgentZero`) manages task distribution and execution across specialized agents. It handles:
- Task creation and routing
- Agent registration
- Task status tracking

#### Agent Manager
Manages the lifecycle of specialized agents including:
- Agent configuration management
- Agent initialization
- Resource cleanup

#### Specialized Agents

1. **Code Agent**
   - Code generation and optimization
   - Code analysis and metrics
   - Support for Python, JavaScript, TypeScript, and Java

2. **Data Agent**
   - Data processing and analysis
   - Statistical calculations
   - Data transformation

3. **NLP Agent**
   - Sentiment analysis
   - Text generation
   - Text classification

4. **Planning Agent**
   - Workflow management
   - Task dependency handling
   - Progress tracking

5. **Vision Agent**
   - Image processing
   - Object detection
   - Face detection
   - Image classification

## Installation Guide

### Prerequisites
- Python 3.7+
- Docker (optional, for containerized deployment)

### Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd tio-pepe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t tio-pepe .
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

## Configuration

### Agent Configuration
Agent configurations are managed through YAML files in the `config` directory:

```yaml
# Example agent configuration
agents:
  code_agent:
    enabled: true
    config:
      supported_languages: ["python", "javascript", "typescript", "java"]
```

### System Configuration
Core system settings are configured in `config/config.py`.

## API Documentation

### Task Management

#### Create Task
```python
task = agent_zero.create_task(
    task_type="code",
    task_data={
        "code_type": "optimize",
        "code": code_content,
        "language": "python"
    }
)
```

#### Check Task Status
```python
status = agent_zero.get_task_status(task_id)
```

### Agent Integration

#### Register New Agent
```python
agent_manager.register_agent_config(AgentConfig(
    type="custom",
    name="CustomAgent",
    enabled=True,
    config={}
))
```

## Development Guide

### Adding New Agents

1. Create a new agent class in `agents/specialized_agents/`
2. Implement the required interface:
   - `__init__(self, config: Dict[str, Any])`
   - `process_task(self, task: Any) -> Dict[str, Any]`
   - `cleanup(self) -> None`
3. Register the agent in `agent_manager.py`

### Error Handling

Implement proper error handling using try-except blocks and logging:

```python
try:
    result = agent.process_task(task)
except Exception as e:
    logger.error(f"Task processing error: {str(e)}")
    raise
```

### Logging

Use the built-in logging system:

```python
from logging import getLogger
logger = getLogger(__name__)

logger.info("Processing task...")
logger.error("Error occurred: %s", str(error))
```

## Performance Optimization

### Memory Management
- Implement cleanup methods for agents
- Use context managers for resource handling
- Monitor memory usage with `performance_monitor.py`

### Concurrency
- Use async/await for I/O-bound operations
- Implement proper task queuing
- Handle resource contention

## Security Considerations

### Authentication
- Configure authentication in `config/auth_config.yaml`
- Implement API key validation
- Use secure session management

### Data Protection
- Sanitize input data
- Implement proper access controls
- Handle sensitive data securely

## Troubleshooting

### Common Issues

1. Agent Initialization Failures
   - Check configuration files
   - Verify dependencies
   - Review error logs

2. Task Processing Errors
   - Validate input data
   - Check agent status
   - Review task configuration

### Logging and Monitoring

- Logs are stored in `logs/system.log`
- Monitor system performance using `tools/performance_monitor.py`
- Review web server access logs for API issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## License

[Add License Information]

## Contact

[Add Contact Information]