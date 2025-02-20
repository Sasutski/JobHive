from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import sys
import time
import os

console = Console()

def clear_screen():
    # Cross-platform clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    console.clear()

def create_header():
    header_text = Text("Employer Dashboard", style="bold white on blue", justify="center")
    return Panel(header_text, box=box.DOUBLE, padding=(1, 1))

def create_menu():
    menu_items = [
        "[1] Post New Job",
        "[2] Review Applicants",
        "[3] View Posted Jobs",
        "[4] Account Settings",
        "[5] Exit"
    ]
    menu_text = Text("\n".join(menu_items), justify="left")
    return Panel(menu_text, title="Menu Options", box=box.ROUNDED, padding=(1, 1))

def loading_animation():
    with console.status("[bold blue]Loading...", spinner="dots"):
        time.sleep(1.5)

def redirect_to_page(choice):
    loading_animation()
    clear_screen()
    
    if choice == "1":
        console.print("[bold green]Redirecting to Post Job page...")
        try:
            import post_job
            post_job.main()
            return "post_job"
        except ImportError:
            console.print("[bold red]Error: post_job.py not found!")

    elif choice == "2":
        console.print("[bold green]Redirecting to Review Applicants page...")
        try:
            import review_applicants
            review_applicants.main()
            return "review_applicants"
        except ImportError:
            console.print("[bold red]Error: review_applicants.py not found!")

    elif choice == "3":
        console.print("[bold green]Redirecting to View Jobs page...")
        try:
            import view_jobs
            view_jobs.main()
            return "view_jobs"
        except ImportError:
            console.print("[bold red]Error: view_jobs.py not found!")

    elif choice == "4":
        console.print("[bold green]Redirecting to Account Settings...")
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from authentication import AuthenticationCLI
            auth_cli = AuthenticationCLI()
            auth_cli.main_loop()
            return "authentication"
        except ImportError as e:
            console.print(f"[bold red]Error: {str(e)}")
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}")

def display_dashboard():
    clear_screen()
    
    # Create and display header
    console.print(create_header())
    
    # Create and display menu
    console.print(create_menu())

def main():
    while True:
        display_dashboard()
        
        # Get user input
        choice = console.input("\n[bold yellow]Enter your choice (1-5): ")
        
        if choice == "5":
            console.print("\n[bold blue]Thank you for using the Employer Dashboard!")
            time.sleep(1)
            sys.exit()
            
        elif choice in ["1", "2", "3", "4"]:
            current_page = redirect_to_page(choice)
            
            if current_page:
                clear_screen()
        else:
            console.print("[bold red]Invalid choice! Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program terminated by user.")
        sys.exit()