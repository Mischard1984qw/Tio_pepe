"""LLM client module for integrating with Ollama and LM Studio in Tío Pepe."""

from typing import Dict, Any, Optional
import aiohttp
import logging
from config.config import OLLAMA_CONFIG, LM_STUDIO_CONFIG

class LLMClient:
    """Handles interactions with Ollama and LM Studio language models."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ollama_config = OLLAMA_CONFIG
        self.lm_studio_config = LM_STUDIO_CONFIG
        self.current_service = 'ollama'  # Default to Ollama

    async def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """Make a request to Ollama API."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.ollama_config['api_url']}/api/generate",
                    json={
                        'model': self.ollama_config['model'],
                        'prompt': prompt,
                        'max_tokens': self.ollama_config['max_tokens'],
                        'temperature': self.ollama_config['temperature']
                    },
                    timeout=self.ollama_config['timeout']
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Ollama API error: {response.status}")
                        return None
            except Exception as e:
                self.logger.error(f"Error calling Ollama API: {str(e)}")
                return None

    async def _call_lm_studio(self, prompt: str) -> Dict[str, Any]:
        """Make a request to LM Studio API."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.lm_studio_config['api_url']}/completions",
                    json={
                        'prompt': prompt,
                        'max_tokens': self.lm_studio_config['max_tokens'],
                        'temperature': self.lm_studio_config['temperature']
                    },
                    timeout=self.lm_studio_config['timeout']
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"LM Studio API error: {response.status}")
                        return None
            except Exception as e:
                self.logger.error(f"Error calling LM Studio API: {str(e)}")
                return None

    async def generate_text(self, prompt: str) -> Optional[str]:
        """Generate text using the current LLM service with fallback."""
        result = None

        # Try primary service first
        if self.current_service == 'ollama':
            result = await self._call_ollama(prompt)
            if not result:
                self.logger.info("Falling back to LM Studio")
                result = await self._call_lm_studio(prompt)
        else:
            result = await self._call_lm_studio(prompt)
            if not result:
                self.logger.info("Falling back to Ollama")
                result = await self._call_ollama(prompt)

        if not result:
            self.logger.error("Both LLM services failed")
            return None

        return result.get('response') or result.get('choices', [{}])[0].get('text')

    def switch_service(self, service: str) -> None:
        """Switch between Ollama and LM Studio."""
        if service not in ['ollama', 'lm_studio']:
            raise ValueError("Invalid service name. Use 'ollama' or 'lm_studio'")
        self.current_service = service
        self.logger.info(f"Switched to {service} service")