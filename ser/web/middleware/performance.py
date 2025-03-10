"""Performance optimization middleware for the Tío Pepe system."""

from typing import Dict, Any
import os
from PIL import Image
from flask import request, Response
from functools import wraps
from config.performance_config import get_performance_config
import csscompressor
import jsmin
import time

class PerformanceMiddleware:
    """Middleware for handling performance optimizations."""

    def __init__(self, app):
        self.app = app
        self.config = get_performance_config()
        self.setup_optimization_paths()

    def setup_optimization_paths(self) -> None:
        """Setup directories for optimized resources."""
        static_dir = self.app.static_folder
        self.optimized_dir = os.path.join(static_dir, 'optimized')
        self.webp_dir = os.path.join(self.optimized_dir, 'webp')
        self.min_dir = os.path.join(self.optimized_dir, 'min')

        for directory in [self.optimized_dir, self.webp_dir, self.min_dir]:
            os.makedirs(directory, exist_ok=True)

    def init_app(self, app):
        """Initialize the middleware with the Flask app."""
        self.app = app
        if self.config['resource_minification']['enabled']:
            self.setup_resource_minification()
        if self.config['image_optimization']['enabled']:
            self.setup_image_optimization()

    def setup_resource_minification(self) -> None:
        """Configure resource minification."""
        @self.app.before_request
        def minify_resources():
            if request.path.endswith('.css'):
                return self.minify_css()
            elif request.path.endswith('.js'):
                return self.minify_js()

    def setup_image_optimization(self) -> None:
        """Configure image optimization."""
        @self.app.before_request
        def optimize_images():
            if any(request.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                return self.optimize_image()

    def minify_css(self) -> Response:
        """Minify CSS files."""
        css_config = self.config['resource_minification']['css']
        if not css_config['minify']:
            return None

        file_path = os.path.join(self.app.static_folder, request.path.lstrip('/'))
        min_path = os.path.join(self.min_dir, os.path.basename(file_path))

        if not os.path.exists(min_path) or \
           os.path.getmtime(file_path) > os.path.getmtime(min_path):
            with open(file_path, 'r') as f:
                content = f.read()
            minified = csscompressor.compress(content)
            with open(min_path, 'w') as f:
                f.write(minified)

        return self.app.send_file(min_path)

    def minify_js(self) -> Response:
        """Minify JavaScript files."""
        js_config = self.config['resource_minification']['js']
        if not js_config['minify']:
            return None

        file_path = os.path.join(self.app.static_folder, request.path.lstrip('/'))
        min_path = os.path.join(self.min_dir, os.path.basename(file_path))

        if not os.path.exists(min_path) or \
           os.path.getmtime(file_path) > os.path.getmtime(min_path):
            with open(file_path, 'r') as f:
                content = f.read()
            minified = jsmin.jsmin(content)
            with open(min_path, 'w') as f:
                f.write(minified)

        return self.app.send_file(min_path)

    def optimize_image(self) -> Response:
        """Optimize and convert images to WebP format."""
        img_config = self.config['image_optimization']
        if not img_config['enabled']:
            return None

        file_path = os.path.join(self.app.static_folder, request.path.lstrip('/'))
        webp_path = os.path.join(self.webp_dir, 
                                os.path.splitext(os.path.basename(file_path))[0] + '.webp')

        if not os.path.exists(webp_path) or \
           os.path.getmtime(file_path) > os.path.getmtime(webp_path):
            with Image.open(file_path) as img:
                # Resize if needed
                if img.width > img_config['max_width']:
                    ratio = img_config['max_width'] / img.width
                    new_size = (img_config['max_width'], int(img.height * ratio))
                    img = img.resize(new_size, Image.LANCZOS)
                
                # Convert to WebP
                img.save(webp_path, 'WEBP', quality=img_config['quality'])

        return self.app.send_file(webp_path)

    def measure_response_time(self, f):
        """Decorator to measure response time."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log slow responses
            if duration * 1000 > self.config['monitoring']['logging']['threshold_ms']:
                self.app.logger.warning(f'Slow response: {request.path} took {duration:.2f}s')
            
            return response
        return decorated_function