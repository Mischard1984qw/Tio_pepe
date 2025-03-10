"""General utility functions shared across the Tío Pepe system."""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import hashlib
import re
import time
from datetime import datetime

def validate_json(data: str) -> bool:
    """Validate if a string is valid JSON."""
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def safe_file_write(file_path: Path, content: str, mode: str = 'w') -> bool:
    """Safely write content to a file with error handling."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def generate_hash(data: str) -> str:
    """Generate SHA-256 hash of input data."""
    return hashlib.sha256(data.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def retry_operation(func: callable, max_attempts: int = 3, delay: float = 1.0) -> Any:
    """Retry an operation with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            time.sleep(delay * (2 ** attempt))

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp in ISO 8601 format."""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.isoformat()

def deep_get(obj: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get nested dictionary values using dot notation."""
    try:
        for key in path.split('.'):
            obj = obj[key]
        return obj
    except (KeyError, TypeError):
        return default

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    return re.sub(r'[<>:"\\/|?*]', '_', filename)