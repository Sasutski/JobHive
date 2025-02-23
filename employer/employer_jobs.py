# JobHive/employer/employer_jobs.py
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import requests, time, sys, os, json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.storage_manager import StorageManager
from config import FIREBASE_CONFIG

class EmployerJobs:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        self.storage_manager = StorageManager()
        
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(requests.get(FIREBASE_CONFIG['service_account_url']).json())
                self.app = firebase_admin.initialize_app(cred, name='job_viewer')
            else:
                try:
                    self.app = firebase_admin.get_app('job_viewer')
                except ValueError:
                    self.app = firebase_admin.get_app()
                    
            self.db = firestore.client(app=self.app)
        except Exception as e:
            self.console.print(f"[red]Error initializing Firebase: {str(e)}[/red]")
            sys.exit(1)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_yellow(self, text):
        self.console.print(f"[bold yellow]{text}[/bold yellow]")

    def input_yellow(self, prompt):
        return self.console.input(f"[bold yellow]{prompt}[/bold yellow]")

    def view_all_jobs(self):
        try:
            # Get employer ID from user.json
            try:
                user_json_path = self.project_root / 'user.json'
                with open(user_json_path) as f:
                    user_data = json.load(f)
                employer_id = user_data.get('uid')
                
                if not employer_id:
                    raise ValueError("Employer ID not found in user.json")
                    
            except Exception as e:
                self.console.print(f"[red]Error loading user data: {str(e)}[/red]")
                self.input_yellow("\nPress Enter to continue...")
                return

            try:
                # Query Firestore directly with employer_id filter
                jobs_ref = self.db.collection('jobs')
                jobs = jobs_ref.where('employer_id', '==', employer_id).get()
                jobs_list = list(jobs)

            except Exception as e:
                self.console.print(f"[red]Error querying Firestore: {str(e)}[/red]")
                self.input_yellow("\nPress Enter to continue...")
                return

            if not jobs_list:
                self.console.print(Panel("[yellow]You haven't posted any jobs yet.[/yellow]", 
                                       title="Posted Jobs", border_style="red"))
                self.input_yellow("\nPress Enter to continue...")
                return

            while True:
                self.clear_screen()
                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Title", style="cyan")
                table.add_column("Type", style="white")
                table.add_column("Location", style="white")
                table.add_column("Salary Range", style="white")
                table.add_column("Posted Date", style="white")

                for idx, job in enumerate(jobs_list, 1):
                    job_data = job.to_dict()
                    posted_date = job_data.get('timestamp').strftime("%Y-%m-%d") if job_data.get('timestamp') else "N/A"
                    
                    table.add_row(
                        str(idx),
                        job_data.get('title', 'N/A'),
                        job_data.get('job_type', 'N/A'),
                        job_data.get('location', 'N/A'),
                        job_data.get('salary_range', 'N/A'),
                        posted_date
                    )

                self.console.print(Panel(table, title="Posted Jobs", border_style="blue"))
                
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View job details (enter job number)")
                self.print_yellow("2. Delete job (enter 'd' followed by job number)")
                self.print_yellow("3. Return (enter 'x')")
                
                choice = self.input_yellow("\nChoice: ").lower()

                if choice == 'x':
                    break
                elif choice.startswith('d'):
                    try:
                        idx = int(choice[1:]) - 1
                        if 0 <= idx < len(jobs_list):
                            if self.delete_job(jobs_list[idx]):
                                jobs_list.pop(idx)
                            self.input_yellow("\nPress Enter to return to jobs list...")
                        else:
                            self.console.print("[red]Invalid job number. Please try again.[/red]")
                            self.input_yellow("\nPress Enter to continue...")
                    except ValueError:
                        self.console.print("[red]Invalid input. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(jobs_list):
                        self.view_job_details(jobs_list[idx])
                        self.input_yellow("\nPress Enter to return to jobs list...")
                    else:
                        self.console.print("[red]Invalid job number. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                else:
                    self.console.print("[red]Invalid input. Please try again.[/red]")
                    self.input_yellow("\nPress Enter to continue...")

        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Network error: Unable to fetch jobs. {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")
        except firestore.exceptions.FirebaseError as e:
            self.console.print(f"[red]Database error: Unable to access jobs. {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")
        except Exception as e:
            self.console.print(f"[red]Unexpected error while viewing jobs: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def view_job_details(self, job_doc):
        try:
            job_data = job_doc.to_dict()
            
            details = [
                f"[bold cyan]Title:[/bold cyan] {job_data.get('title', 'N/A')}",
                f"[bold cyan]Type:[/bold cyan] {job_data.get('job_type', 'N/A')}",
                f"[bold cyan]Location:[/bold cyan] {job_data.get('location', 'N/A')}",
                f"[bold cyan]Salary Range:[/bold cyan] {job_data.get('salary_range', 'N/A')}",
                f"\n[bold cyan]Responsibilities:[/bold cyan]",
                *[f"• {resp}" for resp in job_data.get('responsibilities', '').split('\n') if resp],
                f"\n[bold cyan]Qualifications:[/bold cyan]",
                *[f"• {qual}" for qual in job_data.get('qualifications', '').split('\n') if qual],
                f"\n[bold cyan]Benefits:[/bold cyan]",
                *[f"• {benefit}" for benefit in job_data.get('benefits', '').split('\n') if benefit]
            ]

            self.clear_screen()
            self.console.print(Panel(
                "\n".join(details),
                title="Job Details",
                border_style="blue",
                width=100
            ))

        except Exception as e:
            self.console.print(f"[red]Error viewing job details: {str(e)}[/red]")

    def delete_job(self, job_doc):
        try:
            confirm = self.input_yellow("Are you sure you want to delete this job? (y/n): ")
            if confirm.lower() == 'y':
                # Get the job data and ID
                job_id = job_doc.id
                job_data = job_doc.to_dict()
                
                # Delete the model resume from storage if it exists
                model_resume_path = job_data.get('model_resume_path')
                if model_resume_path:
                    try:
                        if self.storage_manager.delete_file(model_resume_path):
                            self.console.print("[green]Associated resume file deleted successfully.[/green]")
                        else:
                            self.console.print("[yellow]Warning: Could not delete associated resume file.[/yellow]")
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Error deleting resume file: {str(e)}[/yellow]")
    
                # Delete the job document from Firestore
                self.db.collection('jobs').document(job_id).delete()
                self.console.print(f"[green]Job {job_id} has been successfully deleted.[/green]")
                return True
            return False
        except Exception as e:
            self.console.print(f"[red]Error deleting job: {str(e)}[/red]")
            return False

def main():
    viewer = EmployerJobs()
    viewer.view_all_jobs()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()