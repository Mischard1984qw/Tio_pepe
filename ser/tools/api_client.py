"""API client module for standardized external API interactions in Tío Pepe."""

from typing import Dict, Any, Optional, Union
import aiohttp
import asyncio
import logging
from datetime import datetime
from .utils import retry_operation

class APIClient:
    """Handles external API interactions with retry and error handling."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.base_url = self.config.get('base_url', '')
        self.timeout = aiohttp.ClientTimeout(
            total=self.config.get('timeout', 30)
        )
        self.headers = self.config.get('headers', {})
        self.retry_attempts = self.config.get('retry_attempts', 3)
        self.session = None

    async def __aenter__(self):
        """Initialize session when entering context."""
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session when exiting context."""
        if self.session:
            await self.session.close()

    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request with retry logic."""
        if not self.session:
            raise RuntimeError("Client must be used within context manager")

        async def _make_request():
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'data': await response.json(),
                    'timestamp': datetime.now().isoformat()
                }

        try:
            return await retry_operation(
                _make_request,
                max_attempts=self.retry_attempts
            )
        except Exception as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return await self.request('GET', url, params=params)

    async def post(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return await self.request('POST', url, json=data if isinstance(data, dict) else None, data=data)

    async def put(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self.request('PUT', url, json=data if isinstance(data, dict) else None, data=data)

    async def delete(self, url: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self.request('DELETE', url)

    async def patch(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None) -> Dict[str, Any]:
        """Make a PATCH request."""
        return await self.request('PATCH', url, json=data if isinstance(data, dict) else None, data=data)

    def set_header(self, key: str, value: str) -> None:
        """Set a header for future requests."""
        self.headers[key] = value
        if self.session:
            self.session._default_headers[key] = value

    def set_auth_token(self, token: str) -> None:
        """Set authentication token in headers."""
        self.set_header('Authorization', f'Bearer {token}')