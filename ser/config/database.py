"""Database configuration and setup for Tío Pepe system."""

import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

# Database configuration
DB_PATH = Path(__file__).parent.parent / 'data' / 'tiope.db'

# Ensure data directory exists
DB_PATH.parent.mkdir(exist_ok=True)

# Database schema definitions
SCHEMA = {
    'tasks': """
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        task_type TEXT NOT NULL,
        status TEXT NOT NULL,
        priority INTEGER,
        data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    'agent_configs': """
    CREATE TABLE IF NOT EXISTS agent_configs (
        agent_id TEXT PRIMARY KEY,
        agent_type TEXT NOT NULL,
        config TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    'system_logs': """
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    'chat_conversations': """
    CREATE TABLE IF NOT EXISTS chat_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
}

@contextmanager
def get_db_connection():
    """Create a database connection context manager."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database and create tables if they don't exist."""
    with get_db_connection() as conn:
        for table_name, table_schema in SCHEMA.items():
            conn.execute(table_schema)
        conn.commit()

def get_tasks(limit=100):
    """Retrieve recent tasks from the database."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            'SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?',
            (limit,)
        )
        return cursor.fetchall()

def save_task(task_data):
    """Save a task to the database."""
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO tasks (id, task_type, status, priority, data) '
            'VALUES (?, ?, ?, ?, ?)',
            (task_data['id'], task_data['task_type'], task_data['status'],
             task_data.get('priority', 0), str(task_data.get('data', {})))
        )
        conn.commit()

def save_agent_config(agent_config):
    """Save agent configuration to the database."""
    with get_db_connection() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO agent_configs (agent_id, agent_type, config) '
            'VALUES (?, ?, ?)',
            (agent_config['agent_id'], agent_config['agent_type'],
             str(agent_config.get('config', {})))
        )
        conn.commit()

def log_system_event(level, message):
    """Log a system event to the database."""
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO system_logs (level, message) VALUES (?, ?)',
            (level, message)
        )
        conn.commit()

def save_chat_message(session_id, role, message):
    """Save a chat message to the database."""
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO chat_conversations (session_id, role, message) '
            'VALUES (?, ?, ?)',
            (session_id, role, message)
        )
        conn.commit()

def get_chat_history(session_id, limit=50):
    """Retrieve chat history for a specific session."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            'SELECT * FROM chat_conversations '
            'WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?',
            (session_id, limit)
        )
        return cursor.fetchall()