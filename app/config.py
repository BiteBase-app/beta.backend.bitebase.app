import os
from pathlib import Path
from dotenv import load_dotenv
import json

class Config:
    def __init__(self):
        # Load environment variables from all possible sources
        self._load_environment()
        
    def _load_environment(self):
        # 1. Load from .env file if it exists
        load_dotenv()
        
        # 2. Load from service account file if it exists
        service_account_path = Path("bitebase-3d5f9-1475e1373cfa.json")
        if service_account_path.exists():
            try:
                with open(service_account_path) as f:
                    service_account = json.load(f)
                    os.environ.setdefault("FIREBASE_PROJECT_ID", service_account.get("project_id"))
                    os.environ.setdefault("FIREBASE_CLIENT_EMAIL", service_account.get("client_email"))
            except Exception as e:
                print(f"Warning: Failed to load service account file: {e}")

        # 3. Set default values if not already set
        defaults = {
            "FIREBASE_PROJECT_ID": "bitebase-3d5f9",
            "FIREBASE_AUTH_DOMAIN": "bitebase-3d5f9.firebaseapp.com",
            "FIREBASE_STORAGE_BUCKET": "bitebase-3d5f9.firebasestorage.app",
            "ENVIRONMENT": "development"
        }
        
        for key, value in defaults.items():
            os.environ.setdefault(key, value)

    @property
    def firebase_config(self):
        return {
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "auth_domain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
            "storage_bucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
        }

    @property
    def is_production(self):
        return os.environ.get("ENVIRONMENT") == "production"

config = Config()