"""
job_posting.py
post jobs to a database that can be accessed by other users on a different computer: Use firebase
include tags for search filtering
"""
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials

# Initialize Firebase with your credentials
cred = credentials.Certificate("assets/keys/serviceAccountKey.json")

# Initialize the app with your database URL
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://jobhive-d66d3-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
ref = db.reference('jobs')
def post_job(title, description, location, tags):
    # Create a new job posting
    job = {
        'title': title,
        'description': description,
        'location': location,
        'tags': tags
    }

    # Push the job posting to the database
    ref.child('jobs').push(job)
    
# get all jobs in the database

def get_all_jobs():
    jobs = ref.child('jobs').get()
    return jobs

def get_job_by_id(job_id):
    try:
        job = ref.child('jobs').child(job_id).get()
        return job
    except Exception as e:
        return f"Error fetching job by ID: {e}"
    
    
def get_jobs_by_tag(tag):
    try:
        jobs = ref.child('jobs').order_by_child('tags').equal_to(tag).get()
        return jobs
    except Exception as e:
        return f"Error fetching job by ID: {e}"
    
# add debug code

def debug():
    print("Debugging...")
    print("All jobs:")
    print(get_all_jobs())
    print("Job by ID:")
    print(get_job_by_id('1'))
    print("Jobs by tag:")
    print(get_jobs_by_tag('Python'))

debug()
