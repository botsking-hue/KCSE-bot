import json, os
from typing import Any, Dict, List

class DataManager:
    def __init__(self, data_file=None):
        # Use writable temp path suitable for serverless (ephemeral) - but keep default for local dev
        base = os.getenv("DATA_DIR", ".")
        self.data_file = data_file or os.path.join(base, "bot_data.json")
        self.data = self._load_data()

    def _create_initial_data(self):
        return {
            "user_stats": {"total_users": 0},
            "pending_payments": [],
            "pricing_packages": {}
        }

    def _load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    return json.load(f)
            else:
                return self._create_initial_data()
        except Exception as e:
            print("Error loading data:", e)
            return self._create_initial_data()

    def _save_data(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print("Error saving data:", e)

    # pending payments
    def get_pending_payments(self):
        return self.data.get("pending_payments", [])

    def add_pending_payment(self, payment: Dict[str, Any]):
        payments = self.get_pending_payments()
        payments.append(payment)
        self.data["pending_payments"] = payments
        self._save_data()

    def remove_pending_payment(self, user_id: int):
        payments = [p for p in self.get_pending_payments() if p.get("user_id") != user_id]
        self.data["pending_payments"] = payments
        self._save_data()
