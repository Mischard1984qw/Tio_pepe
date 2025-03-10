# Tío Pepe API Documentation

## Overview

This document provides detailed API documentation for the Tío Pepe system, including all available endpoints, request/response formats, and examples.

## Agent Zero API

### Task Management

#### Create Task

```python
POST /api/tasks

Request:
{
    "task_type": "code",  # Type of specialized agent to handle the task
    "task_data": {
        "code_type": "optimize",  # Specific operation for the agent
        "code": "code_content",    # Content to process
        "language": "python"      # Additional parameters
    }
}

Response:
{
    "task_id": "task_123",
    "status": "pending",
    "created_at": "2024-01-01T12:00:00Z"
}
```

#### Get Task Status

```python
GET /api/tasks/{task_id}

Response:
{
    "task_id": "task_123",
    "status": "completed",
    "result": {
        "success": true,
        "data": {}
    }
}
```

## Specialized Agent APIs

### Code Agent

#### Optimize Code

```python
POST /api/code/optimize

Request:
{
    "code": "def example(): pass",
    "language": "python"
}

Response:
{
    "optimized_code": "def example():\n    pass\n",
    "metrics": {
        "original_length": 20,
        "optimized_length": 22
    }
}
```

#### Analyze Code

```python
POST /api/code/analyze

Request:
{
    "code": "code_content",
    "language": "python"
}

Response:
{
    "analysis_results": {
        "metrics": {
            "total_lines": 10,
            "code_lines": 8,
            "comment_lines": 1,
            "blank_lines": 1
        },
        "complexity": {
            "num_functions": 2,
            "num_classes": 1,
            "max_depth": 3
        },
        "style_issues": [],
        "potential_bugs": []
    }
}
```

### Data Agent

#### Analyze Data

```python
POST /api/data/analyze

Request:
{
    "data": [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20}
    ]
}

Response:
{
    "analysis_results": {
        "shape": [2, 2],
        "columns": ["id", "value"],
        "data_types": {
            "id": "int64",
            "value": "int64"
        },
        "missing_values": {}
    }
}
```

### NLP Agent

#### Sentiment Analysis

```python
POST /api/nlp/sentiment

Request:
{
    "text": "This is a great product!"
}

Response:
{
    "sentiment": {
        "label": "POSITIVE",
        "score": 0.95
    }
}
```

### Vision Agent

#### Object Detection

```python
POST /api/vision/detect-objects

Request:
{
    "image_path": "/path/to/image.jpg"
}

Response:
{
    "objects": [
        {
            "x": 100,
            "y": 200,
            "width": 50,
            "height": 50,
            "class": "person",
            "confidence": 0.92
        }
    ]
}
```

## Error Handling

### Error Response Format

```python
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Detailed error message",
        "details": {}
    }
}
```

### Common Error Codes

- `INVALID_REQUEST`: Invalid request format or parameters
- `TASK_NOT_FOUND`: Requested task ID does not exist
- `AGENT_ERROR`: Error in specialized agent processing
- `UNAUTHORIZED`: Authentication failure
- `RATE_LIMITED`: Too many requests

## Authentication

### API Key Authentication

```python
Headers:
{
    "X-API-Key": "your-api-key-here"
}
```

### JWT Authentication

```python
Headers:
{
    "Authorization": "Bearer your-jwt-token-here"
}
```

## Rate Limiting

- Default rate limit: 100 requests per minute
- Rate limit headers:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time until limit resets

## Webhooks

### Task Completion Webhook

```python
POST {webhook_url}

Payload:
{
    "event": "task.completed",
    "task_id": "task_123",
    "result": {
        "success": true,
        "data": {}
    }
}
```

## SDK Examples

### Python SDK

```python
from tio_pepe import Client

client = Client(api_key="your-api-key")

# Create and process a task
task = client.create_task(
    task_type="code",
    task_data={
        "code_type": "optimize",
        "code": code_content,
        "language": "python"
    }
)

# Check task status
status = client.get_task_status(task.id)
```

### JavaScript SDK

```javascript
const TioPepe = require('tio-pepe');

const client = new TioPepe({
    apiKey: 'your-api-key'
});

// Create and process a task
const task = await client.createTask({
    taskType: 'code',
    taskData: {
        codeType: 'optimize',
        code: codeContent,
        language: 'python'
    }
});

// Check task status
const status = await client.getTaskStatus(task.id);
```