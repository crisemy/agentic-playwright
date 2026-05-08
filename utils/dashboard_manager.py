# utils/dashboard_manager.py
import json
import os
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "agent_activity.json"

class DashboardManager:
    """Manages recording and retrieval of agent activity for the dashboard."""
    
    @staticmethod
    def log_thought(agent_name: str, message: str):
        """Record an agent's thought or action."""
        entry = {
            "agent": agent_name,
            "message": message,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        
        logs = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r") as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(entry)
        # Keep only the last 50 logs
        logs = logs[-50:]
        
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

    @staticmethod
    def get_logs():
        """Retrieve all recorded logs."""
        if not LOG_FILE.exists():
            return []
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    @staticmethod
    def clear_logs():
        """Clear the logs."""
        if LOG_FILE.exists():
            os.remove(LOG_FILE)
