"""Test suite for Redis cache configuration and functionality."""

import unittest
from unittest.mock import Mock, patch
from config.redis_config import RedisCache, cache_response
import json

class TestRedisCache(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.redis_cache = RedisCache()

    @patch('config.redis_config.get_config')
    def test_redis_initialization(self, mock_get_config):
        """Test Redis cache initialization with config values."""
        mock_config = {
            'redis': {
                'host': 'test-host',
                'port': 1234,
                'db': 1,
                'socket_timeout': 10,
                'socket_connect_timeout': 5,
                'retry_on_timeout': False,
                'max_connections': 20,
                'health_check_interval': 60,
                'default_ttl': 7200,
                'cache_prefix': 'test',
                'enable_compression': False
            }
        }
        mock_get_config.return_value = mock_config
        
        redis_cache = RedisCache()
        self.assertEqual(redis_cache.default_ttl, 7200)
        self.assertEqual(redis_cache.cache_prefix, 'test')
        self.assertFalse(redis_cache.enable_compression)

    def test_cache_key_generation(self):
        """Test cache key generation with prefix and identifier."""
        key = self.redis_cache.cache_key('test', 'id123')
        expected_key = f"{self.redis_cache.cache_prefix}:test:id123"
        self.assertEqual(key, expected_key)

    @patch('redis.Redis.get')
    def test_get_cache_value(self, mock_redis_get):
        """Test getting value from cache."""
        test_data = {'key': 'value'}
        mock_redis_get.return_value = json.dumps(test_data)
        
        result = self.redis_cache.get('test_key')
        self.assertEqual(result, test_data)
        mock_redis_get.assert_called_once_with('test_key')

    @patch('redis.Redis.get')
    def test_get_cache_none(self, mock_redis_get):
        """Test getting non-existent value from cache."""
        mock_redis_get.return_value = None
        result = self.redis_cache.get('test_key')
        self.assertIsNone(result)

    @patch('redis.Redis.setex')
    def test_set_cache_value(self, mock_redis_setex):
        """Test setting value in cache."""
        mock_redis_setex.return_value = True
        test_data = {'key': 'value'}
        
        result = self.redis_cache.set('test_key', test_data)
        self.assertTrue(result)
        mock_redis_setex.assert_called_once_with(
            'test_key',
            self.redis_cache.default_ttl,
            json.dumps(test_data)
        )

    @patch('redis.Redis.delete')
    def test_delete_cache_value(self, mock_redis_delete):
        """Test deleting value from cache."""
        mock_redis_delete.return_value = 1
        result = self.redis_cache.delete('test_key')
        self.assertTrue(result)
        mock_redis_delete.assert_called_once_with('test_key')

    def test_cache_response_decorator(self):
        """Test cache_response decorator functionality."""
        test_data = {'result': 'test'}
        
        @cache_response('test')
        def test_function(param):
            return test_data

        with patch.object(RedisCache, 'get', return_value=None), \
             patch.object(RedisCache, 'set') as mock_set:
            result = test_function('param1')
            self.assertEqual(result, test_data)
            mock_set.assert_called_once()

if __name__ == '__main__':
    unittest.main()