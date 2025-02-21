# JobHive/employer/review_applicants.py

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import json, os, sys, requests
from pathlib import Path
import webbrowser

class ApplicationReviewer:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(requests.get(
                    "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
                ).json())
                self.app = firebase_admin.initialize_app(cred, name='application_reviewer')
            else:
                try:
                    self.app = firebase_admin.get_app('application_reviewer')
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

    def review_applications(self):
        try:
            # Get employer ID from user.json
            user_json_path = self.project_root / 'user.json'
            with open(user_json_path) as f:
                user_data = json.load(f)
            employer_id = user_data['uid']

            # Get all jobs posted by this employer
            jobs = self.db.collection('jobs').where('employer_id', '==', employer_id).get()
            
            while True:
                self.clear_screen()
                job_list = list(jobs)
                
                if not job_list:
                    self.console.print(Panel("[yellow]You haven't posted any jobs yet.[/yellow]", 
                                          title="Posted Jobs", border_style="red"))
                    self.input_yellow("\nPress Enter to continue...")
                    return

                # Display all jobs
                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Job Title", style="cyan")
                table.add_column("Applications", style="white")
                table.add_column("Status", style="white")

                for idx, job in enumerate(job_list, 1):
                    job_data = job.to_dict()
                    applications = self.db.collection('applications').where('job_id', '==', job.id).get()
                    app_count = len(list(applications))
                    
                    table.add_row(
                        str(idx),
                        job_data['title'],
                        str(app_count),
                        "[green]Active[/green]" if job_data.get('active', True) else "[red]Inactive[/red]"
                    )

                self.console.print(Panel(table, title="Posted Jobs", border_style="blue"))
                
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View applications for a job (enter job number)")
                self.print_yellow("2. Return (enter 'x')")
                
                choice = self.input_yellow("\nChoice: ").lower()

                if choice == 'x':
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(job_list):
                        self.view_job_applications(job_list[idx])
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
                        self.review_application(applications_list[idx])
                    else:
                        self.console.print("[red]Invalid application number. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                else:
                    self.console.print("[red]Invalid input. Please try again.[/red]")
                    self.input_yellow("\nPress Enter to continue...")

        except Exception as e:
            self.console.print(f"[red]Error viewing job applications: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def review_application(self, application_doc):
        try:
            while True:
                self.clear_screen()
                app_data = application_doc.to_dict()
                
                status_color = {
                    'pending': 'yellow',
                    'accepted': 'green',
                    'rejected': 'red'
                }.get(app_data['status'].lower(), 'white')

                details = [
                    f"[bold cyan]Applicant Email:[/bold cyan] {app_data['email']}",
                    f"[bold cyan]Application Date:[/bold cyan] {app_data['application_date'].strftime('%Y-%m-%d %H:%M:%S')}",
                    f"[bold cyan]Status:[/bold cyan] [{status_color}]{app_data['status'].capitalize()}[/{status_color}]",
                    f"[bold cyan]Phone:[/bold cyan] {app_data['phone']}",
                    f"[bold cyan]Age:[/bold cyan] {app_data['age']}",
                    f"[bold cyan]Gender:[/bold cyan] {app_data['gender']}",
                    f"[bold cyan]Resume:[/bold cyan] {app_data['resume_path']}"
                ]

                if app_data.get('linkedin'):
                    details.append(f"[bold cyan]LinkedIn:[/bold cyan] {app_data['linkedin']}")
                if app_data.get('github'):
                    details.append(f"[bold cyan]GitHub:[/bold cyan] {app_data['github']}")
                if app_data.get('portfolio'):
                    details.append(f"[bold cyan]Portfolio:[/bold cyan] {app_data['portfolio']}")

                self.console.print(Panel(
                    "\n".join(details),
                    title="Application Review",
                    border_style="blue",
                    width=100
                ))

                self.print_yellow("\nOptions:")
                self.print_yellow("1. Accept application")
                self.print_yellow("2. Reject application")
                self.print_yellow("3. View resume")
                self.print_yellow("4. Return (enter 'x')")
                
                choice = self.input_yellow("\nChoice: ").lower()

                if choice == 'x':
                    break
                elif choice == '1':
                    self.update_application_status(application_doc.id, 'accepted')
                    self.console.print("[green]Application accepted successfully![/green]")
                    self.input_yellow("\nPress Enter to continue...")
                    break
                elif choice == '2':
                    self.update_application_status(application_doc.id, 'rejected')
                    self.console.print("[red]Application rejected.[/red]")
                    self.input_yellow("\nPress Enter to continue...")
                    break
                elif choice == '3':
                    # Open resume in default browser/application
                    webbrowser.open(app_data['resume_path'])
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")
                    self.input_yellow("\nPress Enter to continue...")

        except Exception as e:
            self.console.print(f"[red]Error reviewing application: {str(e)}[/red]")
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