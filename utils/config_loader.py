import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Loads configuration from config.yaml file"""
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, encoding="utf-8") as f:
            self.data = yaml.safe_load(f)
        
        self.base_url = self.data["base_url"]
        self.timeout = self.data.get("timeout", 30000)
        
        # Priority: Environment variable > YAML config > Default
        env_headless = os.getenv("HEADLESS")
        if env_headless is not None:
            self.headless = env_headless.lower() == "true"
        else:
            self.headless = self.data.get("headless", True)
            
        self.slow_mo = int(os.getenv("SLOW_MO", self.data.get("slow_mo", 0)))

    def get_user(self, user_type: str = "standard"):
        """Returns user credentials from config"""
        return self.data["users"][user_type]