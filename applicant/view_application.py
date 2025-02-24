# Import required libraries and modules
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

# Define the ApplicationViewer class for managing job applications
class ApplicationViewer: 
    def __init__(self):
        # Initialize console for rich text output
        self.console = Console()
        # Set project root directory
        self.project_root = Path(__file__).resolve().parent.parent
        # Initialize storage manager for handling files
        self.storage_manager = StorageManager()
        
        try:
            # Initialize Firebase if not already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(requests.get(
                    "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
                ).json())
                self.app = firebase_admin.initialize_app(cred, name='application_viewer')
            else:
                try:
                    # Try to get existing application viewer app
                    self.app = firebase_admin.get_app('application_viewer')
                except ValueError:
                    # Fallback to default app
                    self.app = firebase_admin.get_app()
                    
            # Initialize Firestore client
            self.db = firestore.client(app=self.app)
        except Exception as e:
            # Handle initialization errors
            self.console.print(f"[red]Error initializing Firebase: {str(e)}[/red]")
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

    def view_applications(self):
        try:
            # Get user ID from configuration file
            user_json_path = self.project_root / 'user.json'
            with open(user_json_path) as f:
                user_data = json.load(f)
            user_id = user_data['uid']

            # Fetch all applications for current user
            applications = self.db.collection('applications').where('user_id', '==', user_id).get()
            applications_list = list(applications)

            # Display message if no applications found
            if not applications_list:
                self.console.print(Panel("[yellow]You haven't applied for any jobs yet.[/yellow]", 
                                       title="Job Applications", border_style="red"))
                self.input_yellow("\nPress Enter to continue...")
                return

            while True:
                # Clear screen for new display
                self.clear_screen()
                # Create table for applications
                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Job Title", style="cyan")
                table.add_column("Application Date", style="white")
                table.add_column("Status", style="white")

                # Populate table with applications
                for idx, application in enumerate(applications_list, 1):
                    app_data = application.to_dict()
                    # Set color based on application status
                    status_color = {
                        'pending': 'yellow',
                        'accepted': 'green',
                        'rejected': 'red'
                    }.get(app_data['status'].lower(), 'white')

                    # Add row to table
                    table.add_row(
                        str(idx),
                        app_data['job_title'],
                        app_data['application_date'].strftime("%Y-%m-%d"),
                        f"[{status_color}]{app_data['status'].capitalize()}[/{status_color}]"
                    )

                # Display applications table
                self.console.print(Panel(table, title="Your Job Applications", border_style="blue"))
                
                # Show available options
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View application details (enter application number)")
                self.print_yellow("2. Cancel application (enter 'c' followed by application number)")
                self.print_yellow("3. Return (enter 'x')")
                
                # Get user choice
                choice = self.input_yellow("\nChoice: ").lower()

                # Process user choice
                if choice == 'x':
                    break
                elif choice.startswith('c'):
                    try:
                        # Handle application cancellation
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
                    # View application details
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
            # Handle any errors during application viewing
            self.console.print(f"[red]Error viewing applications: {str(e)}[/red]")
            self.input_yellow("\nPress Enter to continue...")

    def view_application_details(self, application_doc):
        try:
            # Get application data
            app_data = application_doc.to_dict()
            
            # Set status color based on application status
            status_color = {
                'pending': 'yellow',
                'accepted': 'green',
                'rejected': 'red'
            }.get(app_data['status'].lower(), 'white')

            # Prepare details for display
            details = [
                f"[bold cyan]Job Title:[/bold cyan] {app_data['job_title']}",
                f"[bold cyan]Application Date:[/bold cyan] {app_data['application_date'].strftime('%Y-%m-%d %H:%M:%S')}",
                f"[bold cyan]Status:[/bold cyan] [{status_color}]{app_data['status'].capitalize()}[/{status_color}]",
                f"[bold cyan]Email:[/bold cyan] {app_data['email']}",
                f"[bold cyan]Phone:[/bold cyan] {app_data['phone']}",
                f"[bold cyan]Age:[/bold cyan] {app_data['age']}",
                f"[bold cyan]Gender:[/bold cyan] {app_data['gender']}"
            ]

            # Add optional profile links if available
            if app_data.get('linkedin'):
                details.append(f"[bold cyan]LinkedIn:[/bold cyan] {app_data['linkedin']}")
            if app_data.get('github'):
                details.append(f"[bold cyan]GitHub:[/bold cyan] {app_data['github']}")
            if app_data.get('portfolio'):
                details.append(f"[bold cyan]Portfolio:[/bold cyan] {app_data['portfolio']}")

            # Add rejection reason if application was rejected
            if app_data['status'].lower() == 'rejected' and 'rejection_reason' in app_data:
                details.append(f"\n[bold red]Reason for rejection:[/bold red] {app_data['rejection_reason']}")

            # Add resume information if available
            if app_data.get('resume_path'):
                details.append(f"\n[bold cyan]Resume:[/bold cyan] {app_data['resume_path'].split('/')[-1]}")

            # Clear screen and display application details
            self.clear_screen()
            self.console.print(Panel(
                "\n".join(details),
                title="Application Details",
                border_style="blue",
                width=100
            ))

            # Show additional options for pending applications
            if app_data['status'].lower() == 'pending':
                self.print_yellow("\nYou can cancel this application from the main menu.")

        except Exception as e:
            # Handle errors in viewing application details
            self.console.print(f"[red]Error viewing application details: {str(e)}[/red]")

    def delete_application(self, application_doc):
        try:
            # Confirm deletion with user
            confirm = self.input_yellow("Are you sure you want to cancel this application? (y/n): ")
            if confirm.lower() != 'y':
                return

            # Get application data
            app_data = application_doc.to_dict()
            resume_path = app_data.get('resume_path')
            
            # Delete resume file if it exists
            if resume_path:
                if self.storage_manager.delete_file(resume_path):
                    self.console.print("[green]Resume file deleted successfully.[/green]")
                else:
                    self.console.print("[yellow]Warning: Could not delete resume file.[/yellow]")
    
            # Delete application document
            application_doc.reference.delete()
            self.console.print("[green]Application cancelled successfully.[/green]")
            
        except Exception as e:
            # Handle errors in application deletion
            self.console.print(f"[red]Error cancelling application: {str(e)}[/red]")

# Main function to run the application viewer
def main():
    viewer = ApplicationViewer()
    viewer.view_applications()

# Entry point of the script
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()