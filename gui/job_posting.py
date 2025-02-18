"""
Enhanced job posting system with model resume handling
"""
from datetime import datetime
import firebase_admin
from firebase_admin import db, credentials
from login import is_logged_in, user_token, firebase

# Initialize Firebase Admin SDK
cred = credentials.Certificate("assets/keys/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://jobhive-d66d3-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Initialize Firebase Storage
ref = db.reference('jobs')

def post_job(title, description, location, tags):
    if not is_logged_in():
        return "Error: Must be logged in to post jobs"
    
    # Get user details from Firebase
    db = firebase.database()
    users = db.child("users").get()
    poster_details = None
    for user in users.each():
        if user.val():
            poster_details = user.val()
            break

    # Create job posting without model resume
    job = {
        'title': title,
        'description': description,
        'location': location,
        'tags': {tag: True for tag in tags},
        'poster_token': user_token,  # from login.py
        'poster_details': poster_details,
        'posted_date': datetime.now().isoformat()
    }
    
    # Push the job posting to the database
    return ref.push(job)

def get_all_jobs():
    """
    Get all jobs (without model resumes)
    """
    jobs = ref.get()
    if jobs:
        # Remove model resume references for public viewing
        for job_id in jobs:
            if 'model_resume_ref' in jobs[job_id]:
                del jobs[job_id]['model_resume_ref']
    return jobs

def get_job_by_id(job_id):
    """
    Get specific job (without model resume unless poster)
    """
    try:
        job = ref.child(job_id).get()
        if job and user_token != job.get('poster_token'):
            # Remove model resume reference if not the poster
            if 'model_resume_ref' in job:
                del job['model_resume_ref']
        return job
    except Exception as e:
        return f"Error fetching job by ID: {e}"

def get_jobs_by_tag(tag):
    """
    Get jobs by tag (without model resumes)
    """
    try:
        jobs = ref.order_by_child(f"tags/{tag}").equal_to(True).get()
        if jobs:
            # Remove model resume references
            for job_id in jobs:
                if 'model_resume_ref' in jobs[job_id]:
                    del jobs[job_id]['model_resume_ref']
        return jobs
    except Exception as e:
        return f"Error fetching jobs by tag: {e}"

def get_my_posted_jobs():
    """
    Get all jobs posted by the currently logged in user
    """
    if not is_logged_in():
        return "Error: Must be logged in to view your posted jobs"
    
    try:
        all_jobs = ref.get()
        my_jobs = {}
        for job_id, job in all_jobs.items():
            if job.get('poster_token') == user_token:
                my_jobs[job_id] = job
        return my_jobs
    except Exception as e:
        return f"Error fetching your jobs: {e}"

def debug():
    print("Debugging...\n")
    print("Posting Jobs")
    print(post_job("Do Jobs", "Develop Jobs", "Singapore", ["Python"]))
    print("📌 All Job Listings:")
    all_jobs = get_all_jobs()
    if all_jobs:
        for job_id, job in all_jobs.items():
            print(f"\n🔹 {job['title']} ({job['location']})")
            print(f"   📝 {job['description']}")
            print(f"   🏷️ Tags: {', '.join(job['tags'].keys())}")
            if 'poster_details' in job and job['poster_details']:
                print(f"   👤 Posted by: {job['poster_details'].get('name', 'Unknown')}")

if __name__ == "__main__":
    debug()