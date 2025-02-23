# JobHive/employer/review_applicants.py

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import os, sys, requests, platform, subprocess
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.storage_manager import StorageManager

class ApplicationReviewer:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        self.storage_manager = StorageManager()
        
        try:
            # Get the service account key
            service_account_key = requests.get(
                "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
            ).json()
            
            # Check if any Firebase app exists
            try:
                self.app = firebase_admin.get_app()
            except ValueError:
                # If no app exists, initialize a new one
                cred = credentials.Certificate(service_account_key)
                self.app = firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            
        except Exception as e:
            self.console.print(f"[red]Error initializing Firebase: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")
            sys.exit(1)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_yellow(self, text):
        self.console.print(f"[bold yellow]{text}[/bold yellow]")

    def input_yellow(self, prompt):
        return self.console.input(f"[bold yellow]{prompt}[/bold yellow]")

    def review_applications(self):
        try:
            while True:
                self.clear_screen()
                # Get all jobs posted by the employer
                jobs = self.db.collection('jobs').get()
                jobs_list = list(jobs)

                if not jobs_list:
                    self.console.print(Panel("[yellow]No jobs posted yet[/yellow]", 
                                          title="Jobs", border_style="red"))
                    self.input_yellow("\nPress Enter to return...")
                    break

                # Create table to display jobs
                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Job Title", style="cyan")
                table.add_column("Status", style="white")

                for idx, job in enumerate(jobs_list, 1):
                    job_data = job.to_dict()
                    table.add_row(
                        str(idx),
                        job_data['title'],
                        job_data.get('status', 'Active')
                    )

                self.console.print(Panel(table, title="Your Posted Jobs", border_style="blue"))
                
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View applications (enter job number)")
                self.print_yellow("2. Return to dashboard (enter 'x')")
                
                choice = self.input_yellow("\nChoice: ").lower()

                if choice == 'x':
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(jobs_list):
                        self.view_job_applications(jobs_list[idx])
                    else:
                        self.console.print("[red]Invalid job number. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                else:
                    self.console.print("[red]Invalid input. Please try again.[/red]")
                    self.input_yellow("\nPress Enter to continue...")

        except Exception as e:
            self.console.print(f"[red]Error reviewing applications: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def view_job_applications(self, job_doc):
        try:
            while True:
                self.clear_screen()
                job_data = job_doc.to_dict()
                applications = self.db.collection('applications').where('job_id', '==', job_doc.id).get()
                applications_list = list(applications)

                if not applications_list:
                    self.console.print(Panel(f"[yellow]No applications yet for {job_data['title']}[/yellow]", 
                                          title="Applications", border_style="red"))
                    self.input_yellow("\nPress Enter to continue...")
                    return

                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Applicant", style="cyan")
                table.add_column("Date Applied", style="white")
                table.add_column("Status", style="white")

                for idx, application in enumerate(applications_list, 1):
                    app_data = application.to_dict()
                    status_color = {
                        'pending': 'yellow',
                        'accepted': 'green',
                        'rejected': 'red'
                    }.get(app_data['status'].lower(), 'white')

                    table.add_row(
                        str(idx),
                        app_data['email'],
                        app_data['application_date'].strftime("%Y-%m-%d"),
                        f"[{status_color}]{app_data['status'].capitalize()}[/{status_color}]"
                    )

                self.console.print(Panel(table, title=f"Applications for {job_data['title']}", border_style="blue"))
                
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View application details (enter application number)")
                self.print_yellow("2. Return (enter 'x')")
                
                choice = self.input_yellow("\nChoice: ").lower()

                if choice == 'x':
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(applications_list):
                        self.review_application_details(applications_list[idx])
                    else:
                        self.console.print("[red]Invalid application number. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                else:
                    self.console.print("[red]Invalid input. Please try again.[/red]")
                    self.input_yellow("\nPress Enter to continue...")

        except Exception as e:
            self.console.print(f"[red]Error viewing job applications: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def review_applications(self):
        try:
            while True:
                self.clear_screen()
                # Get all jobs posted by the employer
                jobs = self.db.collection('jobs').get()
                jobs_list = list(jobs)
    
                if not jobs_list:
                    self.console.print(Panel("[yellow]No jobs posted yet[/yellow]", 
                                          title="Jobs", border_style="red"))
                    self.input_yellow("\nPress Enter to return...")
                    break
    
                # Create table to display jobs
                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Job Title", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Applicants", style="green")
    
                for idx, job in enumerate(jobs_list, 1):
                    job_data = job.to_dict()
                    # Convert Firestore timestamp to string format
                    posted_date = job_data.get('posted_date')

    
                    applicant_count = len(list(self.db.collection('applications')
                                            .where('job_id', '==', job.id)
                                            .get()))
                    
                    table.add_row(
                        str(idx),
                        job_data['title'],
                        job_data.get('status', 'Active'),
                        f"[green]{applicant_count}[/green]"
                    )
    
                self.console.print(Panel(table, title="Your Posted Jobs", border_style="blue"))
                
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View applications (enter job number)")
                self.print_yellow("2. Return to dashboard (enter 'x')")
                
                choice = self.input_yellow("\nChoice: ").lower()
    
                if choice == 'x':
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(jobs_list):
                        self.view_job_applications(jobs_list[idx])
                    else:
                        self.console.print("[red]Invalid job number. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                else:
                    self.console.print("[red]Invalid input. Please try again.[/red]")
                    self.input_yellow("\nPress Enter to continue...")
    
        except Exception as e:
            self.console.print(f"[red]Error reviewing applications: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def download_resume(self, app_data):
        """Download and optionally view the applicant's resume."""
        try:
            resume_path = app_data.get('resume_path')
            if not resume_path:
                self.console.print("[red]Resume path not found![/red]")
                self.input_yellow("\nPress Enter to continue...")
                return
    
            # Get original filename from the path
            original_filename = resume_path.split('/')[-1]
            
            # Create downloads directory in project root if it doesn't exist
            downloads_dir = self.project_root / 'downloads'
            downloads_dir.mkdir(exist_ok=True)
            
            # Set save path
            save_path = str(downloads_dir / original_filename)
            
            # Show download progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("[cyan]Downloading resume...", total=None)
                
                # Download the file using StorageManager
                if self.storage_manager.download_file(resume_path, save_path):
                    self.console.print(f"[green]Resume downloaded successfully to: {save_path}[/green]")
                    
                    # Ask if user wants to open the file
                    if self.input_yellow("\nWould you like to open the resume? (y/n): ").lower() == 'y':
                        try:
                            if platform.system() == 'Darwin':  # macOS
                                subprocess.run(['open', save_path])
                            elif platform.system() == 'Windows':
                                os.startfile(save_path)
                            else:  # Linux
                                subprocess.run(['xdg-open', save_path])
                        except Exception as e:
                            self.console.print(f"[red]Error opening file: {str(e)}[/red]")
                else:
                    self.console.print("[red]Failed to download resume.[/red]")
            
            self.input_yellow("\nPress Enter to continue...")
    
        except Exception as e:
            self.console.print(f"[red]Error downloading resume: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def download_resume(self, app_data):
        """Download and optionally view the applicant's resume."""
        try:
            resume_path = app_data.get('resume_path')
            if not resume_path:
                self.console.print("[red]Resume path not found![/red]")
                self.input_yellow("\nPress Enter to continue...")
                return
    
            # Get original filename from the path
            original_filename = resume_path.split('/')[-1]
            
            # Let employer choose download location
            self.print_yellow("\nWhere would you like to save the resume?")
            self.print_yellow("1. Downloads folder")
            self.print_yellow("2. Desktop")
            self.print_yellow("3. Custom location")
            
            choice = self.input_yellow("\nEnter your choice (1-3): ")
            
            if choice == "1":
                # Save to Downloads folder
                downloads_path = str(Path.home() / "Downloads" / original_filename)
                save_path = downloads_path
            elif choice == "2":
                # Save to Desktop
                desktop_path = str(Path.home() / "Desktop" / original_filename)
                save_path = desktop_path
            elif choice == "3":
                # Custom location
                self.print_yellow("\nEnter the full path where you want to save the resume:")
                self.print_yellow(f"(Default filename: {original_filename})")
                custom_path = input().strip()
                
                if not custom_path:
                    self.console.print("[red]No path provided. Operation cancelled.[/red]")
                    return
                    
                # If user provided just a directory, append the filename
                custom_path = Path(custom_path)
                if custom_path.is_dir():
                    save_path = str(custom_path / original_filename)
                else:
                    save_path = str(custom_path)
            else:
                self.console.print("[red]Invalid choice. Operation cancelled.[/red]")
                return
    
            # Create directory if it doesn't exist
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
            # Download the file first
            if self.storage_manager.download_file(resume_path, save_path):
                self.console.print(f"[green]Resume downloaded successfully to: {save_path}[/green]")
                
                # Ask if user wants to open the file
                if self.input_yellow("\nWould you like to open the resume? (y/n): ").lower() == 'y':
                    try:
                        if platform.system() == 'Darwin':  # macOS
                            subprocess.run(['open', save_path])
                        elif platform.system() == 'Windows':
                            os.startfile(save_path)
                        else:  # Linux
                            subprocess.run(['xdg-open', save_path])
                    except Exception as e:
                        self.console.print(f"[red]Error opening file: {str(e)}[/red]")
            else:
                self.console.print("[red]Failed to download resume.[/red]")
            
            self.input_yellow("\nPress Enter to continue...")
    
        except Exception as e:
            self.console.print(f"[red]Error downloading resume: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def update_application_status(self, application_id, status):
        try:
            self.db.collection('applications').document(application_id).update({
                'status': status
            })
        except Exception as e:
            self.console.print(f"[red]Error updating application status: {str(e)}[/red]")

def main():
    reviewer = ApplicationReviewer()
    reviewer.review_applications()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()