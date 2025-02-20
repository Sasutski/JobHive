# JobHive/employer/post_job.py
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import json, requests, time, sys
from pathlib import Path

class JobPostManager:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).parent
        self.API_KEY = "AIzaSyAcwreE9k06t8HtJ6vhSOblwCskAEkWRWQ"
        
        # Initialize Firebase
        cred = credentials.Certificate(requests.get(
            "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
        ).json())
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.current_user = self._load_session()

    def _load_session(self):
        try:
            with open(Path(__file__).parent.parent / 'user.json', 'r') as f:
                return json.load(f)
        except:
            return None

    def create_job_post(self):
        job_data = {
            'title': Prompt.ask("Enter job title"),
            'responsibilities': Prompt.ask("Enter day-to-day responsibilities"),
            'qualifications': Prompt.ask("Enter required qualifications"),
            'location': Prompt.ask("Enter location (or 'remote')"),
            'job_type': Prompt.ask("Enter job type", choices=["full-time", "part-time", "contract", "internship"]),
            'pay_range': Prompt.ask("Enter pay range"),
            'benefits': Prompt.ask("Enter benefits"),
            'employer_id': self.current_user['uid'],
            'created_at': firestore.SERVER_TIMESTAMP
        }

        try:
            self.db.collection('jobs').add(job_data)
            self.console.print("[green]Job posted successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]Error posting job: {str(e)}[/red]")

    def view_my_jobs(self):
        try:
            jobs = self.db.collection('jobs').where('employer_id', '==', self.current_user['uid']).get()
            
            if not jobs:
                self.console.print("[yellow]No jobs found[/yellow]")
                return None

            job_table = Table(show_header=True, box=box.SIMPLE)
            job_table.add_column("Job ID", style="cyan")
            job_table.add_column("Title", style="white")
            job_table.add_column("Location", style="white")
            job_table.add_column("Type", style="white")
            
            for job in jobs:
                job_data = job.to_dict()
                job_table.add_row(
                    job.id,
                    job_data['title'],
                    job_data['location'],
                    job_data['job_type']
                )
            
            self.console.print(Panel(job_table, title="Your Posted Jobs", border_style="blue"))
            return jobs
        except Exception as e:
            self.console.print(f"[red]Error viewing jobs: {str(e)}[/red]")
            return None

    def edit_job(self):
        jobs = self.view_my_jobs()
        if not jobs:
            return

        job_id = Prompt.ask("Enter the Job ID you want to edit")
        
        try:
            job_ref = self.db.collection('jobs').document(job_id)
            job_data = job_ref.get()
            
            if not job_data.exists:
                self.console.print("[red]Job not found![/red]")
                return
                
            fields = {
                "1": "title",
                "2": "responsibilities",
                "3": "qualifications",
                "4": "location",
                "5": "job_type",
                "6": "pay_range",
                "7": "benefits"
            }
            
            self.console.print("\nWhat would you like to edit?")
            for key, value in fields.items():
                self.console.print(f"[cyan]{key}[/cyan]: {value}")
            
            field_choice = Prompt.ask("Choose field to edit", choices=list(fields.keys()))
            field = fields[field_choice]
            
            if field == "job_type":
                new_value = Prompt.ask(
                    f"Enter new {field}",
                    choices=["full-time", "part-time", "contract", "internship"]
                )
            else:
                new_value = Prompt.ask(f"Enter new {field}")
            
            job_ref.update({field: new_value})
            self.console.print("[green]Job updated successfully![/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error editing job: {str(e)}[/red]")

    def delete_job(self):
        jobs = self.view_my_jobs()
        if not jobs:
            return

        job_id = Prompt.ask("Enter the Job ID you want to delete")
        
        try:
            job_ref = self.db.collection('jobs').document(job_id)
            if not job_ref.get().exists:
                self.console.print("[red]Job not found![/red]")
                return
                
            if Prompt.ask("Are you sure you want to delete this job?", choices=["y", "n"]) == "y":
                job_ref.delete()
                self.console.print("[green]Job deleted successfully![/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error deleting job: {str(e)}[/red]")

def main():
    job_manager = JobPostManager()
    
    while True:
        job_manager.console.clear()
        job_manager.console.print(Panel.fit(
            "[bold yellow]Job Post Management[/bold yellow]",
            box=box.DOUBLE
        ))
        
        job_manager.console.print("\n[cyan]1[/cyan]: Create New Job Post")
        job_manager.console.print("[cyan]2[/cyan]: View My Jobs")
        job_manager.console.print("[cyan]3[/cyan]: Edit Job")
        job_manager.console.print("[cyan]4[/cyan]: Delete Job")
        job_manager.console.print("[cyan]5[/cyan]: Return to Dashboard")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            job_manager.create_job_post()
        elif choice == "2":
            job_manager.view_my_jobs()
        elif choice == "3":
            job_manager.edit_job()
        elif choice == "4":
            job_manager.delete_job()
        elif choice == "5":
            break
            
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()