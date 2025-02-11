'''
Implement a Tkinter UI dashboard with sections for user login, resume upload, and feedback display
Integrate `gui/login.py` for user login and registration
Integrate `ai/resume_review.py` for resume feedback
'''

'''Initialize Tkinter UI and launch the dashboard'''

from tkinter import *
from tkinter import ttk, filedialog
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('JobHive.dashboard')

try:
    from login import load_token, get_user_role, LoginApp
    logger.debug("Imported login modules directly")
except:
    try:
        from .login import load_token, get_user_role, LoginApp
        logger.debug("Imported login modules with relative import")
    except Exception as e:
        logger.error(f"Failed to import login modules: {str(e)}")
        pass

class DashboardApp:
    def __init__(self, root):
        logger.debug("Initializing DashboardApp")
        self.root = root
        self.setup_window()
        self.create_widgets()

    def create_widgets(self):
        logger.debug("Creating dashboard widgets")
        # Create main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
        main_frame.columnconfigure(0, weight=1)

        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(W, E), pady=(0, 20))
        
        ttk.Label(header_frame, text="JobHive Dashboard", style='Header.TLabel').pack(side=LEFT)
        ttk.Label(header_frame, text=f"Welcome, {get_user_role()}", style='TLabel').pack(side=RIGHT)

        # Resume section
        resume_frame = ttk.LabelFrame(main_frame, text="Resume Management", padding="10")
        resume_frame.grid(row=1, column=0, sticky=(W, E), pady=(0, 20))
        
        ttk.Button(resume_frame, text="Upload Resume", command=self.upload_resume).pack(side=LEFT, padx=5)
        ttk.Button(resume_frame, text="View Feedback", command=self.view_feedback).pack(side=LEFT, padx=5)

        # Job section
        job_frame = ttk.LabelFrame(main_frame, text="Job Management", padding="10")
        job_frame.grid(row=2, column=0, sticky=(W, E), pady=(0, 20))
        
        if get_user_role() == 'employer':
            ttk.Button(job_frame, text="Post New Job", command=self.post_job).pack(side=LEFT, padx=5)
            ttk.Button(job_frame, text="View Applications", command=self.view_applications).pack(side=LEFT, padx=5)
        else:
            ttk.Button(job_frame, text="Search Jobs", command=self.search_jobs).pack(side=LEFT, padx=5)
            ttk.Button(job_frame, text="My Applications", command=self.view_applications).pack(side=LEFT, padx=5)

    def upload_resume(self):
        file_path = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")]
        )
        if file_path:
            # TODO: Implement resume upload logic
            pass

    def view_feedback(self):
        # TODO: Implement feedback view logic
        pass

    def post_job(self):
        # TODO: Implement job posting logic
        pass

    def search_jobs(self):
        # TODO: Implement job search logic
        pass

    def view_applications(self):
        # TODO: Implement applications view logic
        pass

def main():
    logger.debug("Starting dashboard main()")
    root = Tk()
    
    # Check for user authentication
    logger.debug("Checking for existing token")
    if not load_token():
        logger.info("No valid token found, showing login window")
        login_app = LoginApp(root)
        root.mainloop()
        
        # Check token again after login attempt
        logger.debug("Checking token after login attempt")
        if not load_token():
            logger.warning("Still no valid token after login attempt, exiting")
            try:
                root.quit()
                root.destroy()
            except:
                pass
            return
    
    logger.info("Valid token found, starting dashboard")
    app = DashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()