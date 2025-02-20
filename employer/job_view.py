# JobHive/employer/job_view.py
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import requests, time, sys, warnings, os
from pathlib import Path
from difflib import SequenceMatcher

warnings.filterwarnings("ignore", category=UserWarning, module="google.cloud.firestore_v1.base_collection")

class JobViewer:
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

    def _title_similarity(self, title1, title2):
        title1 = title1.lower()
        title2 = title2.lower()
        
        if title1 in title2 or title2 in title1:
            return 1.0
            
        return SequenceMatcher(None, title1, title2).ratio()

    def view_all_jobs(self, filters=None, page=0, page_size=5):
        try:
            self.clear_screen()
            query = self.db.collection('jobs')
            
            if filters:
                if filters.get('job_type'):
                    query = query.where('job_type', '==', filters['job_type'])
                if filters.get('location'):
                    query = query.where('location', '==', filters['location'])
            
            jobs = list(query.get())
            
            if filters and filters.get('title'):
                search_term = filters['title']
                jobs = [
                    job for job in jobs 
                    if self._title_similarity(search_term, job.to_dict()['title']) >= 0.6
                ]
            
            if filters and filters.get('salary_range'):
                min_salary, max_salary = filters['salary_range']
                jobs = [job for job in jobs if self._is_salary_in_range(job.to_dict(), min_salary, max_salary)]
            
            if not jobs:
                self.console.print(Panel(
                    "[yellow]No jobs found matching the following criteria:[/yellow]\n" +
                    "\n".join([f"[cyan]{key}:[/cyan] {value}" for key, value in filters.items()]) 
                    if filters else "[yellow]No jobs available[/yellow]",
                    title="Search Results",
                    border_style="red"
                ))
                self.input_yellow("\nPress Enter to continue...")
                return None

            total_pages = (len(jobs) - 1) // page_size + 1
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(jobs))
            current_jobs = jobs[start_idx:end_idx]

            job_table = Table(show_header=True, box=box.SIMPLE)
            job_table.add_column("#", style="cyan", justify="right")
            job_table.add_column("Title", style="white")
            job_table.add_column("Location", style="white")
            job_table.add_column("Type", style="white")
            job_table.add_column("Salary Range", style="white")
            
            for idx, job in enumerate(current_jobs, start_idx + 1):
                job_data = job.to_dict()
                job_table.add_row(
                    str(idx),
                    job_data['title'],
                    job_data['location'],
                    job_data['job_type'],
                    job_data.get('salary_range', 'N/A')
                )
            
            self.console.print(Panel(job_table, title=f"Available Jobs (Page {page + 1}/{total_pages})", border_style="blue"))
            
            if total_pages > 1:
                self.print_yellow("\nNavigation: 'n' for next page, 'p' for previous page")
            self.print_yellow("Enter job number to view details or 'x' to exit")
            
            choice = self.input_yellow("\nChoice: ").lower()
            
            if choice == 'n' and page < total_pages - 1:
                return self.view_all_jobs(filters, page + 1, page_size)
            elif choice == 'p' and page > 0:
                return self.view_all_jobs(filters, page - 1, page_size)
            elif choice == 'x':
                return jobs
            elif choice.isdigit():
                job_idx = int(choice) - 1
                if 0 <= job_idx < len(jobs):
                    self.clear_screen()
                    self.view_job_details(jobs[job_idx].id)
                    self.input_yellow("\nPress Enter to continue...")
                    return self.view_all_jobs(filters, page, page_size)
            
            return jobs
            
        except Exception as e:
            self.console.print(f"[red]Error viewing jobs: {str(e)}[/red]")
            return None

    def _is_salary_in_range(self, job_data, filter_min, filter_max):
        try:
            if 'min_salary' not in job_data or 'max_salary' not in job_data:
                return False
            job_min = job_data['min_salary']
            job_max = job_data['max_salary']
            return not (job_max < filter_min or job_min > filter_max)
        except:
            return False

    def view_job_details(self, job_id):
        try:
            self.clear_screen()
            job_doc = self.db.collection('jobs').document(job_id).get()
            
            if not job_doc.exists:
                self.console.print("[red]Job not found![/red]")
                return
            
            job_data = job_doc.to_dict()
            
            details = [
                f"[bold cyan]Title:[/bold cyan] {job_data['title']}",
                f"[bold cyan]Location:[/bold cyan] {job_data['location']}",
                f"[bold cyan]Job Type:[/bold cyan] {job_data['job_type']}",
                f"[bold cyan]Salary Range:[/bold cyan] {job_data.get('salary_range', 'N/A')}",
                "\n[bold cyan]Responsibilities:[/bold cyan]",
                job_data['responsibilities'],
                "\n[bold cyan]Qualifications:[/bold cyan]",
                job_data['qualifications'],
                "\n[bold cyan]Benefits:[/bold cyan]",
                job_data['benefits']
            ]
            
            self.console.print(Panel(
                "\n".join(details),
                title=f"Job Details - {job_data['title']}",
                border_style="blue",
                width=100
            ))
            
        except Exception as e:
            self.console.print(f"[red]Error viewing job details: {str(e)}[/red]")

