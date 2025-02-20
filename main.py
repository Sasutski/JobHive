from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
import time, json
from pathlib import Path
from employer.dashboard import EmployerDashboard
# from JobHive.applicant.dashboard import ApplicantDashboard
import subprocess
import sys

class JobHiveMain:
    def __init__(self):
        self.console = Console()
        # Get the absolute path to the project root
        self.project_root = Path(__file__).resolve().parent.parent

    def check_auth(self):
        """Check if user is authenticated by looking for user.json"""
        try:
            user_file = self.project_root / 'JobHive' / 'user.json'
            if user_file.exists():
                with open(user_file, 'r') as f:
                    user_data = json.load(f)
                    # Verify user data has required fields
                    if all(key in user_data for key in ['uid', 'email', 'user_type']):
                        return user_data
            return None
        except Exception as e:
            self.console.print(f"[red]Error checking authentication: {str(e)}[/red]")
            return None

    def display_welcome(self):
        """Display welcome screen"""
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold yellow]Welcome to JobHive[/bold yellow]\n"
            "[blue]Your Ultimate Job Matching Platform[/blue]",
            box=box.DOUBLE,
            padding=(1, 20)
        ))

    def launch_auth(self):
        """Launch authentication script as a separate process"""
        auth_path = self.project_root / 'JobHive' / 'authentication.py'
        try:
            # Check if auth_path exists before running
            if not auth_path.exists():
                raise FileNotFoundError(f"Authentication script not found at {auth_path}")
            
            subprocess.run([sys.executable, str(auth_path)], check=True)
            
            # Give a small delay to ensure file operations are complete
            time.sleep(0.5)
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]Authentication process failed: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Failed to start authentication: {e}[/red]")
            return False
        return True

    def run(self):
        """Main application loop"""
        while True:
            try:
                self.display_welcome()
                user = self.check_auth()

                if not user:
                    self.console.print("\n[yellow]Please authenticate to continue[/yellow]")
                    self.console.print("\n[cyan]Launching authentication system...[/cyan]")
                    time.sleep(1)
                    
                    if not self.launch_auth():
                        if Prompt.ask(
                            "\nWould you like to try again?",
                            choices=["y", "n"],
                            default="y"
                        ) == "n":
                            break
                        continue
                        
                    user = self.check_auth()
                    if not user:
                        continue

                # User is authenticated at this point
                if user['user_type'] == 'employer':
                    self.console.print("[green]Loading Employer Dashboard...[/green]")
                    time.sleep(1)
                    employer_dashboard = EmployerDashboard()
                    employer_dashboard.run()
                elif user['user_type'] == 'applicant':
                    self.console.print("[green]Loading Applicant Dashboard...[/green]")
                    time.sleep(1)
                    self.console.print("[yellow]Applicant Dashboard is under construction[/yellow]")
                    time.sleep(2)
                else:
                    self.console.print("[red]Invalid user type! Please re-authenticate.[/red]")
                    time.sleep(1)
                    continue

                if Prompt.ask(
                    "\nWould you like to continue using JobHive?",
                    choices=["y", "n"],
                    default="y"
                ) == "n":
                    break

            except KeyboardInterrupt:
                if Prompt.ask(
                    "\n[yellow]Are you sure you want to exit?[/yellow]",
                    choices=["y", "n"],
                    default="n"
                ) == "y":
                    break
            except Exception as e:
                self.console.print(f"[red]An error occurred: {str(e)}[/red]")
                time.sleep(2)
                if Prompt.ask(
                    "\nWould you like to try again?",
                    choices=["y", "n"],
                    default="y"
                ) == "n":
                    break

        self.console.print("\n[yellow]Thank you for using JobHive![/yellow]")
        time.sleep(1)

if __name__ == "__main__":
    app = JobHiveMain()
    app.run()