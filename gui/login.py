# Firebase authentication and user management module for JobHive
# Handles user login, registration, and token persistence
import pyrebase
import json
import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Firebase configuration for project authentication and database access
config = {
  'apiKey': "AIzaSyCO19uyfT37NbNmzJGDvigl47Sv7ejC2SI",
  'authDomain': "jobhive-d66d3.firebaseapp.com",
  'projectId': "jobhive-d66d3",
  'storageBucket': "jobhive-d66d3.firebasestorage.app",
  'messagingSenderId': "658456142271",
  'appId': "1:658456142271:web:6b4a726a61e165e23e410a",
  'measurementId': "G-PF2SBL24EM",
  'databaseURL': "https://jobhive-d66d3-default-rtdb.asia-southeast1.firebasedatabase.app"
}

# Initialize Firebase services
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()  # Authentication instance
db = firebase.database()  # Realtime database instance

# Global variables for session management
firsttime = False  # Flag to track if user just registered
user_token = None  # Current user's authentication token
user_role = None   # Current user's role (applicant/employer)
TOKEN_FILE = 'user_token.json'  # File to persist user session

class LoginApp:
    """Main login application class that handles the GUI and authentication flow"""
    def __init__(self, root):
        """Initialize the login window with root Tkinter instance"""
        self.root = root
        self.setup_window("JobHive Login", 400, 300)
        self.create_widgets()
    
    def setup_window(self, title, width, height):
        self.root.title(title)
        self.root.configure(bg='#2c3e50')
        self.root.focus_force()
        
        # Set custom style with modern color scheme
        style = ttk.Style()
        style.configure('TFrame', background='#2c3e50')
        style.configure('TLabel', background='#2c3e50', font=('Helvetica', 11), foreground='#ffffff')
        style.configure('TButton', font=('Helvetica', 11, 'bold'), padding=6)
        style.configure('Title.TLabel', font=('Helvetica', 24, 'bold'), foreground='#ffffff')
        style.configure('TEntry', padding=8, relief='flat', foreground='#ffffff', background='#34495e')
        style.configure('Focus.TEntry', padding=8, relief='solid', foreground='#ffffff', background='#34495e')
        
        # Configure button styles
        style.configure('Accent.TButton', background='#3498db', foreground='#ffffff')
        style.configure('Secondary.TButton', background='#2c3e50', foreground='#ffffff')
        style.map('Accent.TButton',
                  background=[('active', '#2980b9'), ('pressed', '#2980b9')],
                  relief=[('pressed', 'sunken')])
        style.map('Secondary.TButton',
                  background=[('active', '#34495e'), ('pressed', '#34495e')],
                  relief=[('pressed', 'sunken')])
        
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add window shadow and border
        self.root.overrideredirect(False)
        self.root.attributes('-alpha', 0.0)
        self.root.update_idletasks()
        self.root.attributes('-alpha', 1.0)
    
    def create_entry_field(self, parent, label_text, row, show=None):
        """Create a labeled entry field in the form
        
        Args:
            parent: Parent widget to place the entry field
            label_text (str): Label text for the field
            row (int): Grid row position
            show (str, optional): Character to show instead of actual input (for passwords)
        
        Returns:
            StringVar: Variable bound to the entry field
        """
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=W, pady=8)
        var = StringVar()
        entry = ttk.Entry(parent, textvariable=var, width=30, show=show)
        entry.grid(row=row, column=1, pady=8, padx=(10, 0))
        
        # Add focus animation
        def on_focus_in(event):
            entry.configure(style='Focus.TEntry')
        def on_focus_out(event):
            entry.configure(style='TEntry')
            
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        return var
    
    def create_widgets(self):
        """Create and arrange all GUI widgets for the login window"""
        # Create main frame with padding and shadow effect
        main_frame = ttk.Frame(self.root, padding="30 20 30 20", style='TFrame')
        main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Add title label with custom style
        title_label = ttk.Label(main_frame, text="Welcome to JobHive", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Create styled email and password entry fields
        self.email_var = self.create_entry_field(main_frame, "Email:", 1)
        self.password_var = self.create_entry_field(main_frame, "Password:", 2, show="*")
        
        # Create button frame with modern styling
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.grid(row=3, column=0, columnspan=2, pady=30)
        
        # Style buttons
        style = ttk.Style()
        style.configure('Accent.TButton', background='#3498db', foreground='white')
        style.configure('Secondary.TButton', background='#95a5a6')
        
        login_btn = ttk.Button(button_frame, text="Login", command=self.login, style='Accent.TButton')
        signup_btn = ttk.Button(button_frame, text="Sign Up", command=self.show_signup_window, style='Secondary.TButton')
        
        login_btn.grid(row=0, column=0, padx=10)
        signup_btn.grid(row=0, column=1, padx=10)
    
    def handle_auth_error(self, error):
        """Handle Firebase authentication errors and display appropriate messages
        
        Args:
            error: Firebase authentication error
        """
        error_message = str(error)
        if "INVALID_PASSWORD" in error_message:
            messagebox.showerror("Error", "Invalid password. Please try again.")
        elif "EMAIL_EXISTS" in error_message:
            messagebox.showerror("Error", "Email already exists")
        elif "EMAIL_NOT_FOUND" in error_message:
            messagebox.showerror("Error", "Email not found. Please sign up first.")
        else:
            messagebox.showerror("Error", "Authentication failed. Please try again or contact support.")
    
    def login(self):
        """Handle user login process with Firebase authentication"""
        email = self.email_var.get()
        password = self.password_var.get()
        
        # Validate input fields
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            # Authenticate with Firebase
            log_in = auth.sign_in_with_email_and_password(email, password)
            global user_token, user_role
            user_token = log_in['idToken']
            
            # Retrieve user role from database
            user_data = db.child("users").order_by_child("email").equal_to(email).get()
            for user in user_data.each():
                user_role = user.val().get('role')
                save_token(user_token, user_role)
                messagebox.showinfo("Success", f"Successfully signed in as {user_role}")
                self.root.quit()
                return
            
            messagebox.showerror("Error", "User profile not found. Please contact support.")
        except Exception as e:
            self.handle_auth_error(e)
    
    def show_signup_window(self):
        """Create and display the signup window with registration form"""
        signup = Toplevel(self.root)
        signup.title("JobHive Sign Up")
        self.setup_window_for_toplevel(signup, 400, 500)
        
        # Create main frame for signup form with modern styling
        main_frame = ttk.Frame(signup, padding="30 20 30 20", style='TFrame')
        main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Add form title with custom style
        ttk.Label(main_frame, text="Create Account", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Create form fields
        email_var = self.create_entry_field(main_frame, "Email:", 1)
        password_var = self.create_entry_field(main_frame, "Password:", 2, show="*")
        
        # Create role selection radio buttons
        role_var = StringVar(value="applicant")
        ttk.Label(main_frame, text="Role:").grid(row=3, column=0, sticky=W, pady=5)
        role_frame = ttk.Frame(main_frame)
        role_frame.grid(row=3, column=1, pady=5)
        ttk.Radiobutton(role_frame, text="Applicant", variable=role_var, value="applicant").pack(side=LEFT)
        ttk.Radiobutton(role_frame, text="Employer", variable=role_var, value="employer").pack(side=LEFT)
        
        # Create additional profile fields
        name_var = self.create_entry_field(main_frame, "Name:", 4)
        age_var = self.create_entry_field(main_frame, "Age:", 5)
        location_var = self.create_entry_field(main_frame, "Location:", 6)
        education_var = self.create_entry_field(main_frame, "Education:", 7)
        
        def register():
            """Handle user registration process"""
            # Collect form data
            fields = {
                'email': email_var.get().strip(),
                'password': password_var.get().strip(),
                'role': role_var.get().strip(),
                'name': name_var.get().strip(),
                'age': age_var.get().strip(),
                'location': location_var.get().strip(),
                'education': education_var.get().strip()
            }
            
            # Check each field individually
            empty_fields = [field for field, value in fields.items() if not value]
            if empty_fields:
                error_message = "Please fill in the following fields:\n- " + "\n- ".join(empty_fields)
                messagebox.showerror("Error", error_message)
                return
            
            try:
                # Create new user in Firebase Authentication
                sign_up = auth.create_user_with_email_and_password(fields['email'], fields['password'])
                global user_token, user_role, firsttime
                user_token = sign_up['idToken']
                user_role = fields['role']
                firsttime = True
                
                # Store user profile in Firebase Database
                db.child("users").push(fields)
                save_token(user_token, user_role)
                messagebox.showinfo("Success", f"Successfully signed up as {fields['role']}")
                signup.destroy()
                self.root.quit()
            except Exception as e:
                self.handle_auth_error(e)
        
        ttk.Button(main_frame, text="Register", command=register).grid(row=8, column=0, columnspan=2, pady=20)
    
    def setup_window_for_toplevel(self, window, width, height):
        """Configure properties for a top-level window
        
        Args:
            window: Toplevel window instance
            width (int): Window width
            height (int): Window height
        """
        window.configure(bg='#2c3e50')
        window.transient(self.root)
        window.grab_set()
        
        # Center window on screen
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

def save_token(token, role):
    """Save user authentication token and role to file
    
    Args:
        token (str): User's Firebase authentication token
        role (str): User's role (applicant/employer)
    """
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'token': token, 'role': role}, f)

def load_token():
    """Load and validate saved authentication token
    
    Returns:
        bool: True if valid token loaded, False otherwise
    """
    global user_token, user_role
    try:
        # Check if token file exists
        if not os.path.exists(TOKEN_FILE):
            return False
            
        # Load token and role from file
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            user_token = data.get('token')
            user_role = data.get('role')
            
            if not user_token or not user_role:
                return False
            
            try:
                # Verify token with Firebase
                user_info = auth.get_account_info(user_token)
                if not user_info or 'users' not in user_info:
                    return False
                
                # Verify user role matches database
                email = user_info['users'][0]['email']
                user_data = db.child("users").order_by_child("email").equal_to(email).get()
                
                for user in user_data.each():
                    if user.val().get('role') == user_role:
                        return True
                return False
            except:
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                return False
    except:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        return False

def is_logged_in():
    """Check if user is currently logged in
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    return user_token is not None

def get_user_role():
    """Get current user's role
    
    Returns:
        str: User's role if logged in, None otherwise
    """
    return user_role if user_role else None

if __name__ == "__main__":
    root = Tk()
    app = LoginApp(root)
    root.mainloop()