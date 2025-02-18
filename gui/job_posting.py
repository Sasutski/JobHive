"""
Enhanced job posting system with base64 file storage in Firebase
"""
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
    
    # If a file was provided, encode and store it
    if file_path and os.path.exists(file_path):
        # Check file size (limit: 5MB)
        if os.path.getsize(file_path) > 5 * 1024 * 1024:
            return "Error: File size exceeds 5MB limit"
        
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

# Debugging section
def debug():
    print("Debugging...\n")
    
    # For testing purposes, override authentication functions
    global is_logged_in, user_token
    is_logged_in = lambda: True  # Override to always return True during debugging
    user_token = "test_user_token"
    
    # Post a test job. Ensure "test_resume.pdf" exists in your working directory,
    # or pass None if you want to skip file upload testing.
    posted_job_id = post_job(
        "Python Developer", 
        "Looking for experienced Python developer",
        "Remote",
        ["Python", "Django"],
        "/Users/vince/Desktop/JobHive/assets/resumes/test_model_resume.pdf"  # Change this to None if the file doesn't exist.
    )
    
    if isinstance(posted_job_id, str) and posted_job_id.startswith("Error"):
        print(f"Error posting job: {posted_job_id}")
    else:
        print(f"Job posted successfully with ID: {posted_job_id}")
    
    print("\n📌 All Jobs:")
    all_jobs = get_all_jobs()
    if isinstance(all_jobs, dict):
        for job_id, job in all_jobs.items():
            print(f"\n🔹 {job.get('title', 'No Title')}")
            print(f"   📝 {job.get('description', 'No Description')}")
            print(f"   📍 {job.get('location', 'No Location')}")
            if 'tags' in job:
                print(f"   🏷️ {', '.join(job['tags'].keys())}")
    else:
        print("Error fetching all jobs:", all_jobs)
        
    print("\n🔍 Search Results for 'Python':")
    search_results = search_jobs("Python")
    if isinstance(search_results, dict):
        for job_id, job in search_results.items():
            print(f"Found: {job.get('title', 'No Title')}")
    else:
        print("Error searching jobs:", search_results)
        
    print("\n🕒 Recent Jobs:")
    recent = get_recent_jobs(5)
    if isinstance(recent, list):
        for job in recent:
            print(f"Recent: {job.get('title', 'No Title')}")
    else:
        print("Error fetching recent jobs:", recent)

if __name__ == "__main__":
    debug()
