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
        self.root.configure(bg='#ffffff')
        
        # Set custom style
        style = ttk.Style()
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabel', background='#ffffff', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=10)
        style.configure('Header.TLabel', font=('Helvetica', 24, 'bold'), foreground='#2c3e50')
        style.configure('Section.TLabel', font=('Helvetica', 16, 'bold'), foreground='#34495e')
        style.configure('Card.TFrame', background='#f8f9fa', relief='solid', borderwidth=1)
        style.configure('Primary.TButton', background='#3498db', foreground='#ffffff')
        style.configure('Secondary.TButton', background='#95a5a6', foreground='#ffffff')
        
        # Make window responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def create_widgets(self):
        # Create main container with padding
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
        main_frame.columnconfigure(0, weight=1)

        # Header section with welcome message
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(W, E), pady=(0, 30))
        
        ttk.Label(header_frame, text="JobHive Dashboard", style='Header.TLabel').pack(side=LEFT)
        ttk.Label(header_frame, text=f"Welcome, {get_user_role()}", style='Section.TLabel').pack(side=RIGHT)

        # Resume section with card-like appearance
        resume_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="20")
        resume_frame.grid(row=1, column=0, sticky=(W, E), pady=(0, 20))
        
        ttk.Label(resume_frame, text="Resume Management", style='Section.TLabel').pack(anchor=W, pady=(0, 15))
        button_frame = ttk.Frame(resume_frame)
        button_frame.pack(fill=X)
        
        ttk.Button(button_frame, text="Upload Resume", style='Primary.TButton', command=self.upload_resume).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="View Feedback", style='Secondary.TButton', command=self.view_feedback).pack(side=LEFT, padx=5)

        # Job section with card-like appearance
        job_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="20")
        job_frame.grid(row=2, column=0, sticky=(W, E), pady=(0, 20))
        
        ttk.Label(job_frame, text="Job Management", style='Section.TLabel').pack(anchor=W, pady=(0, 15))
        button_frame = ttk.Frame(job_frame)
        button_frame.pack(fill=X)
        
        if get_user_role() == 'employer':
            ttk.Button(button_frame, text="Post New Job", style='Primary.TButton', command=self.post_job).pack(side=LEFT, padx=5)
            ttk.Button(button_frame, text="View Applications", style='Secondary.TButton', command=self.view_applications).pack(side=LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="Search Jobs", style='Primary.TButton', command=self.search_jobs).pack(side=LEFT, padx=5)
            ttk.Button(button_frame, text="My Applications", style='Secondary.TButton', command=self.view_applications).pack(side=LEFT, padx=5)

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

# Check for user authentication
root = Tk()
if not load_token():
    login_app = LoginApp(root)
    root.mainloop()
    
    if not load_token():
        root.destroy()
        exit()

# Start dashboard
app = DashboardApp(root)
root.mainloop()