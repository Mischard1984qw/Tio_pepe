"""Security middleware for Tío Pepe system implementing authentication, CSRF, and XSS protection."""

from functools import wraps
from typing import Dict, Any, Optional, Callable
import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import request, jsonify, session, g
from werkzeug.security import safe_str_cmp
import yaml
import os
from pathlib import Path

# Load auth configuration
auth_config_path = Path(__file__).parent.parent.parent / 'config' / 'auth_config.yaml'
with open(auth_config_path, 'r') as f:
    auth_config = yaml.safe_load(f)

# JWT configuration
JWT_SECRET_KEY = os.getenv('TIO_PEPE_JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = auth_config['jwt']['algorithm']
ACCESS_TOKEN_EXPIRE_MINUTES = auth_config['jwt']['access_token_expire_minutes']

# Security settings
MAX_LOGIN_ATTEMPTS = auth_config['security']['max_login_attempts']
LOCKOUT_DURATION = auth_config['security']['lockout_duration_minutes']

class SecurityMiddleware:
    """Middleware class for handling security features."""

    def __init__(self, app):
        self.app = app
        self.failed_attempts = {}
        self._setup_security_headers()
        self._setup_csrf_protection()

    def _setup_security_headers(self) -> None:
        """Configure security headers for the application."""
        @self.app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval';"
            return response

    def _setup_csrf_protection(self) -> None:
        """Configure CSRF protection."""
        @self.app.before_request
        def csrf_protect():
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                token = request.headers.get('X-CSRF-Token')
                if not token or not self._validate_csrf_token(token):
                    return jsonify({'error': 'Invalid CSRF token'}), 403

    def _validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token."""
        return safe_str_cmp(token, session.get('csrf_token', ''))

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a new JWT access token."""
        expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data.update({'exp': expires})
        return jwt.encode(data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def check_login_attempts(self, user_id: str) -> bool:
        """Check if user is allowed to attempt login."""
        if user_id in self.failed_attempts:
            attempts, last_attempt = self.failed_attempts[user_id]
            if attempts >= MAX_LOGIN_ATTEMPTS:
                lockout_time = last_attempt + timedelta(minutes=LOCKOUT_DURATION)
                if datetime.utcnow() < lockout_time:
                    return False
                self.failed_attempts.pop(user_id)
        return True

    def record_failed_attempt(self, user_id: str) -> None:
        """Record a failed login attempt."""
        if user_id in self.failed_attempts:
            attempts, _ = self.failed_attempts[user_id]
            self.failed_attempts[user_id] = (attempts + 1, datetime.utcnow())
        else:
            self.failed_attempts[user_id] = (1, datetime.utcnow())

    def require_auth(self, roles: Optional[list] = None) -> Callable:
        """Decorator for requiring authentication and optional role checking."""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = request.headers.get('Authorization')
                if not token or not token.startswith('Bearer '):
                    return jsonify({'error': 'Missing or invalid token'}), 401

                payload = self.verify_token(token.split()[1])
                if not payload:
                    return jsonify({'error': 'Invalid token'}), 401

                if roles and payload.get('role') not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403

                g.user = payload
                return f(*args, **kwargs)
            return decorated
        return decorator

    def sanitize_input(self, data: Any) -> Any:
        """Sanitize user input to prevent XSS attacks."""
        if isinstance(data, str):
            # Basic XSS prevention
            return data.replace('<', '&lt;').replace('>', '&gt;')
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        return data