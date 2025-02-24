# Import required libraries and modules for UI, navigation, and authentication
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import sys
import time
import os
import json
from pathlib import Path

# Import employer-specific modules for different functionalities
from .post_job import JobPoster, main as post_job_main
from .employer_jobs import EmployerJobs, main as employer_jobs_main
from .job_view import JobViewer, main as job_view_main
from .review_applicants import main as review_applicants_main

# Add parent directory to system path for importing authentication module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from authentication import AuthenticationCLI, main as auth_main_loop

# Define the EmployerDashboard class for managing employer interface and navigation
class EmployerDashboard:
    def __init__(self):
        # Initialize console for rich text output
        self.console = Console()
        # Set project root directory
        self.project_root = Path(__file__).resolve().parent.parent
        # Initialize authentication CLI
        self.auth_cli = AuthenticationCLI()
        # Set default employer ID (should be updated on login)
        self.employer_id = "test_employer_id"  # This should be set when user logs in

    def check_session(self):
        """Check if user is still logged in and is an employer"""
        try:
            # Read and verify user data from configuration file
            with open(self.project_root / 'user.json', 'r') as f:
                user_data = json.load(f)
                return user_data.get('user_type') == 'employer'
        except:
            return False

    def clear_screen(self):
        # Clear terminal screen based on OS
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.clear()

    def create_header(self):
        # Create dashboard header with styling
        header_text = Text("Employer Dashboard", style="bold white on blue", justify="center")
        return Panel(header_text, box=box.DOUBLE, padding=(1, 1))

    def create_menu(self):
        # Define and create menu options for the dashboard
        menu_items = [
            "[1] Post New Job",
            "[2] View Posted Jobs",
            "[3] Review Applicants",
            "[4] View Job Market",
            "[5] Account Settings",
            "[x] Exit"
        ]
        menu_text = Text("\n".join(menu_items), justify="left")
        return Panel(menu_text, title="Menu Options", box=box.ROUNDED, padding=(1, 1))

    def loading_animation(self):
        # Display loading animation during page transitions
        with self.console.status("[bold blue]Loading...", spinner="dots"):
            time.sleep(1.5)

    def redirect_to_page(self, choice):
        # Verify user session before processing
        if not self.check_session():
            return "logout"
            
        # Show loading animation during transition
        self.loading_animation()
        self.clear_screen()
        
        try:
            # Handle different menu options
            if choice == "1":
                self.console.print("[bold green]Redirecting to Post Job page...")
                post_job_main()
                return "post_job"
                
            elif choice == "2":
                self.console.print("[bold green]Viewing Posted Jobs...")
                employer_jobs_main()
                return "view_jobs"
                
            elif choice == "3":
                self.console.print("[bold green]Redirecting to Review Applicants page...")
                review_applicants_main()
                return "review_applicants"
                
            elif choice == "4":
                self.console.print("[bold green]Redirecting to Job Market View...")
                job_view_main()
                return "job_market"
                
            elif choice == "5":
                self.console.print("[bold green]Opening Account Settings...")
                auth_main_loop()
                if not self.check_session():  # Check if user logged out or changed type
                    return "logout"
                return "settings"
                
        except Exception as e:
            # Handle and display any errors during redirection
            self.console.print(f"[bold red]Error: {str(e)}")
            time.sleep(2)
            return None

    def display_dashboard(self):
        # Clear screen and display dashboard interface
        self.clear_screen()
        self.console.print(self.create_header())
        self.console.print(self.create_menu())

    def run(self):
        while True:
            if not self.check_session():
                self.console.print("[yellow]Session ended. Returning to main menu...[/yellow]")
                time.sleep(1)
                return "logout"
                
            try:
                self.display_dashboard()
                choice = self.console.input("\n[bold yellow]Enter your choice (1-5, x to exit): ")
                
                if choice.lower() == "x":
                    return "exit"
                    
                elif choice in ["1", "2", "3", "4", "5"]:
                    result = self.redirect_to_page(choice)
                    if result == "logout":
                        return "logout"
                    if result:
                        self.clear_screen()
                else:
                    self.console.print("[bold red]Invalid choice! Please try again.")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                return "exit"
            except Exception as e:
                self.console.print(f"\n[bold red]An error occurred: {str(e)}")
                time.sleep(2)

def main():
    dashboard = EmployerDashboard()
    try:
        result = dashboard.run()
        if result == "logout":
            Console().print("[yellow]Logged out successfully.[/yellow]")
        elif result == "exit":
            Console().print("[yellow]Exiting dashboard...[/yellow]")
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()
    except Exception as e:
        Console().print(f"\n[bold red]An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()