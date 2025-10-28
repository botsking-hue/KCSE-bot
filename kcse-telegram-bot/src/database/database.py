"""
JSON-based database for bot data storage.
"""
import json
import os
from typing import Any, Dict, List, Optional

class Database:
    def __init__(self, db_file: str = 'data/bot_data.json'):
        self.db_file = db_file
        self._ensure_data_directory()
        self.data = self._load_data()
    
    def _ensure_data_directory(self) -> None:
        """Ensure data directory exists."""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_data(self) -> None:
        """Save data to JSON file."""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get_bot_prop(self, key: str, default: Any = None) -> Any:
        """Get bot property."""
        return self.data.get(key, default)
    
    def set_bot_prop(self, key: str, value: Any) -> None:
        """Set bot property."""
        self.data[key] = value
        self._save_data()
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user data."""
        users = self.data.get('users', {})
        return users.get(str(user_id), {})
    
    def set_user_data(self, user_id: int, data: Dict[str, Any]) -> None:
        """Set user data."""
        if 'users' not in self.data:
            self.data['users'] = {}
        self.data['users'][str(user_id)] = data
        self._save_data()
    
    def set_user_prop(self, user_id: int, key: str, value: Any) -> None:
        """Set user property."""
        user_data = self.get_user_data(user_id)
        user_data[key] = value
        self.set_user_data(user_id, user_data)
    
    def get_all_users(self) -> List[int]:
        """Get all user IDs."""
        users = self.data.get('users', {})
        return [int(user_id) for user_id in users.keys()]
    
    def get_total_users(self) -> int:
        """Get total number of users."""
        return len(self.get_all_users())