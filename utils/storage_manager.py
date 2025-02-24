from google.cloud import storage
import requests
import json
from datetime import datetime
from pathlib import Path
import datetime as dt

CREDENTIALS_URL = "https://gist.githubusercontent.com/Sasutski/9b1617a09f94311ef3ab20c392f88534/raw"
BUCKET_NAME = "jobhive-resumes"

class StorageManager:
    def __init__(self):
        try:
            # Get credentials from Gist
            response = requests.get(CREDENTIALS_URL)
            
            # Optionally, strip BOM if necessary
            json_content = response.text.lstrip('\ufeff')
            credentials_info = json.loads(json_content)
            
            # Initialize storage client with credentials
            self.storage_client = storage.Client.from_service_account_info(credentials_info)
            self.bucket = self.storage_client.bucket(BUCKET_NAME)
            
            # Create bucket if it doesn't exist
            if not self.bucket.exists(client=self.storage_client):
                self.bucket = self.storage_client.create_bucket(
                    BUCKET_NAME,
                    location="us-central1"
                )
        
        except Exception as e:
            print(f"Error initializing storage: {str(e)}")
            raise

    def upload_file(self, file_path, destination_folder="resumes", is_private=False):
        """
        Upload a file to Google Cloud Storage with configurable privacy settings.
        
        Args:
            file_path: Local path to the file to be uploaded
            destination_folder: Target folder in the bucket (default: 'resumes')
            is_private: Boolean flag to set file visibility (default: False)
            
        Returns:
            dict: File information including URL and storage path, or None if upload fails
        """
        try:
            # Generate unique filename using timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = Path(file_path).name
            destination_blob_name = f"{destination_folder}/{timestamp}_{original_filename}"
            
            # Create and upload blob
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)

            # Return appropriate information based on privacy setting
            if is_private:
                return {
                    'path': destination_blob_name,
                    'name': original_filename,
                    'is_private': True
                }
            else:
                # Generate week-long signed URL for public files
                signed_url = blob.generate_signed_url(
                    version="v4",
                    expiration=dt.timedelta(days=7),
                    method="GET"
                )
                
                return {
                    'url': signed_url,
                    'path': destination_blob_name,
                    'name': original_filename,
                    'is_private': False
                }
            
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None

    def get_private_file_url(self, blob_path, expiration_minutes=5):
        """
        Generate a temporary signed URL for accessing a private file.
        
        Args:
            blob_path: Path to the blob in storage
            expiration_minutes: URL validity duration in minutes (default: 5)
            
        Returns:
            str: Temporary signed URL or None if generation fails
        """
        try:
            # Verify blob exists
            blob = self.bucket.blob(blob_path)
            if not blob.exists():
                return None
            
            # Generate short-lived signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=dt.timedelta(minutes=expiration_minutes),
                method="GET"
            )
            
            return url
            
        except Exception as e:
            print(f"Error generating signed URL: {str(e)}")
            return None

    def delete_file(self, blob_path):
        """
        Delete a file from Google Cloud Storage.
        
        Args:
            blob_path: Path to the blob to be deleted
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            # Verify and delete blob
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                blob.delete()
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

    def download_file(self, blob_path, destination_path):
        """
        Download a file from Google Cloud Storage to local storage.
        
        Args:
            blob_path: Path to the blob in storage
            destination_path: Local path where file should be saved
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Verify and download blob
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                blob.download_to_filename(destination_path)
                return True
            return False
            
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return False