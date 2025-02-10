'''
Implement a Tkinter UI dashboard with sections for user login, resume upload, and feedback display
Integrate `gui/login.py` for user login and registration
Integrate `ai/resume_review.py` for resume feedback
'''

from tkinter import Tk
from login import load_token, get_user_role

# Creates the display
root = Tk(screenName=None, baseName=None, className='Dashboard', useTk=1)
if load_token():
    user_role = get_user_role()
    if user_role:
        print(f"Welcome back to JobHive! You are logged in as {user_role}")
    else:
        print("Error: Unable to retrieve user role")

# Initialises the mainloop
root.mainloop()