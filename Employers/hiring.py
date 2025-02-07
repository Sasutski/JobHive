# Dictionary to store all job listings
hiring_jobs = {}

def add_job_listing(title, requirements, experience_range, salary_ranges, locations, tags=None):
    """
    Add a new job listing to the hiring_jobs dictionary
    
    Parameters:
    - title (str): Job title
    - requirements (list): List of job requirements
    - experience_range (str): Required experience range (e.g., '1-5 years')
    - salary_ranges (dict): Dictionary containing entry_level, mid_level, and senior_level salary ranges
    - locations (list): List of job locations
    - tags (list): List of keywords describing the job (e.g., ['python', 'web development', 'remote'])
    """
    if not all([title, requirements, experience_range, salary_ranges, locations]):
        raise ValueError("All parameters are required")
        
    if not isinstance(salary_ranges, dict) or not all(level in salary_ranges 
        for level in ['entry_level', 'mid_level', 'senior_level']):
        raise ValueError("salary_ranges must be a dictionary with entry_level, mid_level, and senior_level")
    
    if tags is not None and not isinstance(tags, list):
        raise ValueError("tags must be a list of strings")
    
    hiring_jobs[title] = {
        "requirements": requirements,
        "experience_range": experience_range,
        "salary_range": salary_ranges,
        "locations": locations,
        "tags": tags or []
    }
    return True

def remove_job_listing(title):
    """
    Remove a job listing from the hiring_jobs dictionary
    
    Parameters:
    - title (str): Job title to remove
    """
    if title in hiring_jobs:
        del hiring_jobs[title]
        return True
    return False

def get_job_listing(title):
    """
    Get a specific job listing
    
    Parameters:
    - title (str): Job title to retrieve
    """
    return hiring_jobs.get(title)

def get_all_job_listings():
    """
    Get all job listings
    """
    return hiring_jobs

def update_job_listing(title, field, value):
    """
    Update a specific field in a job listing
    
    Parameters:
    - title (str): Job title to update
    - field (str): Field to update (requirements, experience_range, salary_range, locations, or tags)
    - value: New value for the field
    """
    if title not in hiring_jobs:
        return False
        
    if field not in ["requirements", "experience_range", "salary_range", "locations", "tags"]:
        return False
        
    hiring_jobs[title][field] = value
    return True

