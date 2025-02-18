#!/usr/bin/env python3
from datetime import datetime
import firebase_admin
from firebase_admin import db, credentials
from login import is_logged_in, user_token, firebase
import base64
import os

# Initialize Firebase Admin SDK
cred = credentials.Certificate("assets/keys/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://jobhive-d66d3-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Initialize Firebase Database references
ref = db.reference('jobs')
files_ref = db.reference('files')

def encode_file(file_path):
    """
    Encode file to base64.
    """
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            encoded = base64.b64encode(file_content).decode('utf-8')
            return {
                'filename': os.path.basename(file_path),
                'content': encoded,
                'size': len(file_content),
                'type': os.path.splitext(file_path)[1][1:]  # file extension without dot
            }
    except Exception as e:
        return f"Error encoding file: {e}"

def post_job(title, description, location, tags, file_path=None):
    if not is_logged_in():
        return "Error: Must be logged in to post jobs"
    
    # Get user details from Firebase
    db_inst = firebase.database()
    users = db_inst.child("users").get()
    poster_details = None
    for user in users.each():
        if user.val():
            poster_details = user.val()
            break

    # Create job posting dictionary
    job = {
        'title': title,
        'description': description,
        'location': location,
        'tags': {tag: True for tag in tags},
        'poster_token': user_token,
        'poster_details': poster_details,
        'posted_date': datetime.now().isoformat()
    }
    
    # Push the job posting to get an ID
    job_ref = ref.push(job)
    job_id = job_ref.key
    
    # If a file path was provided and the file exists, handle the file upload
    if file_path and file_path.strip():  # Check if file_path is not empty
        if not os.path.exists(file_path):
            print("Warning: Specified file does not exist. Job posted without file.")
            return job_id
            
        # Check file size (limit: 5MB)
        if os.path.getsize(file_path) > 5 * 1024 * 1024:
            print("Warning: File size exceeds 5MB limit. Job posted without file.")
            return job_id
        
        try:
            file_data = encode_file(file_path)
            if isinstance(file_data, dict):
                # Save file metadata in the job posting
                job['file_info'] = {
                    'filename': file_data['filename'],
                    'size': file_data['size'],
                    'type': file_data['type']
                }
                
                # Save actual file content separately
                files_ref.child(job_id).set({
                    'content': file_data['content'],
                    'uploader': user_token,
                    'upload_date': datetime.now().isoformat()
                })
                
                # Update the job posting with file info
                ref.child(job_id).update(job)
            else:
                print("Warning: Error encoding file. Job posted without file.")
        except Exception as e:
            print(f"Warning: Error handling file upload: {e}. Job posted without file.")
    
    return job_id

def get_all_jobs():
    """
    Get all jobs with basic file info (without actual file content).
    """
    try:
        jobs = ref.get()
        if jobs:
            for job_id in jobs:
                if 'file_content' in jobs[job_id]:
                    del jobs[job_id]['file_content']
        return jobs or {}
    except Exception as e:
        return f"Error fetching jobs: {e}"

def get_job_by_id(job_id):
    """
    Get a specific job by its ID.
    """
    try:
        job = ref.child(job_id).get()
        if job and user_token != job.get('poster_token'):
            # Remove sensitive info if the current user is not the poster
            if 'file_content' in job:
                del job['file_content']
        return job
    except Exception as e:
        return f"Error fetching job: {e}"

def get_jobs_by_tag(tag):
    """
    Get jobs filtered by a specific tag.
    """
    try:
        jobs = ref.order_by_child(f"tags/{tag}").equal_to(True).get()
        if jobs:
            for job_id in jobs:
                if 'file_content' in jobs[job_id]:
                    del jobs[job_id]['file_content']
        return jobs or {}
    except Exception as e:
        return f"Error fetching jobs by tag: {e}"

def get_my_posted_jobs():
    """
    Get all jobs posted by the current user.
    """
    if not is_logged_in():
        return "Error: Must be logged in to view your posted jobs"
    
    try:
        all_jobs = ref.get()
        if not all_jobs:
            return {}
            
        my_jobs = {}
        for job_id, job in all_jobs.items():
            if job.get('poster_token') == user_token:
                my_jobs[job_id] = job
        return my_jobs
    except Exception as e:
        return f"Error fetching your jobs: {e}"

def update_job(job_id, updates):
    """
    Update job details.
    """
    if not is_logged_in():
        return "Error: Must be logged in to update jobs"
        
    try:
        job = ref.child(job_id).get()
        if not job:
            return "Job not found"
            
        # Verify that the current user is the owner
        if job.get('poster_token') != user_token:
            return "Error: Not authorized to update this job"
            
        # Exclude protected fields from updates
        protected_fields = ['poster_token', 'posted_date', 'file_content']
        updates = {k: v for k, v in updates.items() if k not in protected_fields}
        
        ref.child(job_id).update(updates)
        return "Job updated successfully"
    except Exception as e:
        return f"Error updating job: {e}"

def delete_job(job_id):
    """
    Delete a job and its associated file.
    """
    if not is_logged_in():
        return "Error: Must be logged in to delete jobs"
        
    try:
        job = ref.child(job_id).get()
        if not job:
            return "Job not found"
            
        # Verify ownership
        if job.get('poster_token') != user_token:
            return "Error: Not authorized to delete this job"
            
        # Delete the associated file if it exists
        if 'file_info' in job:
            files_ref.child(job_id).delete()
            
        # Delete the job posting
        ref.child(job_id).delete()
        return "Job deleted successfully"
    except Exception as e:
        return f"Error deleting job: {e}"

def search_jobs(query):
    """
    Search for jobs by title or description.
    """
    try:
        all_jobs = ref.get()
        if not all_jobs:
            return {}
            
        query_lower = query.lower()
        matching_jobs = {}
        
        for job_id, job in all_jobs.items():
            if (query_lower in job['title'].lower() or 
                query_lower in job['description'].lower()):
                if 'file_content' in job:
                    del job['file_content']
                matching_jobs[job_id] = job
                
        return matching_jobs
    except Exception as e:
        return f"Error searching jobs: {e}"

def get_recent_jobs(limit=10):
    """
    Get the most recent jobs.
    """
    try:
        jobs = ref.order_by_child('posted_date').limit_to_last(limit).get()
        if jobs:
            for job_id in jobs:
                if 'file_content' in jobs[job_id]:
                    del jobs[job_id]['file_content']
            jobs_list = [{'id': k, **v} for k, v in jobs.items()]
            return sorted(jobs_list, key=lambda x: x['posted_date'], reverse=True)
        return []
    except Exception as e:
        return f"Error fetching recent jobs: {e}"

def get_file_content(job_id):
    """
    Get file content if authorized.
    """
    if not is_logged_in():
        return "Error: Must be logged in to access files"
    
    try:
        job = ref.child(job_id).get()
        if not job or 'file_info' not in job:
            return "No file found for this job"
        
        # Check authorization
        if job['poster_token'] != user_token:
            return "Error: Not authorized to access this file"
        
        file_content = files_ref.child(job_id).get()
        if file_content and 'content' in file_content:
            return {
                'content': file_content['content'],
                'filename': job['file_info']['filename'],
                'type': job['file_info']['type']
            }
        return "File content not found"
    
    except Exception as e:
        return f"Error retrieving file: {e}"

def save_file(job_id, output_path):
    """
    Save file content to disk.
    """
    file_data = get_file_content(job_id)
    if isinstance(file_data, dict):
        try:
            content = base64.b64decode(file_data['content'])
            full_path = os.path.join(output_path, file_data['filename'])
            with open(full_path, 'wb') as file:
                file.write(content)
            return f"File saved to {full_path}"
        except Exception as e:
            return f"Error saving file: {e}"
    return file_data  # Return error message if any

def delete_file(job_id):
    """
    Delete a file if authorized.
    """
    if not is_logged_in():
        return "Error: Must be logged in to delete files"
    
    try:
        job = ref.child(job_id).get()
        if not job or 'file_info' not in job:
            return "No file found for this job"
        
        if job['poster_token'] != user_token:
            return "Error: Not authorized to delete this file"
        
        files_ref.child(job_id).delete()
        ref.child(job_id).child('file_info').delete()
        
        return "File deleted successfully"
    except Exception as e:
        return f"Error deleting file: {e}"

###############################################################################
# Terminal GUI Functions
###############################################################################

def list_all_jobs_gui():
    jobs = get_all_jobs()
    if isinstance(jobs, dict) and jobs:
        print("\n--- All Jobs ---")
        for jid, job in jobs.items():
            print(f"ID: {jid}")
            print(f"Title: {job.get('title', 'No Title')}")
            print(f"Location: {job.get('location', 'No Location')}")
            print(f"Posted: {job.get('posted_date', 'N/A')}")
            print("-" * 20)
    else:
        print("No jobs found or error occurred.")

def open_job_gui():
    job_id = input("Enter Job ID: ").strip()
    job = get_job_by_id(job_id)
    if isinstance(job, dict):
        print("\n--- Job Details ---")
        for key, value in job.items():
            print(f"{key}: {value}")
    else:
        print(job)

def search_jobs_gui():
    query = input("Enter search query: ").strip()
    results = search_jobs(query)
    if isinstance(results, dict) and results:
        print("\n--- Search Results ---")
        for jid, job in results.items():
            print(f"ID: {jid} | Title: {job.get('title', 'No Title')}")
    else:
        print("No matching jobs found or error occurred.")

def post_job_gui():
    print("\n--- Post a New Job ---")
    title = input("Enter Job Title: ").strip()
    description = input("Enter Job Description: ").strip()
    location = input("Enter Job Location: ").strip()
    tags_str = input("Enter tags (comma separated): ").strip()
    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
    file_path = input("Enter file path (or leave blank): ").strip() or None
    result = post_job(title, description, location, tags, file_path)
    print(f"Job posted. ID: {result}" if isinstance(result, str) else result)

def update_job_gui():
    print("\n--- Update a Job ---")
    job_id = input("Enter Job ID to update: ").strip()
    updates = {}
    new_title = input("Enter new title (leave blank to skip): ").strip()
    if new_title:
        updates['title'] = new_title
    new_description = input("Enter new description (leave blank to skip): ").strip()
    if new_description:
        updates['description'] = new_description
    new_location = input("Enter new location (leave blank to skip): ").strip()
    if new_location:
        updates['location'] = new_location
    new_tags = input("Enter new tags (comma separated, leave blank to skip): ").strip()
    if new_tags:
        tags_list = [tag.strip() for tag in new_tags.split(',') if tag.strip()]
        updates['tags'] = {tag: True for tag in tags_list}
    result = update_job(job_id, updates)
    print(result)

def delete_job_gui():
    job_id = input("Enter Job ID to delete: ").strip()
    result = delete_job(job_id)
    print(result)

def my_posted_jobs_gui():
    my_jobs = get_my_posted_jobs()
    if isinstance(my_jobs, dict) and my_jobs:
        print("\n--- My Posted Jobs ---")
        for jid, job in my_jobs.items():
            print(f"ID: {jid} | Title: {job.get('title', 'No Title')}")
    else:
        print("No jobs posted by you or error occurred.")

def terminal_gui():
    print("Launching JobHive Terminal GUI...")
    
    # Enforce real authentication
    if not is_logged_in():
        print("Error: You must be logged in to use the terminal interface.")
        return

    menu_options = {
        '1': ("List All Jobs", list_all_jobs_gui),
        '2': ("Open Job by ID", open_job_gui),
        '3': ("Search Jobs", search_jobs_gui),
        '4': ("Post a Job", post_job_gui),
        '5': ("Update a Job", update_job_gui),
        '6': ("Delete a Job", delete_job_gui),
        '7': ("Get My Posted Jobs", my_posted_jobs_gui),
        '8': ("Exit", None)
    }
    
    while True:
        print("\n=== JobHive Terminal GUI ===")
        for key, (desc, _) in menu_options.items():
            print(f"{key}. {desc}")
        choice = input("Enter your choice: ").strip()
        
        if choice == '8':
            print("Exiting Terminal GUI.")
            break
        elif choice in menu_options:
            menu_options[choice][1]()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    terminal_gui()
