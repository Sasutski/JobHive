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
from config import FIREBASE_CONFIG

# Define the ApplicationReviewer class for managing job applications from employer's perspective
class ApplicationReviewer:
    def __init__(self):
        # Initialize console for rich text output
        self.console = Console()
        # Set project root directory
        self.project_root = Path(__file__).resolve().parent.parent
        # Initialize storage manager for handling files
        self.storage_manager = StorageManager()
        
        try:
            # Get the service account key
            service_account_key = requests.get(FIREBASE_CONFIG['service_account_url']).json()
            
            # Check if any Firebase app exists
            try:
                self.app = firebase_admin.get_app()
            except ValueError:
                # If no app exists, initialize a new one
                cred = credentials.Certificate(service_account_key)
                self.app = firebase_admin.initialize_app(cred)
            
            # Initialize Firestore client
            self.db = firestore.client()
            
        except Exception as e:
            self.console.print(f"[red]Error initializing Firebase: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")
            sys.exit(1)

    def clear_screen(self):
        # Clear terminal screen based on OS
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_yellow(self, text):
        # Print text in yellow color
        self.console.print(f"[bold yellow]{text}[/bold yellow]")

    def input_yellow(self, prompt):
        # Get user input with yellow prompt
        return self.console.input(f"[bold yellow]{prompt}[/bold yellow]")

    def review_applications(self):
        try:
            while True:
                self.clear_screen()
                # Get all jobs posted by the employer
                # Get all jobs posted by the employer
                jobs = self.db.collection('jobs').get()
                jobs_list = list(jobs)
    
                # Display message if no jobs found
                if not jobs_list:
                    self.console.print(Panel("[yellow]No jobs posted yet[/yellow]", 
                                          title="Jobs", border_style="red"))
                    self.input_yellow("\nPress Enter to return...")
                    break
    
                # Create table to display jobs
                # Create table to display jobs
                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Job Title", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Applicants", style="green")
    
                # Populate table with job information
                for idx, job in enumerate(jobs_list, 1):
                    job_data = job.to_dict()
                    applicant_count = len(list(self.db.collection('applications')
                                            .where('job_id', '==', job.id)
                                            .get()))
                    
                    table.add_row(
                        str(idx),
                        job_data['title'],
                        job_data.get('status', 'Active'),
                        f"[green]{applicant_count}[/green]"
                    )
    
                # Display jobs table and options
                self.console.print(Panel(table, title="Your Posted Jobs", border_style="blue"))
                
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View applications (enter job number)")
                self.print_yellow("2. Return to dashboard (enter 'x')")
                
                # Process user choice
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
    
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Network error: Unable to fetch applications. {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")
        except firestore.exceptions.FirebaseError as e:
            self.console.print(f"[red]Database error: Unable to access applications. {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")
        except Exception as e:
            self.console.print(f"[red]Unexpected error while reviewing applications: {str(e)}[/red]")
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

                # Create table to display jobs
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
                
                # Process user choice
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

    def review_application_details(self, application_doc):
        try:
            self.clear_screen()
            app_data = application_doc.to_dict()
            
            status_color = {
                'pending': 'yellow',
                'accepted': 'green',
                'rejected': 'red'
            }.get(app_data['status'].lower(), 'white')

            details = [
                f"[bold cyan]Applicant Name:[/bold cyan] {app_data.get('user_name', 'N/A')}",
                f"[bold cyan]Email:[/bold cyan] {app_data['email']}",
                f"[bold cyan]Phone:[/bold cyan] {app_data['phone']}",
                f"[bold cyan]Age:[/bold cyan] {app_data['age']}",
                f"[bold cyan]Gender:[/bold cyan] {app_data['gender']}",
                f"[bold cyan]Application Date:[/bold cyan] {app_data['application_date'].strftime('%Y-%m-%d %H:%M:%S')}",
                f"[bold cyan]Status:[/bold cyan] [{status_color}]{app_data['status'].capitalize()}[/{status_color}]"
            ]

            # Add optional fields if they exist
            if app_data.get('linkedin'):
                details.append(f"[bold cyan]LinkedIn:[/bold cyan] {app_data['linkedin']}")
            if app_data.get('github'):
                details.append(f"[bold cyan]GitHub:[/bold cyan] {app_data['github']}")
            if app_data.get('portfolio'):
                details.append(f"[bold cyan]Portfolio:[/bold cyan] {app_data['portfolio']}")

            # Add rejection reason if application was rejected
            if app_data['status'].lower() == 'rejected' and 'rejection_reason' in app_data:
                details.append(f"\n[bold red]Reason for rejection:[/bold red] {app_data['rejection_reason']}")

            self.console.print(Panel(
                "\n".join(details),
                title="Application Details",
                border_style="blue",
                width=100
            ))

            self.print_yellow("\nOptions:")
            if app_data['status'].lower() == 'pending':
                self.print_yellow("1. Accept application")
                self.print_yellow("2. Reject application")
            self.print_yellow("3. Download resume")
            self.print_yellow("4. Return")
            
            choice = self.input_yellow("\nChoice: ")
            
            if choice == "1" and app_data['status'].lower() == 'pending':
                if self.update_application_status(application_doc, "accepted"):
                    self.console.print("[green]Application accepted successfully![/green]")
                    
            elif choice == "2" and app_data['status'].lower() == 'pending':
                self.print_yellow("\nPlease provide a reason for rejection:")
                self.print_yellow("1. Not suitable due to experience")
                self.print_yellow("2. Not suitable due to qualifications")
                self.print_yellow("3. Not suitable due to age")
                self.print_yellow("4. Position already filled")
                self.print_yellow("5. Other (custom reason)")
                
                reason_choice = self.input_yellow("\nSelect reason (1-5): ")
                
                rejection_reasons = {
                    "1": "Not suitable due to experience level",
                    "2": "Not suitable due to qualifications",
                    "3": "Not suitable due to age requirements",
                    "4": "Position has been filled",
                    "5": None  # Will be set to custom reason
                }
                
                rejection_message = rejection_reasons.get(reason_choice)
                
                if reason_choice == "5":
                    rejection_message = self.input_yellow("Enter custom rejection reason: ")
                
                if rejection_message and self.update_application_status(application_doc, "rejected", rejection_message):
                    self.console.print("[green]Application rejected successfully![/green]")
                
            elif choice == "3":
                self.download_resume(app_data)
                
            self.input_yellow("\nPress Enter to continue...")
            
        except Exception as e:
            self.console.print(f"[red]Error reviewing application: {str(e)}[/red]")
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
            
            choice = self.input_yellow("\nEnter your choice (1-2): ")
            
            if choice == "1":
                # Save to Downloads folder
                save_path = str(Path.home() / "Downloads" / original_filename)
            elif choice == "2":
                # Save to Desktop
                save_path = str(Path.home() / "Desktop" / original_filename)
            else:
                # Default to desktop for invalid choice
                self.console.print("[red]Invalid choice. Saving to desktop.[/red]")
                save_path = str(Path.home() / "Desktop" / original_filename)
    
            # Create directory if it doesn't exist
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
            # Download and save the resume file
            if self.storage_manager.download_file(resume_path, save_path):
                self.console.print(f"[green]Resume downloaded successfully to: {save_path}[/green]")
                
                # Offer to open the downloaded file
                if self.input_yellow("\nWould you like to open the resume? (y/n): ").lower() == 'y':
                    try:
                        # Open file based on operating system
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
            
    
        except Exception as e:
            # Handle errors in resume download
            self.console.print(f"[red]Error downloading resume: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def update_application_status(self, application_doc, status, message=None):
        """Update application status and add rejection message if applicable."""
        try:
            # Prepare update data
            update_data = {'status': status}
            
            # Add rejection message if status is 'rejected' and message is provided
            if status.lower() == 'rejected' and message:
                update_data['rejection_reason'] = message

            # Update the application document
            application_doc.reference.update(update_data)
            return True
        except Exception as e:
            # Handle errors in status update
            self.console.print(f"[red]Error updating application status: {str(e)}[/red]")
            return False

# Main function to run the application reviewer
def main():
    reviewer = ApplicationReviewer()
    reviewer.review_applications()

# Entry point of the script
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()