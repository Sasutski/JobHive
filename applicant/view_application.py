from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import json, os, sys, requests
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.storage_manager import StorageManager

class ApplicationViewer: 
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        self.storage_manager = StorageManager()
        
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(requests.get(
                    "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
                ).json())
                self.app = firebase_admin.initialize_app(cred, name='application_viewer')
            else:
                try:
                    self.app = firebase_admin.get_app('application_viewer')
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

    def view_applications(self):
        try:
            # Get user ID from user.json
            user_json_path = self.project_root / 'user.json'
            with open(user_json_path) as f:
                user_data = json.load(f)
            user_id = user_data['uid']

            # Get all applications for this user
            applications = self.db.collection('applications').where('user_id', '==', user_id).get()
            applications_list = list(applications)

            if not applications_list:
                self.console.print(Panel("[yellow]You haven't applied for any jobs yet.[/yellow]", 
                                       title="Job Applications", border_style="red"))
                self.input_yellow("\nPress Enter to continue...")
                return

            while True:
                self.clear_screen()
                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Job Title", style="cyan")
                table.add_column("Application Date", style="white")
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
                        app_data['job_title'],
                        app_data['application_date'].strftime("%Y-%m-%d"),
                        f"[{status_color}]{app_data['status'].capitalize()}[/{status_color}]"
                    )

                self.console.print(Panel(table, title="Your Job Applications", border_style="blue"))
                
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View application details (enter application number)")
                self.print_yellow("2. Cancel application (enter 'c' followed by application number)")
                self.print_yellow("3. Return (enter 'x')")
                
                choice = self.input_yellow("\nChoice: ").lower()

                if choice == 'x':
                    break
                elif choice.startswith('c'):
                    try:
                        idx = int(choice[1:]) - 1
                        if 0 <= idx < len(applications_list):
                            app = applications_list[idx]
                            if app.to_dict()['status'].lower() == 'pending':
                                self.delete_application(app)
                                applications_list.pop(idx)
                            else:
                                self.console.print("[red]Can only cancel pending applications.[/red]")
                            self.input_yellow("\nPress Enter to continue...")
                        else:
                            self.console.print("[red]Invalid application number.[/red]")
                            self.input_yellow("\nPress Enter to continue...")
                    except ValueError:
                        self.console.print("[red]Invalid input format.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(applications_list):
                        self.view_application_details(applications_list[idx])
                        self.input_yellow("\nPress Enter to return to applications list...")
                    else:
                        self.console.print("[red]Invalid application number.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                else:
                    self.console.print("[red]Invalid input.[/red]")
                    self.input_yellow("\nPress Enter to continue...")

        except Exception as e:
            self.console.print(f"[red]Error viewing applications: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def view_application_details(self, application_doc):
        try:
            app_data = application_doc.to_dict()
            
            status_color = {
                'pending': 'yellow',
                'accepted': 'green',
                'rejected': 'red'
            }.get(app_data['status'].lower(), 'white')

            details = [
                f"[bold cyan]Job Title:[/bold cyan] {app_data['job_title']}",
                f"[bold cyan]Application Date:[/bold cyan] {app_data['application_date'].strftime('%Y-%m-%d %H:%M:%S')}",
                f"[bold cyan]Status:[/bold cyan] [{status_color}]{app_data['status'].capitalize()}[/{status_color}]",
                f"[bold cyan]Email:[/bold cyan] {app_data['email']}",
                f"[bold cyan]Phone:[/bold cyan] {app_data['phone']}",
                f"[bold cyan]Age:[/bold cyan] {app_data['age']}",
                f"[bold cyan]Gender:[/bold cyan] {app_data['gender']}"
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

            # Add resume information
            if app_data.get('resume_path'):
                details.append(f"\n[bold cyan]Resume:[/bold cyan] {app_data['resume_path'].split('/')[-1]}")

            self.clear_screen()
            self.console.print(Panel(
                "\n".join(details),
                title="Application Details",
                border_style="blue",
                width=100
            ))

            # Show additional options
            if app_data['status'].lower() == 'pending':
                self.print_yellow("\nYou can cancel this application from the main menu.")

        except Exception as e:
            self.console.print(f"[red]Error viewing application details: {str(e)}[/red]")

    def delete_application(self, application_doc):
        try:
            confirm = self.input_yellow("Are you sure you want to cancel this application? (y/n): ")
            if confirm.lower() != 'y':
                return

            # Get application data first
            app_data = application_doc.to_dict()
            resume_path = app_data.get('resume_path')
            
            # Delete the resume file from storage if path exists
            if resume_path:
                if self.storage_manager.delete_file(resume_path):
                    self.console.print("[green]Resume file deleted successfully.[/green]")
                else:
                    self.console.print("[yellow]Warning: Could not delete resume file.[/yellow]")
    
            # Delete the application document
            application_doc.reference.delete()
            self.console.print("[green]Application cancelled successfully.[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error cancelling application: {str(e)}[/red]")

def main():
    viewer = ApplicationViewer()
    viewer.view_applications()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()