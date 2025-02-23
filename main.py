from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
import sys, os
from pathlib import Path
from datetime import datetime
import json

from authentication import AuthenticationCLI
from applicant.dashboard import ApplicantDashboard
from employer.dashboard import EmployerDashboard

class JobHive:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).parent
        self.auth = AuthenticationCLI()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def create_header(self):
        header_text = """
[bold cyan]
     ██╗ ██████╗ ██████╗ ██╗  ██╗██╗██╗   ██╗███████╗
     ██║██╔═══██╗██╔══██╗██║  ██║██║██║   ██║██╔════╝
     ██║██║   ██║██████╔╝███████║██║██║   ██║█████╗  
██   ██║██║   ██║██╔══██╗██╔══██║██║╚██╗ ██╔╝██╔══╝  
╚█████╔╝╚██████╔╝██████╔╝██║  ██║██║ ╚████╔╝ ███████╗
 ╚════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝
[/bold cyan]"""
        return Panel(header_text, box=box.DOUBLE)

    def display_welcome(self):
        self.clear_screen()
        self.console.print(self.create_header())
        self.console.print("\n[bold cyan]Welcome to JobHive![/bold cyan]")
        self.console.print("[cyan]Your One-Stop Platform for Job Search and Recruitment[/cyan]\n")

    def create_menu(self):
        menu_items = [
            "[1] Login",
            "[2] Register",
            "[3] About",
            "[4] Exit"
        ]
        menu_text = "\n".join(menu_items)
        return Panel(menu_text, title="Main Menu", box=box.ROUNDED)

    def display_about(self):
        self.clear_screen()
        about_text = """
[cyan]JobHive is a comprehensive job search and recruitment platform that connects job seekers with employers.
Our platform offers:[/cyan]

[green]For Job Seekers:[/green]
• Browse and apply for jobs
• Track application status
• Resume review and optimization
• Save interesting job postings

[green]For Employers:[/green]
• Post job openings
• Review applications
• Manage candidate pipeline
• Access recruitment tools

[cyan]Version: 1.0.0
Created by: MST4
Last Updated: February 2025[/cyan]
"""
        self.console.print(Panel(about_text, title="About JobHive", border_style="blue", width=100))
        self.console.input("\n[yellow]Press Enter to return to main menu...[/yellow]")

    def handle_user_type(self, user_type):
        if user_type.lower() == 'applicant':
            dashboard = ApplicantDashboard()
            dashboard.run()
        elif user_type.lower() == 'employer':
            dashboard = EmployerDashboard()
            dashboard.run()
        else:
            self.console.print("[red]Invalid user type![/red]")

    def check_login_status(self):
        user_file = self.project_root / 'user.json'
        if user_file.exists():
            with open(user_file) as f:
                user_data = json.load(f)
            return user_data.get('user_type')
        return None

    def run(self):
        try:
            while True:
                user_type = self.check_login_status()
                
                if user_type:
                    self.handle_user_type(user_type)
                else:
                    self.display_welcome()
                    self.console.print(self.create_menu())
                    
                    choice = Prompt.ask("\nPlease select an option", choices=["1", "2", "3", "4"])
                    
                    if choice == "1":
                        if self.auth.login():
                            user_type = self.check_login_status()
                            if user_type:
                                self.handle_user_type(user_type)
                                
                    elif choice == "2":
                        self.auth.register()
                        
                    elif choice == "3":
                        self.display_about()
                        
                    elif choice == "4":
                        try:
                            if Prompt.ask("\n[yellow]Are you sure you want to exit?[/yellow]", 
                                choices=["y", "n"], default="n") == "y":
                                self.console.print("\n[cyan]Thank you for using JobHive![/cyan]")
                                break
                        except KeyboardInterrupt:
                            self.console.print("\n[cyan]Goodbye![/cyan]")
                            break

                try:
                    if not Prompt.ask("\nWould you like to continue using JobHive?", 
                        choices=["y", "n"], default="y") == "y":
                        if Prompt.ask("\n[yellow]Are you sure you want to exit?[/yellow]", 
                            choices=["y", "n"], default="n") == "y":
                            self.console.print("\n[cyan]Thank you for using JobHive![/cyan]")
                            break
                except KeyboardInterrupt:
                    self.console.print("\n[cyan]Goodbye![/cyan]")
                    break

        except KeyboardInterrupt:
            self.console.print("\n[cyan]Goodbye![/cyan]")
        except Exception as e:
            self.console.print(f"\n[red]An error occurred: {str(e)}[/red]")

def main():
    app = JobHive()
    app.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[cyan]Goodbye![/cyan]")
    except Exception as e:
        Console().print(f"\n[red]An error occurred: {str(e)}[/red]")