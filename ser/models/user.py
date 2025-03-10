"""User model and authentication database schema for Tío Pepe system."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import sqlite3
from pathlib import Path
from contextlib import contextmanager

# Database path
DB_PATH = Path(__file__).parent.parent / 'data' / 'tiope.db'

# User roles
ROLES = {
    'admin': ['read', 'write', 'delete', 'manage_users'],
    'manager': ['read', 'write', 'delete'],
    'user': ['read', 'write'],
    'guest': ['read']
}

# Database schema for users and roles
USER_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    failed_login_attempts INTEGER DEFAULT 0,
    last_login_attempt TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""

AUDIT_LOG_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)"""

class UserModel:
    """User model for handling user-related operations."""

    def __init__(self):
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables."""
        with self._get_db() as conn:
            conn.execute(USER_SCHEMA)
            conn.execute(AUDIT_LOG_SCHEMA)
            conn.commit()

    @contextmanager
    def _get_db(self):
        """Get database connection."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_user(self, username: str, email: str, password_hash: str, role: str = 'user') -> Optional[Dict[str, Any]]:
        """Create a new user."""
        if role not in ROLES:
            raise ValueError(f"Invalid role: {role}")

        try:
            with self._get_db() as conn:
                cursor = conn.execute(
                    """INSERT INTO users (username, email, password_hash, role)
                       VALUES (?, ?, ?, ?)""",
                    (username, email, password_hash, role)
                )
                conn.commit()
                return self.get_user_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self._get_db() as conn:
            result = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            return dict(result) if result else None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        with self._get_db() as conn:
            result = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()
            return dict(result) if result else None

    def update_login_attempt(self, user_id: int, failed: bool = True) -> None:
        """Update user's login attempt status."""
        with self._get_db() as conn:
            if failed:
                conn.execute(
                    """UPDATE users 
                       SET failed_login_attempts = failed_login_attempts + 1,
                           last_login_attempt = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (user_id,)
                )
            else:
                conn.execute(
                    """UPDATE users 
                       SET failed_login_attempts = 0,
                           last_login_attempt = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (user_id,)
                )
            conn.commit()

    def log_audit_event(self, user_id: Optional[int], action: str, resource: str,
                        details: str, ip_address: str) -> None:
        """Log an audit event."""
        with self._get_db() as conn:
            conn.execute(
                """INSERT INTO audit_logs (user_id, action, resource, details, ip_address)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, action, resource, details, ip_address)
            )
            conn.commit()

    def get_user_permissions(self, role: str) -> List[str]:
        """Get permissions for a given role."""
        return ROLES.get(role, [])

    def check_permission(self, role: str, required_permission: str) -> bool:
        """Check if role has the required permission."""
        return required_permission in self.get_user_permissions(role)