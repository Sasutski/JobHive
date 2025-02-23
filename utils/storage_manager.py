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
        Upload a file to Google Cloud Storage.
        Args:
            file_path: Path to the file to upload
            destination_folder: Folder in bucket to store file
            is_private: Whether the file should be private
        Returns:
            dict: Contains file information including URL and storage path
        """
        try:
            # Create a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = Path(file_path).name
            destination_blob_name = f"{destination_folder}/{timestamp}_{original_filename}"
            
            # Create blob and upload file
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)

            # For private files, we'll only return the path
            # For public files, we'll include a signed URL
            if is_private:
                return {
                    'path': destination_blob_name,
                    'name': original_filename,
                    'is_private': True
                }
            else:
                # Generate a signed URL with longer expiration for public files
                signed_url = blob.generate_signed_url(
                    version="v4",
                    expiration=dt.timedelta(days=7),  # 7 day expiration for public files
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
        Get a signed URL for temporary access to a private file
        Args:
            blob_path: Path to the blob in storage
            expiration_minutes: Number of minutes until URL expires
        Returns:
            str: Signed URL for temporary access
        """
        try:
            blob = self.bucket.blob(blob_path)
            if not blob.exists():
                return None
            
            # Generate signed URL
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
        Delete a file from Google Cloud Storage
        """
        try:
            blob = self.bucket.blob(blob_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

    def list_files(self, prefix="resumes/", include_private=False):
        """
        List all files in a folder
        """
        try:
            files = []
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            for blob in blobs:
                file_info = {
                    'name': blob.name.split('/')[-1],
                    'path': blob.name,
                    'size': blob.size,
                    'updated': blob.updated
                }
                
                # Generate signed URL for all files
                if include_private or not prefix.startswith('model_resumes/'):
                    file_info['signed_url'] = blob.generate_signed_url(
                        version="v4",
                        expiration=dt.timedelta(minutes=30),
                        method="GET"
                    )
                
                files.append(file_info)
            
            return files
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def download_file(self, storage_path, local_path):
        """Download a file from Firebase Storage to a local path."""
        try:
            blob = self.bucket.blob(storage_path)
            blob.download_to_filename(local_path)
            return True
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return False