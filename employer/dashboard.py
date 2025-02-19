from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from datetime import datetime
import time

class EmployerDashboard:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()

    def create_header(self):
        """Create the dashboard header"""
        header = Panel(
            Align.center("[bold yellow]JobHive Employer Dashboard[/bold yellow]"),
            style="bold white on blue"
        )
        return header

    def create_stats_panel(self, stats):
        """Create a panel showing key statistics"""
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow")
        
        for key, value in stats.items():
            stats_table.add_row(key, str(value))
            
        stats_panel = Panel(
            stats_table,
            title="[bold]Key Statistics[/bold]",
            border_style="blue"
        )
        return stats_panel

    def create_job_listings_table(self, jobs):
        """Create a table showing active job listings"""
        table = Table(title="Active Job Listings")
        table.add_column("ID", style="cyan")
        table.add_column("Position", style="magenta")
        table.add_column("Applications", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Posted Date", style="blue")

        for job in jobs:
            table.add_row(
                str(job['id']),
                job['position'],
                str(job['applications']),
                job['status'],
                job['posted_date']
            )
        
        return table

    def create_recent_activities(self, activities):
        """Create a panel showing recent activities"""
        activity_text = Text()
        for activity in activities:
            activity_text.append(f"• {activity['time']} - {activity['description']}\n")
        
        activities_panel = Panel(
            activity_text,
            title="[bold]Recent Activities[/bold]",
            border_style="green"
        )
        return activities_panel

    def display_dashboard(self):
        """Display the complete dashboard"""
        # Sample data - replace with actual data from your database
        sample_stats = {
            "Total Active Jobs": 12,
            "Total Applications": 145,
            "Pending Reviews": 23,
            "Hired This Month": 5
        }

        sample_jobs = [
            {"id": 1, "position": "Senior Developer", "applications": 25, 
             "status": "Active", "posted_date": "2024-02-01"},
            {"id": 2, "position": "Product Manager", "applications": 18, 
             "status": "Active", "posted_date": "2024-02-03"},
            {"id": 3, "position": "UX Designer", "applications": 15, 
             "status": "Closing Soon", "posted_date": "2024-02-05"}
        ]

        sample_activities = [
            {"time": "10:30 AM", "description": "New application received for Senior Developer"},
            {"time": "09:15 AM", "description": "Interview scheduled with John Doe"},
            {"time": "Yesterday", "description": "Posted new job listing for UX Designer"}
        ]

        # Clear the screen
        self.console.clear()

        # Create layout
        self.layout.split_column(
            Layout(self.create_header(), size=3),
            Layout(self.create_stats_panel(sample_stats), size=8),
            Layout(self.create_job_listings_table(sample_jobs), size=12),
            Layout(self.create_recent_activities(sample_activities), size=10)
        )

        # Render the layout
        self.console.print(self.layout)

    def run(self):
        """Run the dashboard with automatic refresh"""
        while True:
            try:
                self.display_dashboard()
                time.sleep(30)  # Refresh every 30 seconds
            except KeyboardInterrupt:
                print("\nExiting dashboard...")
                break

if __name__ == "__main__":
    dashboard = EmployerDashboard()
    dashboard.run()