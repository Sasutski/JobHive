from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import sys, time, os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from authentication import AuthenticationCLI
from .job_view import ApplicantJobViewer, main as job_view_main

class ApplicantDashboard:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        self.auth_cli = AuthenticationCLI()  # Initialize authentication system
        self.job_viewer = ApplicantJobViewer()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.clear()

    def create_header(self):
        header_text = Text("Applicant Dashboard", style="bold white on blue", justify="center")
        return Panel(header_text, box=box.DOUBLE, padding=(1, 1))

    def create_menu(self):
        menu_items = [
            "[1] View Available Jobs",
            "[2] Apply for Jobs",
            "[3] View My Applications",
            "[4] Account Settings",
            "[5] Exit"
        ]
        menu_text = Text("\n".join(menu_items), justify="left")
        return Panel(menu_text, title="Menu Options", box=box.ROUNDED, padding=(1, 1))

    def loading_animation(self):
        with self.console.status("[bold blue]Loading...", spinner="dots"):
            time.sleep(1.5)

    def redirect_to_page(self, choice):
        self.loading_animation()
        self.clear_screen()
        
        try:
            if choice == "1":
                self.console.print("[bold green]Redirecting to Job Listings...")
                job_view_main()
                return "job_view"
                
            elif choice == "2":
                self.console.print("[bold green]Redirecting to Job Application page...")
                from .apply_job import main as apply_job_main
                apply_job_main()
                return "apply_job"
                
            elif choice == "3":
                self.console.print("[bold green]Redirecting to My Applications...")
                from .my_applications import main as my_applications_main
                my_applications_main()
                return "my_applications"
                
            elif choice == "4":
                self.console.print("[bold green]Opening Account Settings...")
                result = self.auth_cli.main_loop()  # This will handle all the authentication UI and logic
                if not self.auth_cli.current_user:  # Check if user logged out
                    return "logout"
                return "settings"
                
        except Exception as e:
            self.console.print(f"[bold red]Error: {str(e)}")
            time.sleep(2)

    def display_dashboard(self):
        self.clear_screen()
        self.console.print(self.create_header())
        self.console.print(self.create_menu())

    def run(self):
        while True:
            try:
                self.display_dashboard()
                choice = self.console.input("\n[bold yellow]Enter your choice (1-5): ")
                
                if choice == "5":
                    break
                    
                elif choice in ["1", "2", "3", "4"]:
                    result = self.redirect_to_page(choice)
                    if result == "logout":
                        self.console.print("[bold blue]Logged out. Returning to login screen...")
                        time.sleep(2)
                        break
                    if result:
                        self.clear_screen()
                else:
                    self.console.print("[bold red]Invalid choice! Please try again.")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Program terminated by user.")
                break
            except Exception as e:
                self.console.print(f"\n[bold red]An error occurred: {str(e)}")
                time.sleep(2)

def main():
    dashboard = ApplicantDashboard()
    try:
        dashboard.run()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()
    except Exception as e:
        Console().print(f"\n[bold red]An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()