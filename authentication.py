from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from rich.text import Text
from rich.layout import Layout
from typing import Optional
import firebase_admin
from firebase_admin import auth, credentials, firestore
from firebase_admin._auth_utils import (
    UserNotFoundError,
    InvalidIdTokenError
)
import time
import json
import os
from pathlib import Path
import requests

# Replace with your Firebase Web API Key
YOUR_FIREBASE_WEB_API_KEY = "AIzaSyAcwreE9k06t8HtJ6vhSOblwCskAEkWRWQ"

class AuthenticationCLI:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).parent
        
        # Get serviceAccountKey directly from gist
        gist_url = "https://gist.githubusercontent.com/Sasutski/808de9abc7f676ed253cc0f63a0f56b5/raw/serviceAccountKey.json"
        response = requests.get(gist_url)
        if response.status_code == 200:
            service_account_info = response.json()  # Parse JSON directly from response
        else:
            raise Exception("Failed to fetch serviceAccountKey from gist")
    
        # Initialize Firebase Admin SDK with the dictionary directly
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.current_user = self.load_user_session()

    def load_user_session(self):
        """Load user session from JSON file"""
        try:
            session_file = self.project_root / 'user.json'
            if session_file.exists():
                with open(session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load session: {str(e)}[/yellow]")
        return None

    def save_user_session(self, user_data=None):
        """Save user session to JSON file"""
        try:
            session_file = self.project_root / 'user.json'
            if user_data:
                with open(session_file, 'w') as f:
                    json.dump(user_data, f, indent=4)
                self.current_user = user_data
            else:
                if session_file.exists():
                    session_file.unlink()  # Delete the file
                self.current_user = None
        except Exception as e:
            self.console.print(f"[red]Error saving session: {str(e)}[/red]")

    def display_header(self):
        """Display the application header"""
        self.console.print(Panel.fit(
            "[bold yellow]JobHive Authentication System[/bold yellow]",
            box=box.DOUBLE,
            padding=(1, 20)
        ))
        if self.current_user:
            self.console.print(f"[green]Logged in as: {self.current_user.get('email')} ({self.current_user.get('user_type', 'N/A')})[/green]")

    def display_menu(self):
        """Display the main menu"""
        menu_table = Table(show_header=False, box=box.SIMPLE)
        menu_table.add_column("Option", style="cyan")
        menu_table.add_column("Description", style="white")
        
        if not self.current_user:
            menu_items = [
                ("1", "Login"),
                ("2", "Create New User"),
                ("0", "Exit")
            ]
        else:
            menu_items = [
                ("1", "Get User Details"),
                ("2", "Update User"),
                ("3", "Disable User"),
                ("4", "Enable User"),
                ("5", "Delete User"),
                ("6", "Verify Token"),
                ("7", "Logout"),
                ("0", "Exit")
            ]
        
        for option, description in menu_items:
            menu_table.add_row(option, description)
            
        self.console.print(Panel(menu_table, title="Menu", border_style="blue"))

    def login_flow(self):
        """Handle user login flow using email/password"""
        self.console.print("\n[bold blue]Login[/bold blue]")
        try:
            email = Prompt.ask("Enter email")
            password = Prompt.ask("Enter password", password=True)
            
            with self.console.status("[bold green]Logging in..."):
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={YOUR_FIREBASE_WEB_API_KEY}"
                
                payload = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                }
                
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    auth_data = response.json()
                    # Get user details using the UID
                    user = auth.get_user(auth_data['localId'])
                    
                    # Get Firestore data
                    user_doc = self.db.collection('users').document(user.uid).get()
                    user_data = {
                        'uid': user.uid,
                        'email': user.email,
                        'display_name': user.display_name,
                        'email_verified': user.email_verified,
                        'disabled': user.disabled,
                        'id_token': auth_data['idToken'],
                        'refresh_token': auth_data['refreshToken'],
                        'user_type': user_doc.get('user_type')  # Include user type in session
                    }
                    self.save_user_session(user_data)
                    self.console.print("[green]Login successful![/green]")
                else:
                    error_message = response.json().get('error', {}).get('message', 'Unknown error')
                    self.console.print(f"[red]Login failed: {error_message}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def logout_flow(self):
        """Handle user logout flow"""
        if Confirm.ask("Are you sure you want to logout?"):
            self.save_user_session(None)
            self.console.print("[yellow]Logged out successfully![/yellow]")

    def create_user_flow(self):
        """Handle user creation flow"""
        self.console.print("\n[bold blue]Create New User[/bold blue]")
        try:
            email = Prompt.ask("Enter email")
            password = Prompt.ask("Enter password", password=True)
            display_name = Prompt.ask("Enter display name", default="")
            
            # Add user type selection
            user_type = Prompt.ask(
                "Select user type",
                choices=["applicant", "employer"],
                default="applicant"
            )
            
            with self.console.status("[bold green]Creating user..."):
                user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=display_name
                )
                
                # Store user data in Firestore
                user_ref = self.db.collection('users').document(user.uid)
                user_ref.set({
                    'email': email,
                    'display_name': display_name,
                    'user_type': user_type,
                    'created_at': firestore.SERVER_TIMESTAMP
                })
            
            self.console.print(f"[green]User created successfully! UID: {user.uid}[/green]")
            
            if Confirm.ask("Would you like to login as this user?"):
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={YOUR_FIREBASE_WEB_API_KEY}"
                payload = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                }
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    auth_data = response.json()
                    # Get Firestore data
                    user_doc = user_ref.get()
                    user_data = {
                        'uid': user.uid,
                        'email': user.email,
                        'display_name': user.display_name,
                        'email_verified': user.email_verified,
                        'disabled': user.disabled,
                        'id_token': auth_data['idToken'],
                        'refresh_token': auth_data['refreshToken'],
                        'user_type': user_doc.get('user_type')
                    }
                    self.save_user_session(user_data)
                    self.console.print("[green]Logged in successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def get_user_flow(self):
        """Handle user details retrieval flow"""
        self.console.print("\n[bold blue]Get User Details[/bold blue]")
        try:
            if self.current_user:
                uid = self.current_user['uid']
            else:
                uid = Prompt.ask("Enter user UID")
            
            with self.console.status("[bold green]Fetching user details..."):
                user = auth.get_user(uid)
                user_doc = self.db.collection('users').document(uid).get()
            
            user_table = Table(show_header=True, box=box.SIMPLE)
            user_table.add_column("Property", style="cyan")
            user_table.add_column("Value", style="white")
            
            user_details = [
                ("UID", user.uid),
                ("Email", user.email),
                ("Display Name", user.display_name),
                ("Email Verified", str(user.email_verified)),
                ("Disabled", str(user.disabled)),
                ("User Type", user_doc.get('user_type', 'N/A'))
            ]
            
            for prop, value in user_details:
                user_table.add_row(prop, str(value))
                
            self.console.print(Panel(user_table, title="User Details", border_style="green"))
        except UserNotFoundError as e:
            self.console.print(f"[red]User not found: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def verify_token_flow(self):
        """Handle token verification flow"""
        self.console.print("\n[bold blue]Verify Token[/bold blue]")
        try:
            if self.current_user and self.current_user.get('id_token'):
                token = self.current_user['id_token']
            else:
                token = Prompt.ask("Enter token")
            
            with self.console.status("[bold green]Verifying token..."):
                decoded_token = auth.verify_id_token(token)
            
            token_table = Table(show_header=True, box=box.SIMPLE)
            token_table.add_column("Claim", style="cyan")
            token_table.add_column("Value", style="white")
            
            for key, value in decoded_token.items():
                token_table.add_row(str(key), str(value))
                
            self.console.print(Panel(token_table, title="Token Claims", border_style="green"))
        except InvalidIdTokenError as e:
            self.console.print(f"[red]Invalid token: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def update_user_flow(self):
        """Handle user update flow"""
        self.console.print("\n[bold blue]Update User[/bold blue]")
        try:
            if self.current_user:
                uid = self.current_user['uid']
            else:
                uid = Prompt.ask("Enter user UID")
            
            email = Prompt.ask("Enter new email (press enter to skip)", default="")
            display_name = Prompt.ask("Enter new display name (press enter to skip)", default="")
            user_type = Prompt.ask("Enter new user type (press enter to skip)", choices=["", "applicant", "employer"], default="")
            
            update_params = {}
            if email:
                update_params['email'] = email
            if display_name:
                update_params['display_name'] = display_name
                
            if update_params or user_type:
                with self.console.status("[bold green]Updating user..."):
                    if update_params:
                        updated_user = auth.update_user(uid, **update_params)
                    else:
                        updated_user = auth.get_user(uid)
                    
                    # Update Firestore
                    user_ref = self.db.collection('users').document(uid)
                    update_data = {}
                    if email:
                        update_data['email'] = email
                    if display_name:
                        update_data['display_name'] = display_name
                    if user_type:
                        update_data['user_type'] = user_type
                    
                    if update_data:
                        user_ref.update(update_data)
                    
                    # Update session data if the current user was updated
                    if self.current_user and self.current_user['uid'] == uid:
                        user_data = self.current_user.copy()
                        user_data.update({
                            'email': updated_user.email,
                            'display_name': updated_user.display_name,
                            'email_verified': updated_user.email_verified,
                            'disabled': updated_user.disabled
                        })
                        if user_type:
                            user_data['user_type'] = user_type
                        self.save_user_session(user_data)
                        
                self.console.print("[green]User updated successfully![/green]")
            else:
                self.console.print("[yellow]No updates provided[/yellow]")
        except UserNotFoundError as e:
            self.console.print(f"[red]User not found: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def disable_user_flow(self):
        """Handle user disable flow"""
        self.console.print("\n[bold blue]Disable User[/bold blue]")
        try:
            if self.current_user:
                uid = self.current_user['uid']
            else:
                uid = Prompt.ask("Enter user UID")
            
            if Confirm.ask("Are you sure you want to disable this user?"):
                with self.console.status("[bold green]Disabling user..."):
                    auth.update_user(uid, disabled=True)
                    
                    # Update session data if the current user was disabled
                    if self.current_user and self.current_user['uid'] == uid:
                        self.save_user_session(None)  # Log out if current user is disabled
                        
                self.console.print("[green]User disabled successfully![/green]")
        except UserNotFoundError as e:
            self.console.print(f"[red]User not found: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def enable_user_flow(self):
        """Handle user enable flow"""
        self.console.print("\n[bold blue]Enable User[/bold blue]")
        try:
            if self.current_user:
                uid = self.current_user['uid']
            else:
                uid = Prompt.ask("Enter user UID")
            
            with self.console.status("[bold green]Enabling user..."):
                auth.update_user(uid, disabled=False)
            self.console.print("[green]User enabled successfully![/green]")
        except UserNotFoundError as e:
            self.console.print(f"[red]User not found: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def delete_user_flow(self):
        """Handle user deletion flow"""
        self.console.print("\n[bold blue]Delete User[/bold blue]")
        try:
            if self.current_user:
                uid = self.current_user['uid']
            else:
                uid = Prompt.ask("Enter user UID")
            
            if Confirm.ask("Are you sure you want to delete this user?", default=False):
                with self.console.status("[bold green]Deleting user..."):
                    # Delete from Firestore first
                    self.db.collection('users').document(uid).delete()
                    # Then delete from Authentication
                    auth.delete_user(uid)
                    
                    # Clear session if the current user was deleted
                    if self.current_user and self.current_user['uid'] == uid:
                        self.save_user_session(None)
                        
                self.console.print("[green]User deleted successfully![/green]")
        except UserNotFoundError as e:
            self.console.print(f"[red]User not found: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def main_loop(self):
        """Main application loop"""
        while True:
            self.console.clear()
            self.display_header()
            self.display_menu()
            
            if not self.current_user:
                choice = Prompt.ask("Select an option", choices=["0", "1", "2"])
                
                if choice == "0":
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break
                elif choice == "1":
                    self.login_flow()
                elif choice == "2":
                    self.create_user_flow()
            else:
                choice = Prompt.ask("Select an option", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
                
                if choice == "0":
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break
                elif choice == "1":
                    self.get_user_flow()
                elif choice == "2":
                    self.update_user_flow()
                elif choice == "3":
                    self.disable_user_flow()
                elif choice == "4":
                    self.enable_user_flow()
                elif choice == "5":
                    self.delete_user_flow()
                elif choice == "6":
                    self.verify_token_flow()
                elif choice == "7":
                    self.logout_flow()
                
            time.sleep(2)

if __name__ == "__main__":
    cli = AuthenticationCLI()
    cli.main_loop()