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

firsttime = False
user_token = None
TOKEN_FILE = 'user_token.json'

def save_token(token):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'token': token}, f)

def load_token():
    global user_token
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                user_token = data.get('token')
                return True
    except:
        pass
    return False

def logIn():
    global user_token
    email = input("Enter your email address : ")
    password = input("Enter Your password : ")
    try:
        log_in = auth.sign_in_with_email_and_password(email, password)
        user_token = log_in['idToken']
        save_token(user_token)
        print("Successfully signed In")
        details()
    except:
        print("Invalid email or password")

def signUp():
    global firsttime, user_token
    if load_token():
        print("Welcome back to JobHive!")
        return
        
    print("Welcome to JobHive!")
    choice = input("Are you a new user?[y/n]")
    if choice == "n":
        logIn()
    elif choice == "y":
        email = input("Enter your email address : ")
        password = input("Enter Your password : ")
        try:
            sign_up = auth.create_user_with_email_and_password(email, password)
            user_token = sign_up['idToken']
            save_token(user_token)
            print("Successfully signed Up")
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
            "education": education
        }
        db = firebase.database()
        db.child("users").push(data)
        print("Data added successfully")
    else:
        print("Welcome back!")

def logout():
    global user_token
    if user_token:
        user_token = None
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        print("Successfully logged out")
    else:
        print("No user is currently logged in")

def is_logged_in():
    return user_token is not None

signUp()