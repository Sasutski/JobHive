from google.cloud import storage
import requests
import json
from datetime import datetime
from pathlib import Path

CREDENTIALS_URL = "https://gist.githubusercontent.com/Sasutski/9b1617a09f94311ef3ab20c392f88534/raw"
BUCKET_NAME = "jobhive-resumes"

class StorageManager:
    def __init__(self):
        try:
            # Get credentials from Gist
            response = requests.get(CREDENTIALS_URL)
            # Debug: print the fetched credentials content
            print("Fetched credentials content:", response.text)
            
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
                print(f"Bucket {BUCKET_NAME} created successfully")
        
        except Exception as e:
            print(f"Error initializing storage: {str(e)}")
            raise

    def upload_file(self, file_path, destination_folder="resumes"):
        """
        Upload a file to Google Cloud Storage.
        """
        try:
            # Create a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = Path(file_path).name
            destination_blob_name = f"{destination_folder}/{timestamp}_{original_filename}"
            
            # Create blob and upload file
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            
            # Since uniform bucket-level access is enabled, do not use blob.make_public()
            # Instead, ensure that the bucket's IAM policy grants the desired public access.
            # For example, you might grant the "allUsers" member the "Storage Object Viewer" role.
            
            return {
                'url': blob.public_url,
                'path': destination_blob_name,
                'name': original_filename
            }
            
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
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

    def list_files(self, prefix="resumes/"):
        """
        List all files in a folder
        """
        try:
            files = []
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            for blob in blobs:
                files.append({
                    'name': blob.name.split('/')[-1],
                    'path': blob.name,
                    'url': blob.public_url,
                    'size': blob.size,
                    'updated': blob.updated
                })
            
            return files
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
