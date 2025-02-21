from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import firebase_admin
from firebase_admin import firestore, credentials
import requests, time, sys, warnings, os, json
from pathlib import Path
from difflib import SequenceMatcher
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning, module="google.cloud.firestore_v1.base_collection")

class ApplicantJobViewer:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).resolve().parent.parent
        
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(requests.get(
                    "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
                ).json())
                self.app = firebase_admin.initialize_app(cred, name='applicant_viewer')
            else:
                try:
                    self.app = firebase_admin.get_app('applicant_viewer')
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

    def _title_similarity(self, title1, title2):
        title1 = title1.lower()
        title2 = title2.lower()
        if title1 in title2 or title2 in title1:
            return 1.0
        return SequenceMatcher(None, title1, title2).ratio()

    def apply_for_job(self, job_id, job_title):
        try:
            # Verify user.json exists and can be read
            user_json_path = self.project_root / 'user.json'
            if not user_json_path.exists():
                self.console.print("[red]Error: user.json file not found![/red]")
                return False

            # Read user data
            with open(user_json_path) as f:
                user_data = json.load(f)

            # Check if already applied
            applications_ref = self.db.collection('applications')
            existing_application = applications_ref.where('user_id', '==', user_data['uid']).where('job_id', '==', job_id).get()
            
            if list(existing_application):
                self.console.print("[red]You have already applied for this job![/red]")
                return False

            # Collect application details
            self.console.print("\n[yellow]Please provide the following information:[/yellow]")
            
            # Required fields
            email = self.input_yellow("Email: ")
            while not email or '@' not in email:
                self.console.print("[red]Please enter a valid email address[/red]")
                email = self.input_yellow("Email: ")

            phone = self.input_yellow("Phone Number: ")
            while not phone:
                self.console.print("[red]Phone number is required[/red]")
                phone = self.input_yellow("Phone Number: ")

            age = self.input_yellow("Age: ")
            while not age.isdigit() or int(age) < 16:
                self.console.print("[red]Please enter a valid age (16+)[/red]")
                age = self.input_yellow("Age: ")

            gender = self.input_yellow("Gender (M/F/Other): ").upper()
            while gender not in ['M', 'F', 'OTHER']:
                self.console.print("[red]Please enter M, F, or Other[/red]")
                gender = self.input_yellow("Gender (M/F/Other): ").upper()

            resume_path = self.input_yellow("Resume file path: ")
            while not Path(resume_path).exists():
                self.console.print("[red]File not found. Please enter a valid file path[/red]")
                resume_path = self.input_yellow("Resume file path: ")

            # Optional fields
            linkedin = self.input_yellow("LinkedIn Profile (optional): ")
            github = self.input_yellow("GitHub Profile (optional): ")
            portfolio = self.input_yellow("Portfolio URL (optional): ")

            # Prepare application data
            application_data = {
                'user_id': user_data['uid'],
                'user_name': user_data['display_name'],
                'job_id': job_id,
                'job_title': job_title,
                'email': email,
                'phone': phone,
                'age': int(age),
                'gender': gender,
                'resume_path': resume_path,
                'linkedin': linkedin if linkedin else None,
                'github': github if github else None,
                'portfolio': portfolio if portfolio else None,
                'application_date': datetime.now(),
                'status': 'pending'
            }

            # Add application to Firebase
            doc_ref = applications_ref.document()
            doc_ref.set(application_data)

            self.console.print("[green]Application submitted successfully![/green]")
            return True

        except Exception as e:
            self.console.print(f"[red]Error submitting application: {str(e)}[/red]")
            return False

    def delete_saved_job(self, job_doc_id):
        try:
            # Get confirmation from user
            confirm = self.input_yellow("\nAre you sure you want to delete this saved job? (y/n): ").lower()
            if confirm != 'y':
                self.console.print("[yellow]Deletion cancelled.[/yellow]")
                return False

            # Delete the job from Firebase
            self.db.collection('saved_jobs').document(job_doc_id).delete()
            self.console.print("[green]Job successfully deleted![/green]")
            return True

        except Exception as e:
            self.console.print(f"[red]Error deleting job: {str(e)}[/red]")
            return False

    def save_job(self, job_id, job_title):
        try:
            # Debug print
            self.console.print(f"[blue]Attempting to save job: {job_title} (ID: {job_id})[/blue]")
    
            # Verify user.json exists and can be read
            user_json_path = self.project_root / 'user.json'
            if not user_json_path.exists():
                self.console.print("[red]Error: user.json file not found![/red]")
                return False
    
            # Read user data
            with open(user_json_path) as f:
                user_data = json.load(f)
    
            # Verify user data contains required fields
            if 'uid' not in user_data or 'display_name' not in user_data:
                self.console.print("[red]Error: Missing user ID or display name in user.json[/red]")
                return False
    
            user_id = user_data['uid']
            user_name = user_data['display_name']
    
            # Debug print
            self.console.print(f"[blue]User ID: {user_id}[/blue]")
    
            # Check for existing saved job
            saved_jobs_ref = self.db.collection('saved_jobs')
            existing_saved = saved_jobs_ref.where('user_id', '==', user_id).where('job_id', '==', job_id).get()
            
            if list(existing_saved):
                self.console.print("[red]You have already saved this job![/red]")
                return False
    
            # Prepare job data
            saved_job_data = {
                'user_id': user_id,
                'user_name': user_name,
                'job_id': job_id,
                'job_title': job_title,
                'saved_date': datetime.now()
            }
    
            # Debug print
            self.console.print("[blue]Saving job to Firebase...[/blue]")
    
            # Add document to Firebase
            doc_ref = saved_jobs_ref.document()
            doc_ref.set(saved_job_data)
    
            self.console.print("[green]Job saved successfully![/green]")
            return True
    
        except FileNotFoundError:
            self.console.print("[red]Error: Could not find user.json file[/red]")
            return False
        except json.JSONDecodeError:
            self.console.print("[red]Error: Invalid JSON in user.json file[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Error saving job: {str(e)}[/red]")
            return False

    def view_saved_jobs(self):
        try:
            user_json_path = self.project_root / 'user.json'
            with open(user_json_path) as f:
                user_data = json.loads(f.read())
            
            user_id = user_data['uid']

            saved_jobs = self.db.collection('saved_jobs').where('user_id', '==', user_id).get()
            
            if not saved_jobs:
                self.console.print(Panel("[yellow]You haven't saved any jobs yet.[/yellow]", 
                                       title="Saved Jobs", border_style="red"))
                return

            while True:
                self.clear_screen()
                table = Table(show_header=True, box=box.SIMPLE)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Job Title", style="cyan")
                table.add_column("Saved Date", style="white")

                saved_jobs_list = list(saved_jobs)

                for idx, job in enumerate(saved_jobs_list, 1):
                    job_data = job.to_dict()
                    table.add_row(
                        str(idx),
                        job_data['job_title'],
                        job_data['saved_date'].strftime("%Y-%m-%d")
                    )

                self.console.print(Panel(table, title="Saved Jobs", border_style="blue"))
                
                self.print_yellow("\nOptions:")
                self.print_yellow("1. View job details (enter job number)")
                self.print_yellow("2. Apply for job (enter 'a' followed by job number, e.g., 'a1')")
                self.print_yellow("3. Delete job (enter 'd' followed by job number, e.g., 'd1')")
                self.print_yellow("4. Return (enter 'x')")
                
                choice = self.input_yellow("\nChoice: ").lower()
                
                if choice == 'x':
                    break
                elif choice.startswith('d'):
                    try:
                        idx = int(choice[1:]) - 1
                        if 0 <= idx < len(saved_jobs_list):
                            if self.delete_saved_job(saved_jobs_list[idx].id):
                                saved_jobs = self.db.collection('saved_jobs').where('user_id', '==', user_id).get()
                                saved_jobs_list = list(saved_jobs)
                                if not saved_jobs_list:
                                    self.console.print(Panel("[yellow]You have no saved jobs.[/yellow]", 
                                                           title="Saved Jobs", border_style="red"))
                                    self.input_yellow("\nPress Enter to continue...")
                                    break
                        else:
                            self.console.print("[red]Invalid job number. Please try again.[/red]")
                            self.input_yellow("\nPress Enter to continue...")
                    except ValueError:
                        self.console.print("[red]Invalid input format. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                elif choice.startswith('a'):
                    try:
                        idx = int(choice[1:]) - 1
                        if 0 <= idx < len(saved_jobs_list):
                            job_data = saved_jobs_list[idx].to_dict()
                            self.apply_for_job(job_data['job_id'], job_data['job_title'])
                            self.input_yellow("\nPress Enter to continue...")
                        else:
                            self.console.print("[red]Invalid job number. Please try again.[/red]")
                            self.input_yellow("\nPress Enter to continue...")
                    except ValueError:
                        self.console.print("[red]Invalid input format. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(saved_jobs_list):
                        job_data = saved_jobs_list[idx].to_dict()
                        self.clear_screen()
                        self.view_job_details(job_data['job_id'])
                        self.input_yellow("\nPress Enter to return to saved jobs...")
                    else:
                        self.console.print("[red]Invalid job number. Please try again.[/red]")
                        self.input_yellow("\nPress Enter to continue...")
                else:
                    self.console.print("[red]Invalid input. Please try again.[/red]")
                    self.input_yellow("\nPress Enter to continue...")

        except Exception as e:
            self.console.print(f"[red]Error viewing saved jobs: {str(e)}[/red]")

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
                    "[yellow]No jobs found matching the criteria[/yellow]",
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
                return None
            elif choice.isdigit():
                job_idx = int(choice) - 1
                if 0 <= job_idx < len(jobs):
                    self.clear_screen()
                    job = jobs[job_idx]
                    self.view_job_details(job.id)
                    self.input_yellow("\nPress Enter to continue...")
                    return self.view_all_jobs(filters, page, page_size)
            
            return None
            
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

            self.print_yellow("\nOptions:")
            self.print_yellow("1: Apply for this job")
            self.print_yellow("2: Save this job")
            self.print_yellow("3: Return")
            
            choice = self.input_yellow("\nSelect an option [1-3]: ").strip()
            
            if choice == "1":
                self.apply_for_job(job_id, job_data['title'])
            elif choice == "2":
                self.save_job(job_id, job_data['title'])
            
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
    job_viewer = ApplicantJobViewer()
    
    while True:
        job_viewer.clear_screen()
        job_viewer.console.print(Panel.fit(
            "[bold yellow]Job Search Dashboard[/bold yellow]",
            box=box.DOUBLE
        ))
        
        job_viewer.print_yellow("\n1: View All Jobs")
        job_viewer.print_yellow("2: Filter Jobs")
        job_viewer.print_yellow("3: View Saved Jobs")
        job_viewer.print_yellow("4: Return to Dashboard")
        
        choice = job_viewer.input_yellow("\nSelect an option [1-4]: ").strip()
        
        if choice == "1":
            job_viewer.view_all_jobs()
        elif choice == "2":
            filters = {}
            job_viewer.clear_screen()
            
            if job_viewer.input_yellow("Search by job title? (y/n): ").lower() == "y":
                filters['title'] = job_viewer.input_yellow("Enter search term for job title: ")
            
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
                filters['location'] = job_viewer.input_yellow("Enter location: ")
            
            if job_viewer.input_yellow("Filter by salary range? (y/n): ").lower() == "y":
                min_salary, max_salary = handle_salary_filter(job_viewer.console)
                filters['salary_range'] = (min_salary, max_salary)
            
            job_viewer.view_all_jobs(filters)
            
        elif choice == "3":
            job_viewer.view_saved_jobs()
        elif choice == "4":
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