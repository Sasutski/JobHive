# Import required modules for path and file operations
import os
from pathlib import Path

# Set project root directory using the current file's location
PROJECT_ROOT = Path(__file__).parent

# Firebase configuration settings
# Contains service account key URL and API key for Firebase authentication
FIREBASE_CONFIG = {
    "service_account_url": "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json",
    "api_key": "AIzaSyAcwreE9k06t8HtJ6vhSOblwCskAEkWRWQ"
}

# File storage configuration settings
# Defines upload directory and allowed file extensions for document uploads
STORAGE_CONFIG = {
    "upload_folder": PROJECT_ROOT / "uploads",  # Path to upload directory
    "allowed_extensions": {'.pdf', '.doc', '.docx', '.txt'}  # Allowed file types
}

# Session configuration settings
# Defines session file location and token expiration time
SESSION_CONFIG = {
    "session_file": PROJECT_ROOT / "user.json",  # Path to user session file
    "token_expiry": 3600  # Session token expiry time (1 hour in seconds)
}

# Create required directories if they don't exist
# Ensures upload folder is available when application starts
STORAGE_CONFIG['upload_folder'].mkdir(parents=True, exist_ok=True)