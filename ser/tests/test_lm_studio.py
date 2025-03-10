"""Test suite for LM Studio integration."""

import pytest
import asyncio
from tools.llm_client import LLMClient
from unittest.mock import patch, AsyncMock
from config.config import LM_STUDIO_CONFIG

@pytest.fixture
def llm_client():
    """Create a LLMClient instance for testing."""
    client = LLMClient()
    client.switch_service('lm_studio')
    return client

@pytest.mark.asyncio
async def test_lm_studio_text_generation(llm_client):
    """Test successful text generation with LM Studio."""
    test_prompt = "What is the capital of France?"
    expected_response = {"choices": [{"text": "The capital of France is Paris."}]}
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = expected_response
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await llm_client.generate_text(test_prompt)
        assert result == expected_response["choices"][0]["text"]

@pytest.mark.asyncio
async def test_lm_studio_error_handling(llm_client):
    """Test error handling when LM Studio service fails."""
    test_prompt = "Test prompt"
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await llm_client.generate_text(test_prompt)
        assert result is None

@pytest.mark.asyncio
async def test_lm_studio_timeout(llm_client):
    """Test timeout handling in LM Studio requests."""
    test_prompt = "Test prompt"
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.side_effect = asyncio.TimeoutError
        
        result = await llm_client.generate_text(test_prompt)
        assert result is None

@pytest.mark.asyncio
async def test_lm_studio_config(llm_client):
    """Test LM Studio configuration parameters."""
    test_prompt = "Test prompt"
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"choices": [{"text": "Test response"}]}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        await llm_client.generate_text(test_prompt)
        
        # Verify the API call parameters
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs['timeout'] == LM_STUDIO_CONFIG['timeout']
        assert call_kwargs['json']['max_tokens'] == LM_STUDIO_CONFIG['max_tokens']
        assert call_kwargs['json']['temperature'] == LM_STUDIO_CONFIG['temperature']