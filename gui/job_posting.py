import firebase_admin
from firebase_admin import db, credentials
import json

# Initialize Firebase with your credentials
cred = credentials.Certificate("assets/keys/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://jobhive-d66d3-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Reference directly to the "jobs" node
ref = db.reference('jobs')

def post_job(title, description, location, tags):
    # Create a new job posting with tags stored as a dict for easier querying
    job = {
        'title': title,
        'description': description,
        'location': location,
        'tags': {tag: True for tag in tags}
    }
    # Push the job posting directly to the "jobs" node
    ref.push(job)
    
def get_all_jobs():
    jobs = ref.get()
    return jobs

def get_job_by_id(job_id):
    try:
        job = ref.child(job_id).get()
        return job
    except Exception as e:
        return f"Error fetching job by ID: {e}"
    
def get_jobs_by_tag(tag):
    try:
        # Query by the child key "tags/<tag>"
        jobs = ref.order_by_child(f"tags/{tag}").equal_to(True).get()
        return jobs
    except Exception as e:
        return f"Error fetching jobs by tag: {e}"
    
def debug():
    print("Debugging...\n")

    print("📌 All Job Listings:")
    all_jobs = get_all_jobs()
    for job_id, job in all_jobs.items():
        print(f"\n🔹 {job['title']} ({job['location']})")
        print(f"   📝 {job['description']}")
        print(f"   🏷️ Tags: {', '.join(job['tags'].keys())}")

    if all_jobs:
        first_key = list(all_jobs.keys())[0]
        first_job = get_job_by_id(first_key)
        print("\n📍 First Job Details:")
        print(f"🔹 {first_job['title']} ({first_job['location']})")
        print(f"   📝 {first_job['description']}")
        print(f"   🏷️ Tags: {', '.join(first_job['tags'].keys())}")

    print("\n📌 Jobs Tagged with 'Python':")
    jobs_by_tag = get_jobs_by_tag('Python')
    for job_id, job in jobs_by_tag.items():
        print(f"\n🔹 {job['title']} ({job['location']})")
        print(f"   📝 {job['description']}")
        print(f"   🏷️ Tags: {', '.join(job['tags'].keys())}")

debug()

debug()
