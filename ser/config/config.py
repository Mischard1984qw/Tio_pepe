"""General system configuration module for Tío Pepe."""

import os
from pathlib import Path
from typing import Dict, Any

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / 'config'
MODELS_DIR = BASE_DIR / 'models'

# API configurations
API_CONFIG = {
    'base_url': os.getenv('TIO_PEPE_API_URL', 'http://localhost:8000'),
    'version': 'v1',
    'timeout': int(os.getenv('TIO_PEPE_API_TIMEOUT', '30')),
    'retry_attempts': int(os.getenv('TIO_PEPE_API_RETRIES', '3'))
}

# Model configurations
MODEL_CONFIG = {
    'vision_model': os.getenv('TIO_PEPE_VISION_MODEL', 'default_vision_model'),
    'nlp_model': os.getenv('TIO_PEPE_NLP_MODEL', 'default_nlp_model'),
    'code_model': os.getenv('TIO_PEPE_CODE_MODEL', 'default_code_model'),
    'model_cache_dir': str(MODELS_DIR / 'cache')
}

# Ollama Configuration
OLLAMA_CONFIG = {
    'api_url': os.getenv('OLLAMA_API_URL', 'http://localhost:11434'),
    'model': os.getenv('OLLAMA_MODEL', 'llama2'),
    'timeout': int(os.getenv('OLLAMA_TIMEOUT', '30')),
    'max_tokens': int(os.getenv('OLLAMA_MAX_TOKENS', '2048')),
    'temperature': float(os.getenv('OLLAMA_TEMPERATURE', '0.7'))
}

# LM Studio Configuration
LM_STUDIO_CONFIG = {
    'api_url': os.getenv('LM_STUDIO_API_URL', 'http://localhost:1234/v1'),
    'model_path': os.getenv('LM_STUDIO_MODEL_PATH', '/models/local'),
    'timeout': int(os.getenv('LM_STUDIO_TIMEOUT', '30')),
    'max_tokens': int(os.getenv('LM_STUDIO_MAX_TOKENS', '2048')),
    'temperature': float(os.getenv('LM_STUDIO_TEMPERATURE', '0.7'))
}

# Logging configuration
LOGGING_CONFIG = {
    'level': os.getenv('TIO_PEPE_LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_dir': str(BASE_DIR / 'logs')
}

# Agent configurations
AGENT_CONFIG = {
    'max_concurrent_tasks': int(os.getenv('TIO_PEPE_MAX_TASKS', '10')),
    'task_timeout': int(os.getenv('TIO_PEPE_TASK_TIMEOUT', '300')),
    'enable_async': os.getenv('TIO_PEPE_ASYNC_ENABLED', 'true').lower() == 'true'
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary."""
    return {
        'api': API_CONFIG,
        'model': MODEL_CONFIG,
        'logging': LOGGING_CONFIG,
        'agent': AGENT_CONFIG,
        'ollama': OLLAMA_CONFIG,
        'lm_studio': LM_STUDIO_CONFIG
    }

def get_api_config() -> Dict[str, Any]:
    """Get API-specific configuration."""
    return API_CONFIG

def get_model_config() -> Dict[str, Any]:
    """Get model-specific configuration."""
    return MODEL_CONFIG

def get_logging_config() -> Dict[str, Any]:
    """Get logging-specific configuration."""
    return LOGGING_CONFIG

def get_agent_config() -> Dict[str, Any]:
    """Get agent-specific configuration."""
    return AGENT_CONFIG