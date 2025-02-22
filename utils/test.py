import os
from storage_manager import StorageManager

def delete_all_files(storage_manager):
    """
    Delete all files in the storage bucket.
    
    Args:
        storage_manager: StorageManager instance
    
    Returns:
        tuple: (number of files deleted, number of files failed to delete)
    """
    print("\nStarting deletion of all files...")
    files = storage_manager.list_files()
    
    if not files:
        print("No files found to delete.")
        return (0, 0)
    
    success_count = 0
    fail_count = 0
    
    for file in files:
        try:
            # Use the 'path' key from the file dictionary
            if storage_manager.delete_file(file['path']):
                success_count += 1
                print(f"Deleted: {file['name']}")
            else:
                fail_count += 1
                print(f"Failed to delete: {file['name']}")
        except Exception as e:
            fail_count += 1
            print(f"Error deleting {file['name']}: {str(e)}")
    
    print(f"\nDeletion complete. Successfully deleted {success_count} files. Failed to delete {fail_count} files.")
    return (success_count, fail_count)
def main():
    try:
        # Initialize the StorageManager
        storage_manager = StorageManager()
        print("StorageManager initialized successfully.\n")
        
        # Specify the path to your PDF resume
        resume_path = "assets/resumes/test_candidate_resume.pdf"  # Change this to your actual PDF file path
        
        # Upload the resume
        upload_result = storage_manager.upload_file(resume_path)
        if upload_result:
            print("Resume uploaded successfully:")
            print(upload_result, "\n")
        else:
            print("Resume upload failed.\n")
            return
        
        # List files in the 'resumes' folder
        print("Listing files in the bucket (prefix 'resumes/'):")
        files = storage_manager.list_files()
        for file in files:
            print(file)
        print()

        # Option to delete all files
        user_input = input("Would you like to delete all files? (yes/no): ").lower()
        if user_input == 'yes':
            delete_all_files(storage_manager)
            
    except Exception as e:
        print("An error occurred during testing:", e)

if __name__ == "__main__":
    main()