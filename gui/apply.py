import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

class JobApplication:
    def __init__(self):
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate("path/to/serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.user_data = {}

    def get_jobs(self):
        """Fetch all jobs from Firebase"""
        try:
            jobs_ref = self.db.collection('jobs')
            jobs = jobs_ref.stream()
            return [job.to_dict() for job in jobs]
        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return []

    def save_job(self, job_id, user_id):
        """Save a job for later"""
        try:
            saved_jobs_ref = self.db.collection('saved_jobs')
            saved_jobs_ref.add({
                'job_id': job_id,
                'user_id': user_id,
                'date_saved': datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error saving job: {e}")
            return False

    def get_saved_jobs(self, user_id):
        """Get all saved jobs for a user"""
        try:
            saved_jobs_ref = self.db.collection('saved_jobs')
            saved_jobs = saved_jobs_ref.where('user_id', '==', user_id).stream()
            return [job.to_dict() for job in saved_jobs]
        except Exception as e:
            print(f"Error fetching saved jobs: {e}")
            return []

    def submit_application(self, job_id, application_data):
        """Submit a job application"""
        required_fields = {
            'resume': str,  # URL or path to uploaded resume
            'cover_letter': str,  # URL or path to uploaded cover letter
            'email': str,
            'phone': str,
            'age': int,
            'gender': str
        }

        # Validate required fields
        for field, field_type in required_fields.items():
            if field not in application_data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(application_data[field], field_type):
                raise TypeError(f"Invalid type for {field}")

        # Optional fields validation
        optional_fields = {
            'linkedin_profile': str,
            'github_profile': str,
            'portfolio_website': str,
            'additional_info': str,
            'employer_questions': dict
        }

        try:
            # Get job details to check requirements
            job_ref = self.db.collection('jobs').document(job_id)
            job = job_ref.get().to_dict()

            # Validate optional requirements based on job specifications
            for req in job.get('requirements', []):
                if req in optional_fields and req not in application_data:
                    raise ValueError(f"Job requires {req} but it was not provided")

            # Submit application to Firebase
            applications_ref = self.db.collection('applications')
            application_data.update({
                'job_id': job_id,
                'submission_date': datetime.now(),
                'status': 'submitted'
            })
            
            applications_ref.add(application_data)
            return True

        except Exception as e:
            print(f"Error submitting application: {e}")
            return False

    def get_application_status(self, application_id):
        """Get the status of a submitted application"""
        try:
            application_ref = self.db.collection('applications').document(application_id)
            application = application_ref.get()
            if application.exists:
                return application.to_dict()['status']
            return None
        except Exception as e:
            print(f"Error getting application status: {e}")
            return None

# Example usage:
def main():
    job_app = JobApplication()
    
    # Example application data
    application_data = {
        'resume': 'uploads/resume.pdf',  # URL or path to uploaded resume
        'cover_letter': 'uploads/cover_letter.pdf',  # URL or path to uploaded cover letter
        'email': 'candidate@email.com',
        'phone': '+1234567890',
        'age': 25,
        'gender': 'Male',
        'linkedin_profile': 'https://linkedin.com/in/username',
        'github_profile': 'https://github.com/username',
        'portfolio_website': 'https://portfolio.com',
        'additional_info': 'Additional information here',
        'employer_questions': {
            'question1': 'answer1',
            'question2': 'answer2'
        }
    }

    # Get all jobs
    jobs = job_app.get_jobs()
    
    # Save a job for later
    job_app.save_job('job_id', 'user_id')
    
    # Submit application
    job_app.submit_application('job_id', application_data)
    
    # Check application status
    status = job_app.get_application_status('application_id')

if __name__ == "__main__":
    main()