def handle_salary_filter(console):
    while True:
        try:
            min_salary = int(console.input_yellow("Enter minimum salary (in thousands USD): "))
            if min_salary < 0:
                console.print("[red]Minimum salary cannot be negative[/red]")
                continue
                
            max_salary = int(console.input_yellow("Enter maximum salary (in thousands USD): "))
            if max_salary < min_salary:
                console.print("[red]Maximum salary must be greater than or equal to minimum salary[/red]")
                continue
                
            return min_salary, max_salary
        except ValueError:
            console.print("[red]Please enter valid whole numbers[/red]")

def main():
    job_viewer = JobViewer()
    
    while True:
        job_viewer.clear_screen()
        job_viewer.console.print(Panel.fit(
            "[bold yellow]Job Market View[/bold yellow]",
            box=box.DOUBLE
        ))
        
        job_viewer.print_yellow("\n1: View All Jobs")
        job_viewer.print_yellow("2: Filter Jobs")
        job_viewer.print_yellow("3: Return to Dashboard")
        
        choice = job_viewer.input_yellow("\nSelect an option [1/2/3]: ").strip()
        
        if choice == "1":
            job_viewer.view_all_jobs()
            
        elif choice == "2":
            filters = {}
            job_viewer.clear_screen()
            
            if job_viewer.input_yellow("Search by job title? (y/n): ").lower() == "y":
                title_search = job_viewer.input_yellow("Enter search term for job title: ")
                filters['title'] = title_search
            
            if job_viewer.input_yellow("Filter by job type? (y/n): ").lower() == "y":
                job_viewer.print_yellow("\nAvailable job types:")
                job_viewer.print_yellow("1. Full-time")
                job_viewer.print_yellow("2. Part-time")
                job_viewer.print_yellow("3. Contract")
                job_viewer.print_yellow("4. Internship")
                
                job_type_map = {
                    "1": "full-time",
                    "2": "part-time",
                    "3": "contract",
                    "4": "internship"
                }
                
                while True:
                    choice = job_viewer.input_yellow("\nSelect job type [1-4]: ")
                    if choice in job_type_map:
                        filters['job_type'] = job_type_map[choice]
                        break
                    job_viewer.console.print("[red]Invalid choice. Please try again.[/red]")
            
            if job_viewer.input_yellow("Filter by location? (y/n): ").lower() == "y":
                location = job_viewer.input_yellow("Enter location: ")
                filters['location'] = location
            
            if job_viewer.input_yellow("Filter by salary range? (y/n): ").lower() == "y":
                min_salary, max_salary = handle_salary_filter(job_viewer.console)
                filters['salary_range'] = (min_salary, max_salary)
            
            job_viewer.view_all_jobs(filters)
            
        elif choice == "3":
            break
        
        else:
            job_viewer.console.print("[red]Invalid choice. Please try again.[/red]")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[bold red]Program terminated by user.")
        sys.exit()