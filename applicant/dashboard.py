from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import sys, time, os, json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from authentication import AuthenticationCLI, main as auth_main_loop
from .job_view import ApplicantJobViewer, main as job_view_main

class ApplicantDashboard:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        self.auth_cli = AuthenticationCLI()  # Initialize authentication system
        self.job_viewer = ApplicantJobViewer()

    def check_session(self):
        """Check if user is still logged in and is an applicant"""
        try:
            with open(self.project_root / 'user.json', 'r') as f:
                user_data = json.load(f)
                return user_data.get('user_type') == 'applicant'
        except:
            return False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.clear()

    def create_header(self):
        header_text = Text("Applicant Dashboard", style="bold white on blue", justify="center")
        return Panel(header_text, box=box.DOUBLE, padding=(1, 1))

    def create_menu(self):
        menu_items = [
            "[1] View and Apply for Available Jobs",
            "[2] View My Applications",
            "[3] Account Settings",
            "[x] Exit"
        ]
        menu_text = Text("\n".join(menu_items), justify="left")
        return Panel(menu_text, title="Menu Options", box=box.ROUNDED, padding=(1, 1))

    def loading_animation(self):
        with self.console.status("[bold blue]Loading...", spinner="dots"):
            time.sleep(1.5)

    def redirect_to_page(self, choice):
        if not self.check_session():
            return "logout"
            
        self.loading_animation()
        self.clear_screen()
        
        try:
            if choice == "1":
                self.console.print("[bold green]Redirecting to Job Listings...")
                job_view_main()
                return "job_view"
                
            elif choice == "2":
                self.console.print("[bold green]Redirecting to My Applications...")
                from .view_application import main as view_applications_main
                view_applications_main()
                return "my_applications"
                
            elif choice == "3":
                self.console.print("[bold green]Opening Account Settings...")
                auth_main_loop()  # This will handle all the authentication UI and logic
                if not self.check_session():  # Check if user logged out or changed type
                    return "logout"
                return "settings"
                
        except Exception as e:
            self.console.print(f"[bold red]Error: {str(e)}")
            time.sleep(2)
            return None

    def display_dashboard(self):
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
                choice = self.console.input("\n[bold yellow]Enter your choice (1-3, x to exit): ")
                
                if choice.lower() == "x":
                    return "exit"
                    
                elif choice in ["1", "2", "3"]:
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
    dashboard = ApplicantDashboard()
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