import os
from pathlib import Path

# Base configuration
PROJECT_ROOT = Path(__file__).parent

# Firebase configuration
FIREBASE_CONFIG = {
    "service_account_url": "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json",
    "api_key": "AIzaSyAcwreE9k06t8HtJ6vhSOblwCskAEkWRWQ"
}

# File storage configuration
STORAGE_CONFIG = {
    "upload_folder": PROJECT_ROOT / "uploads",
    "allowed_extensions": {'.pdf', '.doc', '.docx', '.txt'}
}

# Session configuration
SESSION_CONFIG = {
    "session_file": PROJECT_ROOT / "user.json",
    "token_expiry": 3600  # 1 hour in seconds
}

# Create required directories
STORAGE_CONFIG['upload_folder'].mkdir(parents=True, exist_ok=True)