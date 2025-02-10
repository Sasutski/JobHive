import pyrebase
import json
import os

config = { # Firebase configuration
  'apiKey': "AIzaSyCO19uyfT37NbNmzJGDvigl47Sv7ejC2SI",
  'authDomain': "jobhive-d66d3.firebaseapp.com",
  'projectId': "jobhive-d66d3",
  'storageBucket': "jobhive-d66d3.firebasestorage.app",
  'messagingSenderId': "658456142271",
  'appId': "1:658456142271:web:6b4a726a61e165e23e410a",
  'measurementId': "G-PF2SBL24EM",
  'databaseURL': "https://jobhive-d66d3-default-rtdb.asia-southeast1.firebasedatabase.app"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

firsttime = False
user_token = None
user_role = None
TOKEN_FILE = 'user_token.json'

def save_token(token, role):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'token': token, 'role': role}, f)

def load_token():
    global user_token, user_role
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                user_token = data.get('token')
                user_role = data.get('role')
                
                if not user_token or not user_role:
                    return False
                    
                try:
                    # Verify token is still valid with Firebase
                    user_info = auth.get_account_info(user_token)
                    if not user_info or 'users' not in user_info:
                        return False
                        
                    email = user_info['users'][0]['email']
                    # Verify user exists in database
                    user_data = db.child("users").order_by_child("email").equal_to(email).get()
                    user_found = False
                    
                    for user in user_data.each():
                        stored_role = user.val().get('role')
                        if stored_role == user_role:
                            user_found = True
                            break
                            
                    if not user_found:
                        return False
                        
                    return True
                    
                except Exception as e:
                    # Token likely expired or invalid
                    if os.path.exists(TOKEN_FILE):
                        os.remove(TOKEN_FILE)
                    return False
                    
    except Exception as e:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
    return False

def logIn():
    global firsttime, user_token, user_role
    if load_token():
        print(f"Welcome back to JobHive! You are logged in as {user_role}")
        return

    email = input("Enter your email address : ")
    password = input("Enter Your password : ")
    try:
        log_in = auth.sign_in_with_email_and_password(email, password)
        user_token = log_in['idToken']
        
        # Get user role from database
        user_data = db.child("users").order_by_child("email").equal_to(email).get()
        user_found = False
        for user in user_data.each():
            user_role = user.val().get('role')
            user_found = True
            break
            
        if not user_found:
            print("User profile not found. Please contact support.")
            return
        
        save_token(user_token, user_role)
        print(f"Successfully signed in as {user_role}")
        details()
    except Exception as e:
        error_message = str(e)
        if "INVALID_PASSWORD" in error_message:
            print("Invalid password. Please try again.")
        elif "EMAIL_NOT_FOUND" in error_message:
            print("Email not found. Please sign up first.")
        else:
            print(f"Login error: {error_message}")
            print("Please try again or contact support if the issue persists.")


def signUp():
    global firsttime, user_token, user_role
    if load_token():
        print(f"Welcome back to JobHive! You are logged in as {user_role}")
        return
        
    print("Welcome to JobHive!")
    choice = input("Are you a new user?[y/n]")
    if choice == "n":
        logIn()
    elif choice == "y":
        email = input("Enter your email address : ")
        password = input("Enter Your password : ")
        role = input("Are you an employer or applicant? [employer/applicant] : ").lower()
        
        if role not in ['employer', 'applicant']:
            print("Invalid role. Please choose either 'employer' or 'applicant'")
            return
            
        try:
            sign_up = auth.create_user_with_email_and_password(email, password)
            user_token = sign_up['idToken']
            user_role = role
            save_token(user_token, user_role)
            print(f"Successfully signed up as {role}")
            firsttime = True
            details()
        except:
            print("Email exists")
    else:
        print("Please answer in y or n")

def details():
    if firsttime == True:
        print("Hello! Let's add some credentials to your account")
        name = input("Enter your name : ")
        age = input("Enter your age : ")
        location = input("Enter your location : ")
        education = input("Enter your education : ")
        data = {
            "name": name,
            "age": age,
            "location": location,
            "education": education,
            "role": user_role,
            "email": auth.get_account_info(user_token)['users'][0]['email']
        }
        db.child("users").push(data)
        print("Data added successfully")
    else:
        print("Welcome back!")

def logout():
    global user_token, user_role
    if load_token():
        user_token = None
        user_role = None
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        print("Successfully logged out")
    else:
        print("No user is currently logged in")

def is_logged_in():
    return user_token is not None

def get_user_role():
    return user_role if user_role else None

if __name__ == "__main__":
    signUp()

'''
Modify `logIn` and `signUp` functions to work with Tkinter UI
Add Tkinter UI elements for user login and registration
'''
