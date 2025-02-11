'''
Implement a Tkinter UI dashboard with sections for user login, resume upload, and feedback display
Integrate `gui/login.py` for user login and registration
Integrate `ai/resume_review.py` for resume feedback
'''

from tkinter import *
from tkinter import ttk, filedialog
from login import load_token, get_user_role, LoginApp

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.root.title("JobHive Dashboard")
        self.root.configure(bg='#f5f6fa')
        
        # Set custom style
        style = ttk.Style()
        style.configure('TFrame', background='#2c3e50')
        style.configure('TLabel', background='#2c3e50', font=('Helvetica', 10), foreground='#ffffff')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=5, foreground='#ffffff')
        style.configure('Header.TLabel', font=('Helvetica', 24, 'bold'), foreground='#ffffff')
        style.configure('Section.TLabel', font=('Helvetica', 16, 'bold'), foreground='#ffffff')
        
        # Make window responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.configure(bg='#2c3e50')

    def create_widgets(self):
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
    root = Tk()
    
    # Check for user authentication
    if not load_token():
        login_app = LoginApp(root)
        root.mainloop()
        
        # If still no token after login attempt, exit gracefully
        if not load_token():
            try:
                root.quit()
                root.destroy()
            except:
                pass
            return
    
    # Start dashboard
    app = DashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()