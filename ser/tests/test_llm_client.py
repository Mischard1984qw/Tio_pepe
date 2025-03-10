"""Test suite for LLM client integration with Ollama."""

import pytest
import asyncio
from tools.llm_client import LLMClient
from unittest.mock import patch, AsyncMock

@pytest.fixture
def llm_client():
    """Create a LLMClient instance for testing."""
    return LLMClient()

@pytest.mark.asyncio
async def test_ollama_text_generation(llm_client):
    """Test successful text generation with Ollama."""
    test_prompt = "What is the capital of France?"
    expected_response = {"response": "The capital of France is Paris."}
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = expected_response
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await llm_client.generate_text(test_prompt)
        assert result == expected_response["response"]

@pytest.mark.asyncio
async def test_ollama_error_handling(llm_client):
    """Test error handling when Ollama service fails."""
    test_prompt = "Test prompt"
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await llm_client.generate_text(test_prompt)
        assert result is None

@pytest.mark.asyncio
async def test_service_fallback(llm_client):
    """Test fallback to LM Studio when Ollama fails."""
    test_prompt = "Test prompt"
    expected_response = {"choices": [{"text": "Fallback response"}]}
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        # Mock Ollama failure
        mock_ollama = AsyncMock()
        mock_ollama.status = 500
        
        # Mock LM Studio success
        mock_lm_studio = AsyncMock()
        mock_lm_studio.status = 200
        mock_lm_studio.json.return_value = expected_response
        
        mock_post.return_value.__aenter__.side_effect = [mock_ollama, mock_lm_studio]
        
        result = await llm_client.generate_text(test_prompt)
        assert result == expected_response["choices"][0]["text"]

@pytest.mark.asyncio
async def test_service_switching(llm_client):
    """Test switching between Ollama and LM Studio services."""
    llm_client.switch_service('lm_studio')
    assert llm_client.current_service == 'lm_studio'
    
    llm_client.switch_service('ollama')
    assert llm_client.current_service == 'ollama'
    
    with pytest.raises(ValueError):
        llm_client.switch_service('invalid_service')