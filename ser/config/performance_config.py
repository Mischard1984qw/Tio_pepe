"""Performance optimization configuration for the Tío Pepe system."""

from typing import Dict, Any

def get_performance_config() -> Dict[str, Any]:
    """Get performance optimization configuration settings."""
    return {
        'lazy_loading': {
            'enabled': True,
            'threshold': '100px',  # Load when element is 100px from viewport
            'components': [
                'agents',
                'tasks',
                'settings'
            ]
        },
        'image_optimization': {
            'enabled': True,
            'formats': ['webp', 'jpeg'],
            'quality': 85,
            'max_width': 1920,
            'responsive_sizes': [320, 640, 1024, 1920],
            'lazy_load': True
        },
        'resource_minification': {
            'enabled': True,
            'js': {
                'minify': True,
                'compress': True,
                'sourcemaps': True
            },
            'css': {
                'minify': True,
                'compress': True,
                'sourcemaps': True
            }
        },
        'monitoring': {
            'enabled': True,
            'prometheus': {
                'port': 9090,
                'metrics': [
                    'response_time',
                    'memory_usage',
                    'cpu_usage',
                    'request_count'
                ]
            },
            'logging': {
                'performance_metrics': True,
                'slow_queries': True,
                'threshold_ms': 1000
            }
        }
    }