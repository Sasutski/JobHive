# JobHive/employer/post_job.py
from rich.console import Console
from rich.panel import Panel
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import requests
import time
import sys
import os
from pathlib import Path

class JobPoster:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        
        try:
            self.db = firestore.client()
        except ValueError:
            cred = credentials.Certificate(requests.get(
                "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
            ).json())
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_yellow(self, text):
        self.console.print(f"[bold yellow]{text}[/bold yellow]")

    def input_yellow(self, prompt):
        return self.console.input(f"[bold yellow]{prompt}[/bold yellow]")

    def post_job(self):
        try:
            self.clear_screen()
            self.console.print(Panel.fit(
                "[bold yellow]Post New Job[/bold yellow]",
                box=box.DOUBLE
            ))
            
            self.print_yellow("\nPlease enter the following job details:\n")
            
            title = self.input_yellow("Job Title: ").strip()
            while not title:
                self.console.print("[red]Job title cannot be empty.[/red]")
                title = self.input_yellow("Job Title: ").strip()

            self.print_yellow("\nJob Type Options:")
            self.print_yellow("1. Full-time")
            self.print_yellow("2. Part-time")
            self.print_yellow("3. Contract")
            self.print_yellow("4. Internship")
            
            job_type_map = {
                "1": "full-time",
                "2": "part-time",
                "3": "contract",
                "4": "internship"
            }
            
            while True:
                choice = self.input_yellow("\nSelect job type [1-4]: ")
                if choice in job_type_map:
                    job_type = job_type_map[choice]
                    break
                self.console.print("[red]Invalid choice. Please try again.[/red]")

            location = self.input_yellow("\nLocation: ").strip()
            while not location:
                self.console.print("[red]Location cannot be empty.[/red]")
                location = self.input_yellow("Location: ").strip()

            while True:
                try:
                    min_salary = int(self.input_yellow("\nMinimum Salary (in thousands USD): "))
                    if min_salary < 0:
                        self.console.print("[red]Salary cannot be negative.[/red]")
                        continue
                    
                    max_salary = int(self.input_yellow("Maximum Salary (in thousands USD): "))
                    if max_salary < min_salary:
                        self.console.print("[red]Maximum salary must be greater than minimum salary.[/red]")
                        continue
                    
                    salary_range = f"${min_salary}k - ${max_salary}k"
                    break
                except ValueError:
                    self.console.print("[red]Please enter valid numbers.[/red]")

            self.print_yellow("\nEnter job responsibilities (press Enter twice to finish):")
            responsibilities = []
            while True:
                line = self.input_yellow("")
                if not line and responsibilities:
                    break
                if line:
                    responsibilities.append(line)

            self.print_yellow("\nEnter qualifications (press Enter twice to finish):")
            qualifications = []
            while True:
                line = self.input_yellow("")
                if not line and qualifications:
                    break
                if line:
                    qualifications.append(line)

            self.print_yellow("\nEnter benefits (press Enter twice to finish):")
            benefits = []
            while True:
                line = self.input_yellow("")
                if not line and benefits:
                    break
                if line:
                    benefits.append(line)

            job_data = {
                'title': title,
                'job_type': job_type,
                'location': location,
                'min_salary': min_salary,
                'max_salary': max_salary,
                'salary_range': salary_range,
                'responsibilities': "\n".join(responsibilities),
                'qualifications': "\n".join(qualifications),
                'benefits': "\n".join(benefits),
                'timestamp': firestore.SERVER_TIMESTAMP
            }

            self.db.collection('jobs').add(job_data)
            
            self.clear_screen()
            self.console.print("[green]Job posted successfully![/green]")
            time.sleep(2)
            return True

        except Exception as e:
            self.console.print(f"[red]Error posting job: {str(e)}[/red]")
            time.sleep(2)
            return False

def main():
    poster = JobPoster()
    try:
        while True:
            poster.clear_screen()
            poster.console.print(Panel.fit(
                "[bold yellow]Job Posting Menu[/bold yellow]",
                box=box.DOUBLE
            ))
            
            poster.print_yellow("\n1: Post New Job")
            poster.print_yellow("2: Return to Dashboard")
            
            choice = poster.input_yellow("\nSelect an option [1/2]: ").strip()
            
            if choice == "1":
                poster.post_job()
            elif choice == "2":
                break
            else:
                poster.console.print("[red]Invalid choice. Please try again.[/red]")
                time.sleep(1)

    except KeyboardInterrupt:
        poster.console.print("\n[bold red]Program terminated by user.")
        sys.exit()

if __name__ == "__main__":
    main()