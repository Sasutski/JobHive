import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate("assets/keys/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://jobhive-d66d3-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


def is_logged_in(user_id):
    """Check if the user is logged in."""
    try:
        user_ref = db.reference(f'users/{user_id}')
        user_data = user_ref.get()
        return user_data is not None
    except Exception as e:
        return False

def search_jobs(query):
    """Search for jobs based on a query and return the job IDs and titles."""
    try:
        jobs = db.reference('jobs').get()
        if jobs:
            search_results = {job_id: job for job_id, job in jobs.items() if query.lower() in job.get("title", "").lower() or query.lower() in job.get("description", "").lower()}
            return search_results if search_results else "No jobs found matching the query."
        return "No jobs available."
    except Exception as e:
        return f"Error searching jobs: {e}"

def view_job_details(job_id):
    """View the full details of a specific job, excluding poster details."""
    try:
        job_ref = db.reference(f'jobs/{job_id}')
        job_data = job_ref.get()
        if job_data:
            # Remove 'poster_details' from the job data before returning it to the applicant
            job_data.pop('poster_details', None)
            return job_data
        return "Job not found."
    except Exception as e:
        return f"Error fetching job details: {e}"

def apply_for_job(user_id, job_id, application_data):
    """Apply for a job if all required information is provided."""
    try:
        if not is_logged_in(user_id):
            return ["Error: User must be logged in to apply."]
        
        user_ref = db.reference(f'users/{user_id}')
        user_data = user_ref.get()
        
        if not user_data:
            return ["User not found."]
        
        job_ref = db.reference(f'jobs/{job_id}')
        job_data = job_ref.get()
        
        if not job_data:
            return ["Job not found."]
        
        # Ensure required fields are present
        required_fields = ["cv", "cover_letter", "age", "gender", "email", "phone_number"]
        optional_fields = ["linkedin", "github", "portfolio"]
        
        missing_fields = []
        for field in required_fields:
            if field not in application_data or not application_data[field]:
                missing_fields.append(f"Missing required field: {field}")
        
        # Check for employer-required optional fields
        employer_requirements = job_data.get("required_fields", [])
        for field in employer_requirements:
            if field in optional_fields and field not in application_data:
                missing_fields.append(f"Missing employer-required field: {field}")
        
        # Include employer-specific questions and additional requirements
        additional_requirements = job_data.get("additional_requirements", [])
        for field in additional_requirements:
            if field not in application_data:
                missing_fields.append(f"Missing additional requirement: {field}")
        
        if missing_fields:
            return missing_fields
        
        # Store application in database, excluding specific fields
        application_ref = db.reference('applications').push()
        application_ref.set({
            "user_id": user_id,
            "job_id": job_id,
            "application_data": {key: value for key, value in application_data.items() if key not in ["poster_details", "poster_token", "file_info"]},
            "status": "Pending"
        })
        
        return ["Application submitted successfully."]
    except Exception as e:
        return [f"Error: {str(e)}"]

def debug_search_and_apply_tests():
    print("\nSearching for jobs with 'developer'...\n")
    search_results = search_jobs("developer")
    
    if isinstance(search_results, dict) and search_results:
        print("=== Search Results ===\n")
        for jid, job in search_results.items():
            print(f"Job ID: {jid}")
            print(f"Title: {job.get('title', 'No Title')}")
            print(f"Description: {job.get('description', 'No Description')}")
            print(f"Location: {job.get('location', 'No Location')}")
            print(f"Posted: {job.get('posted_date', 'N/A')}")
            print("-" * 30)
        
        # Example: Assume user selects job with ID '-OJMy3TlMe3y4qXUKfpz'
        selected_job_id = '-OJMy3TlMe3y4qXUKfpz'
        print(f"\nUser selected job ID: {selected_job_id}")
        
        # Viewing job details for the selected job
        job_details = view_job_details(selected_job_id)
        print("\n=== Job Details ===")
        if isinstance(job_details, dict):
            print(f"Title: {job_details.get('title', 'No Title')}")
            print(f"Description: {job_details.get('description', 'No Description')}")
            print(f"Location: {job_details.get('location', 'No Location')}")
            print(f"Posted: {job_details.get('posted_date', 'N/A')}")
            print("-" * 30)
        else:
            print(job_details)
        
        # Applying for the selected job
        test_application = {
            "cv": "test_cv.pdf",
            "cover_letter": "test_cover_letter.pdf",
            "age": 25,
            "gender": "Male",
            "email": "test@example.com",
            "phone_number": "1234567890",
            "linkedin": "https://linkedin.com/test",
            "github": "https://github.com/test",
            "portfolio": "https://portfolio.com/test"
        }
        
        print("\n=== Applying for Job ===")
        application_response = apply_for_job("test_user", selected_job_id, test_application)
        for res in application_response:
            print(f"- {res}")
    else:
        print(search_results)

# Run debug test for searching, viewing job details, and applying
debug_search_and_apply_tests()
