from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
import firebase_admin
from firebase_admin import auth, credentials, firestore
from firebase_admin._auth_utils import UserNotFoundError, InvalidIdTokenError
import json, requests, time
from pathlib import Path

class AuthenticationCLI:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).parent
        self.API_KEY = "AIzaSyAcwreE9k06t8HtJ6vhSOblwCskAEkWRWQ"
        
        # Initialize Firebase only if not already initialized
        if not firebase_admin._apps:  # Check if no Firebase apps exist
            cred = credentials.Certificate(requests.get(
                "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
            ).json())
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.current_user = self._load_session()

    def _load_session(self):
        try:
            with open(self.project_root / 'user.json', 'r') as f:
                return json.load(f)
        except: return None

    def _save_session(self, user_data=None):
        path = self.project_root / 'user.json'
        if user_data:
            with open(path, 'w') as f:
                json.dump(user_data, f, indent=4)
        elif path.exists():
            path.unlink()
        self.current_user = user_data

    def _display_ui(self):
        self.console.clear()
        self.console.print(Panel.fit("[bold yellow]JobHive Authentication System[/bold yellow]",
                                   box=box.DOUBLE, padding=(1, 20)))
        if self.current_user:
            self.console.print(f"[green]Logged in as: {self.current_user['email']} ({self.current_user['user_type']})[/green]")

        menu_table = Table(show_header=False, box=box.SIMPLE)
        menu_table.add_column("Option", style="cyan")
        menu_table.add_column("Description", style="white")
        
        items = [("1", "Login"), ("2", "Create New User"), ("0", "Exit")] if not self.current_user else [
            ("1", "Get User Details"), ("2", "Update User"), ("3", "Disable User"),
            ("4", "Enable User"), ("5", "Delete User"), ("6", "Verify Token"),
            ("7", "Logout"), ("0", "Exit")
        ]
        
        for opt, desc in items:
            menu_table.add_row(opt, desc)
        self.console.print(Panel(menu_table, title="Menu", border_style="blue"))

    def login_flow(self):
        try:
            email = Prompt.ask("Enter email")
            password = Prompt.ask("Enter password", password=True)
            
            with self.console.status("[bold green]Logging in..."):
                response = requests.post(
                    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}",
                    json={"email": email, "password": password, "returnSecureToken": True}
                ).json()
                
                user = auth.get_user(response['localId'])
                user_doc = self.db.collection('users').document(user.uid).get()
                
                self._save_session({
                    'uid': user.uid,
                    'email': user.email,
                    'display_name': user.display_name,
                    'email_verified': user.email_verified,
                    'disabled': user.disabled,
                    'id_token': response['idToken'],
                    'refresh_token': response['refreshToken'],
                    'user_type': user_doc.to_dict().get('user_type')
                })
                self.console.print("[green]Login successful![/green]")
        except Exception as e:
            self.console.print(f"[red]Login failed: {str(e)}[/red]")

    def create_user_flow(self):
        try:
            email = Prompt.ask("Enter email")
            password = Prompt.ask("Enter password", password=True)
            display_name = Prompt.ask("Enter display name", default="")
            user_type = Prompt.ask("Select user type", choices=["applicant", "employer"], default="applicant")
            
            status = self.console.status("[bold green]Creating user...")
            status.start()
            
            try:
                # Create Firebase user
                user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=display_name
                )
    
                # Create Firestore document
                self.db.collection('users').document(user.uid).set({
                    'email': email,
                    'display_name': display_name,
                    'user_type': user_type,
                    'created_at': firestore.SERVER_TIMESTAMP
                })
    
                status.stop()
                self.console.print("[green]User created successfully![/green]")
                
                # Handle automatic login if requested
                if Confirm.ask("Would you like to login as this user?"):
                    try:
                        response = requests.post(
                            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}",
                            json={
                                "email": email,
                                "password": password,
                                "returnSecureToken": True
                            },
                            timeout=30
                        )
                        
                        response.raise_for_status()
                        response_data = response.json()
                        
                        if 'idToken' not in response_data or 'refreshToken' not in response_data:
                            raise Exception("Invalid response from authentication server")
                        
                        self._save_session({
                            'uid': user.uid,
                            'email': email,
                            'display_name': display_name,
                            'email_verified': False,
                            'disabled': False,
                            'id_token': response_data['idToken'],
                            'refresh_token': response_data['refreshToken'],
                            'user_type': user_type
                        })
                        self.console.print("[green]Logged in successfully![/green]")
                    except requests.exceptions.RequestException as e:
                        self.console.print(f"[red]Network error during login: {str(e)}[/red]")
                    except Exception as e:
                        self.console.print(f"[red]Failed to login: {str(e)}[/red]")
                        
            except Exception as e:
                status.stop()
                if 'user' in locals():  # If Firestore failed but user was created
                    auth.delete_user(user.uid)
                self.console.print(f"[red]Error creating user: {str(e)}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def get_user_flow(self):
        try:
            uid = self.current_user['uid'] if self.current_user else Prompt.ask("Enter user UID")
            user = auth.get_user(uid)
            user_doc = self.db.collection('users').document(uid).get()
            
            user_table = Table(show_header=True, box=box.SIMPLE)
            user_table.add_column("Property", style="cyan")
            user_table.add_column("Value", style="white")
            
            for prop, value in [
                ("UID", user.uid), ("Email", user.email),
                ("Display Name", user.display_name),
                ("Email Verified", str(user.email_verified)),
                ("Disabled", str(user.disabled)),
                ("User Type", user_doc.to_dict().get('user_type', 'N/A'))
            ]:
                user_table.add_row(prop, str(value))
                
            self.console.print(Panel(user_table, title="User Details", border_style="green"))
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def update_user_flow(self):
        try:
            uid = self.current_user['uid'] if self.current_user else Prompt.ask("Enter user UID")
            email = Prompt.ask("Enter new email (press enter to skip)", default="")
            display_name = Prompt.ask("Enter new display name (press enter to skip)", default="")
            user_type = Prompt.ask("Enter new user type", choices=["", "applicant", "employer"], default="")
            
            updates = {}
            if email: updates['email'] = email
            if display_name: updates['display_name'] = display_name
            
            if updates or user_type:
                with self.console.status("[bold green]Updating user..."):
                    if updates:
                        updated_user = auth.update_user(uid, **updates)
                    
                    if any([email, display_name, user_type]):
                        update_data = {k: v for k, v in {
                            'email': email, 'display_name': display_name,
                            'user_type': user_type
                        }.items() if v}
                        self.db.collection('users').document(uid).update(update_data)
                    
                    if self.current_user and self.current_user['uid'] == uid:
                        user_data = self.current_user.copy()
                        user_data.update(updates)
                        if user_type: user_data['user_type'] = user_type
                        self._save_session(user_data)
                
                self.console.print("[green]User updated successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def logout_flow(self):
        if Confirm.ask("Are you sure you want to logout?"):
            self._save_session(None)
            self.console.print("[yellow]Logged out successfully![/yellow]")

    def verify_token_flow(self):
        try:
            token = self.current_user['id_token'] if self.current_user else Prompt.ask("Enter token")
            claims = auth.verify_id_token(token)
            
            token_table = Table(show_header=True, box=box.SIMPLE)
            token_table.add_column("Claim", style="cyan")
            token_table.add_column("Value", style="white")
            
            for key, value in claims.items():
                token_table.add_row(str(key), str(value))
                
            self.console.print(Panel(token_table, title="Token Claims", border_style="green"))
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def disable_enable_user_flow(self, disable=True):
        try:
            uid = self.current_user['uid'] if self.current_user else Prompt.ask("Enter user UID")
            action = "disable" if disable else "enable"
            
            if Confirm.ask(f"Are you sure you want to {action} this user?"):
                auth.update_user(uid, disabled=disable)
                if disable and self.current_user and self.current_user['uid'] == uid:
                    self._save_session(None)
                self.console.print(f"[green]User {action}d successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def delete_user_flow(self):
        try:
            uid = self.current_user['uid'] if self.current_user else Prompt.ask("Enter user UID")
            
            if Confirm.ask("Are you sure you want to delete this user?", default=False):
                self.db.collection('users').document(uid).delete()
                auth.delete_user(uid)
                
                if self.current_user and self.current_user['uid'] == uid:
                    self._save_session(None)
                self.console.print("[green]User deleted successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

def main():
    auth_cli = AuthenticationCLI()
    while True:
        auth_cli._display_ui()
        choices = ["0", "1", "2"] if not auth_cli.current_user else ["0", "1", "2", "3", "4", "5", "6", "7"]
        choice = Prompt.ask("Select an option", choices=choices)
        
        if choice == "0":
            auth_cli.console.print("[yellow]Goodbye![/yellow]")
            break
            
        actions = {
            "1": auth_cli.login_flow if not auth_cli.current_user else auth_cli.get_user_flow,
            "2": auth_cli.create_user_flow if not auth_cli.current_user else auth_cli.update_user_flow,
            "3": lambda: auth_cli.disable_enable_user_flow(True),
            "4": lambda: auth_cli.disable_enable_user_flow(False),
            "5": auth_cli.delete_user_flow,
            "6": auth_cli.verify_token_flow,
            "7": auth_cli.logout_flow
        }
        
        actions[choice]()
        time.sleep(2)

if __name__ == "__main__":
    main()