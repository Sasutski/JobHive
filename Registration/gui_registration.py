import tkinter as tk
from tkinter import ttk, messagebox
import os

class RegistrationApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.create_main_layout()
        self.create_form()
        self.create_illustration()

    def setup_window(self):
        self.root.title("JobHive Registration")
        # Set window size and position
        window_width = 1200
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg="#ffffff")
        self.root.resizable(True, True)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Black.TButton',
            background='black',
            foreground='white',
            font=('Arial', 14, 'bold'),
            padding=(50, 12))
        style.map('Black.TButton',
            background=[('active', '#333333'), ('pressed', '#1a1a1a')],
            foreground=[('active', 'white'), ('pressed', 'white')])

    def create_main_layout(self):
        self.main_frame = tk.Frame(self.root, bg="#ffffff")
        self.main_frame.pack(expand=True, fill="both", padx=80, pady=50)

        # Left side - Form
        self.form_frame = tk.Frame(self.main_frame, bg="#ffffff")
        self.form_frame.pack(side="left", expand=True, fill="both", padx=(0, 60))

        # Heading
        self.create_heading()

    def create_heading(self):
        tk.Label(
            self.form_frame,
            text="Ready to start your\nsuccess story?",
            font=("Arial", 40, "bold"),
            bg="#ffffff",
            fg="#333333",
            justify="left"
        ).pack(anchor="w", pady=(0, 20))

        tk.Label(
            self.form_frame,
            text="Create your account and start your journey to finding your dream job today!",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#666666",
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(0, 40))

    def create_form(self):
        # Store entry widgets
        self.entries = {}
        
        # Create form fields
        fields = [
            ("full_name", "Full Name"),
            ("email", "Email Address"),
            ("password", "Password"),
            ("confirm_password", "Confirm Password")
        ]

        for field_id, label in fields:
            entry = self.create_form_field(label)
            self.entries[field_id] = entry
            if 'password' in field_id:
                entry.configure(show='•')

        # Terms and conditions
        self.terms_var = tk.BooleanVar()
        self.create_terms_checkbox()

        # Sign up button
        self.create_signup_button()

    def create_form_field(self, label_text):
        frame = tk.Frame(self.form_frame, bg="#ffffff")
        frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            frame,
            text=label_text,
            font=("Arial", 11, "bold"),
            fg="#333333",
            bg="#ffffff"
        ).pack(anchor="w")

        entry = tk.Entry(
            frame,
            font=("Arial", 12),
            relief="solid",
            bd=1,
            bg="#f8f9fa",
            fg="#333333"
        )
        entry.configure(highlightthickness=1, highlightbackground="#e1e1e1", highlightcolor="#3498db")
        entry.pack(fill="x", pady=(5, 0))
        return entry

    def create_terms_checkbox(self):
        terms_frame = tk.Frame(self.form_frame, bg="#ffffff")
        terms_frame.pack(fill="x", pady=(20, 0))

        self.terms_check = tk.Checkbutton(
            terms_frame,
            text="I agree to the",
            variable=self.terms_var,
            bg="#ffffff",
            fg="#333333"
        )
        self.terms_check.pack(side="left")

        terms_link = tk.Label(
            terms_frame,
            text="Terms & Conditions",
            fg="#3498db",
            cursor="hand2",
            bg="#ffffff"
        )
        terms_link.pack(side="left")
        terms_link.bind('<Button-1>', self.show_terms)

    def create_signup_button(self):
        signup_button = ttk.Button(
            self.form_frame,
            text="Sign up",
            style='Black.TButton',
            cursor="hand2",
            command=self.validate_and_submit
        )
        signup_button.pack(anchor="w", pady=30)

    def create_illustration(self):
        self.illustration_frame = tk.Frame(self.main_frame, bg="#ffffff")
        self.illustration_frame.pack(side="right", expand=True, fill="both")

        canvas = tk.Canvas(
            self.illustration_frame,
            width=500,
            height=500,
            bg="#f0f5ff",
            highlightthickness=0
        )
        canvas.pack(expand=True, pady=20)

        # Create decorative elements
        canvas.create_rectangle(50, 50, 450, 450, fill="#e6eeff", outline="")
        canvas.create_text(
            250, 250,
            text="JobHive",
            font=("Arial", 24, "bold"),
            fill="#3498db"
        )

    def validate_and_submit(self):
        # Get form values
        values = {field: entry.get().strip() for field, entry in self.entries.items()}

        # Validation
        if any(not value for value in values.values()):
            messagebox.showerror("Error", "All fields are required")
            return

        if not self.validate_email(values['email']):
            messagebox.showerror("Error", "Please enter a valid email address")
            return

        if values['password'] != values['confirm_password']:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if len(values['password']) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return

        if not self.terms_var.get():
            messagebox.showerror("Error", "Please accept the terms and conditions")
            return

        # If all validation passes
        messagebox.showinfo("Success", "Registration successful!")
        self.clear_form()

    def validate_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def show_terms(self, event):
        terms_text = """Terms and Conditions\n\n
1. By using JobHive, you agree to these terms and conditions.
2. We respect your privacy and protect your personal information.
3. You must provide accurate information during registration.
4. You are responsible for maintaining the confidentiality of your account.
5. JobHive reserves the right to modify these terms at any time."""
        
        terms_window = tk.Toplevel(self.root)
        terms_window.title("Terms & Conditions")
        terms_window.geometry("600x400")
        
        text_widget = tk.Text(terms_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.insert("1.0", terms_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True)

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.terms_var.set(False)

def main():
    try:
        root = tk.Tk()
        root.update_idletasks()
        app = RegistrationApp(root)
        root.lift()
        root.focus_force()
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()