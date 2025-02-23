# JobHive/employer/post_job.py
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import requests, time, sys, os, json
from datetime import datetime
from pathlib import Path
import subprocess
import platform
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.storage_manager import StorageManager
from config import FIREBASE_CONFIG

class JobPoster:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        self.storage_manager = StorageManager()
        
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(requests.get(FIREBASE_CONFIG['service_account_url']).json())
                self.app = firebase_admin.initialize_app(cred)
            else:
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

    def validate_input(self, prompt, validator=None, error_msg=None):
        """Generic input validator with custom validation logic."""
        while True:
            value = self.input_yellow(prompt)
            if not validator or validator(value):
                return value
            self.console.print(f"[red]{error_msg or 'Invalid input. Please try again.'}[/red]")

    def open_file_dialog(self):
        """Opens a native file dialog and returns the selected file path."""
        system = platform.system()
        
        try:
            if system == 'Darwin':  # macOS
                script = '''
                tell application "System Events"
                    activate
                    try
                        set theFile to choose file with prompt "Select a resume file:" default location (path to desktop) of type {"PDF", "DOC", "DOCX"}
                        POSIX path of theFile
                    on error errorMessage
                        return ""
                    end try
                end tell
                '''
                process = subprocess.Popen(['osascript', '-e', script],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                result = stdout.decode('utf-8').strip()
                if result:
                    return result
                return None
                
            elif system == 'Windows':
                script = '''
                Add-Type -AssemblyName System.Windows.Forms
                $f = New-Object System.Windows.Forms.OpenFileDialog
                $f.Filter = "Document files (*.pdf;*.doc;*.docx)|*.pdf;*.doc;*.docx"
                if ($f.ShowDialog() -eq 'OK') { $f.FileName } else { '' }
                '''
                process = subprocess.Popen(['powershell', '-Command', script],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                result = stdout.decode('utf-8').strip()
                if result:
                    return result
                return None
                
            else:  # Linux or other systems
                self.print_yellow("\nNative file dialog not supported on this system.")
                self.print_yellow("Please enter the file path manually (or press Enter to cancel):")
                path = input().strip()
                return path if path else None
                
        except (KeyboardInterrupt, EOFError):
            return None
        except Exception as e:
            self.console.print(f"[red]Error in file dialog: {str(e)}[/red]")
            return None

    def submit_job(self, job_data):
        try:
            with open(self.project_root / 'user.json') as f:
                user_data = json.load(f)
            employer_id = user_data.get('uid')

            job_data['employer_id'] = employer_id
            job_data['timestamp'] = firestore.SERVER_TIMESTAMP

            job_ref = self.db.collection('jobs').document()
            job_ref.set(job_data)
            return True
        except Exception as e:
            self.console.print(f"[red]Error submitting job: {str(e)}[/red]")
            return False

    def collect_multiline_input(self, prompt, min_items=1):
        """Collect multiline input with validation."""
        items = []
        self.print_yellow(f"\n{prompt} (press Enter twice when done):")
        while True:
            item = input().strip()
            if not item:
                if len(items) >= min_items:
                    break
                self.console.print(f"[yellow]Please enter at least {min_items} item(s).[/yellow]")
                continue
            items.append(item)
        return '\n'.join(items)

    def post_job(self):
        try:
            self.clear_screen()
            self.console.print(Panel("[bold cyan]Post a New Job[/bold cyan]", box=box.DOUBLE))
            job_data = {}

            # Basic job details with validation
            job_data['title'] = self.validate_input(
                "Enter job title: ",
                lambda x: len(x.strip()) >= 3,
                "Job title must be at least 3 characters long."
            )

            # Job type selection with improved UI
            job_types = ["full-time", "part-time", "contract", "internship"]
            self.console.print(Panel("\n".join(
                f"[cyan]{idx}.[/cyan] {jtype.title()}"
                for idx, jtype in enumerate(job_types, 1)
            ), title="Job Types", border_style="cyan"))

            while True:
                try:
                    type_choice = int(self.input_yellow("Select job type (1-4): "))
                    if 1 <= type_choice <= 4:
                        job_data['job_type'] = job_types[type_choice - 1]
                        break
                    self.console.print("[red]Please select a number between 1 and 4.[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a valid number.[/red]")

            job_data['location'] = self.validate_input(
                "\nEnter job location: ",
                lambda x: len(x.strip()) >= 2,
                "Location must be at least 2 characters long."
            )

            # Salary range with improved validation
            while True:
                try:
                    min_salary = int(self.input_yellow("\nEnter minimum salary (in thousands USD): "))
                    max_salary = int(self.input_yellow("Enter maximum salary (in thousands USD): "))
                    
                    if min_salary < 0 or max_salary < 0:
                        self.console.print("[red]Salary cannot be negative.[/red]")
                        continue
                    if min_salary > max_salary:
                        self.console.print("[red]Minimum salary cannot be greater than maximum salary.[/red]")
                        continue
                        
                    job_data['min_salary'] = min_salary
                    job_data['max_salary'] = max_salary
                    job_data['salary_range'] = f"${min_salary}k - ${max_salary}k"
                    break
                except ValueError:
                    self.console.print("[red]Please enter valid numbers for salary.[/red]")

            # Detailed job information with minimum requirements
            self.print_yellow("\nCollecting detailed information...")
            
            job_data['responsibilities'] = self.collect_multiline_input(
                "Enter job responsibilities", min_items=2)
            
            job_data['qualifications'] = self.collect_multiline_input(
                "Enter job qualifications", min_items=2)
            
            job_data['benefits'] = self.collect_multiline_input(
                "Enter job benefits", min_items=1)

            # Model resume upload
            file_path = None  # Initialize file_path variable
            if self.input_yellow("\nWould you like to upload a model resume? (y/n): ").lower() == 'y':
                self.print_yellow("\nOpening file selector...")
                sys.stdin = open(os.devnull, 'r')
                try:
                    file_path = self.open_file_dialog()
                    
                    if file_path and os.path.exists(file_path):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = os.path.basename(file_path)
                        model_resume_path = f"model_resumes/{timestamp}_{filename}"
                        job_data['model_resume_path'] = model_resume_path
                        self.console.print(f"[green]Selected file: {filename}[/green]")
                    else:
                        self.print_yellow("\nNo file selected or file not found.")
                        
                except Exception as e:
                    self.print_yellow(f"\nError selecting file: {str(e)}")
                finally:
                    sys.stdin = sys.__stdin__

            # Review and submit
            self.clear_screen()
            self.console.print(Panel(
                "\n".join(f"[cyan]{k}:[/cyan] {v}" for k, v in job_data.items()),
                title="Job Details",
                border_style="yellow"
            ))

            if self.input_yellow("\nSubmit job posting? (y/n): ").lower() == 'y':
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("[cyan]Submitting job posting...", total=None)
                    try:
                        file_uploaded = False
                        
                        if 'model_resume_path' in job_data:
                            progress.update(task, description="[cyan]Uploading resume...")
                            file_uploaded = self.storage_manager.upload_file(file_path, "model_resumes")
                            
                            if not file_uploaded:
                                self.print_yellow("\nFile upload failed. Job posting cancelled.")
                                return
                                
                            job_data['model_resume_path'] = file_uploaded['path']
                            job_data['model_resume_url'] = file_uploaded.get('url')
            
                        progress.update(task, description="[cyan]Saving job details...")
                        
                        if self.submit_job(job_data):
                            self.console.print("\n[green]✓ Job posted successfully![/green]")
                        else:
                            if file_uploaded:
                                self.storage_manager.delete_file(job_data['model_resume_path'])
                            self.print_yellow("\nFailed to post job. Any uploaded files were removed.")
                        
                    except Exception as e:
                        if file_uploaded:
                            self.storage_manager.delete_file(job_data['model_resume_path'])
                        self.print_yellow(f"\nError occurred: {str(e)}. Any uploaded files were removed.")
            else:
                self.print_yellow("\nJob posting cancelled.")

        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Network error: Unable to connect to server. {str(e)}[/red]")
        except firestore.exceptions.FirebaseError as e:
            self.console.print(f"[red]Database error: Unable to post job. {str(e)}[/red]")
        except ValueError as e:
            self.console.print(f"[red]Invalid input: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]Unexpected error while posting job: {str(e)}[/red]")
        finally:
            self.input_yellow("\nPress Enter to continue...")

def main():
    try:
        poster = JobPoster()
        poster.post_job()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()
    except Exception as e:
        Console().print(f"\n[bold red]Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()