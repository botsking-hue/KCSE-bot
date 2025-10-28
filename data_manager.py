import json
import os
from typing import Dict, List, Any, Optional

class DataManager:
    def __init__(self, data_file="bot_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return self._create_initial_data()
        return self._create_initial_data()
    
    def _create_initial_data(self) -> Dict[str, Any]:
        initial_data = {
            "admins": [6501240419],
            "user_stats": {"total_users": 0},
            "pending_payments": [],
            "pricing_packages": {
                "single": {"name": "Single Paper", "price": 2000},
                "package_5": {"name": "5 Papers Package", "price": 8000},
                "subscription": {"name": "All Papers Subscription", "price": 15000},
                "school": {"name": "School Package", "price": 30000},
                "early_bird": {"name": "Early Bird Special", "price": 1500}
            },
            "users": {},
            "awaiting_broadcast": False,
            "awaiting_payment_code": {}
        }
        self._save_data(initial_data)
        return initial_data
    
    def _save_data(self, data: Dict[str, Any] = None):
        if data is None:
            data = self.data
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Admin methods
    def get_admins(self) -> List[int]:
        return self.data.get("admins", [6501240419])
    
    def add_admin(self, admin_id: int) -> bool:
        admins = self.get_admins()
        if admin_id not in admins:
            admins.append(admin_id)
            self.data["admins"] = admins
            self._save_data()
            return True
        return False
    
    def remove_admin(self, admin_id: int) -> bool:
        admins = self.get_admins()
        if admin_id in admins and admin_id != 6501240419:
            admins.remove(admin_id)
            self.data["admins"] = admins
            self._save_data()
            return True
        return False
    
    def is_admin(self, user_id: int) -> bool:
        return user_id in self.get_admins()
    
    # User methods
    def get_user(self, user_id: int) -> Dict[str, Any]:
        return self.data.get("users", {}).get(str(user_id), {})
    
    def set_user_prop(self, user_id: int, prop: str, value: Any):
        if "users" not in self.data:
            self.data["users"] = {}
        
        user_id_str = str(user_id)
        if user_id_str not in self.data["users"]:
            self.data["users"][user_id_str] = {}
        
        self.data["users"][user_id_str][prop] = value
        self._save_data()
    
    def get_all_users(self) -> List[int]:
        return [int(user_id) for user_id in self.data.get("users", {}).keys()]
    
    def update_user_stats(self):
        total_users = len(self.get_all_users())
        self.data["user_stats"] = {"total_users": total_users}
        self._save_data()
    
    # Payment methods
    def get_pending_payments(self) -> List[Dict[str, Any]]:
        return self.data.get("pending_payments", [])
    
    def add_pending_payment(self, payment: Dict[str, Any]):
        payments = self.get_pending_payments()
        payments.append(payment)
        self.data["pending_payments"] = payments
        self._save_data()
    
    def remove_pending_payment(self, user_id: int):
        payments = self.get_pending_payments()
        payments = [p for p in payments if p.get("user_id") != user_id]
        self.data["pending_payments"] = payments
        self._save_data()
    
    # Package methods
    def get_packages(self) -> Dict[str, Any]:
        return self.data.get("pricing_packages", {})
    
    def update_package_price(self, package_key: str, new_price: int):
        packages = self.get_packages()
        if package_key in packages:
            packages[package_key]["price"] = new_price
            self.data["pricing_packages"] = packages
            self._save_data()
            return True
        return False
    
    # State management
    def set_awaiting_broadcast(self, value: bool):
        self.data["awaiting_broadcast"] = value
        self._save_data()
    
    def is_awaiting_broadcast(self) -> bool:
        return self.data.get("awaiting_broadcast", False)
    
    def set_awaiting_payment_code(self, user_id: int, value: bool):
        if value:
            self.data["awaiting_payment_code"][str(user_id)] = True
        else:
            self.data["awaiting_payment_code"].pop(str(user_id), None)
        self._save_data()
    
    def is_awaiting_payment_code(self, user_id: int) -> bool:
        return self.data.get("awaiting_payment_code", {}).get(str(user_id), False)
