from GUIs.salary import create_gui as create_salary_gui
from GUIs.review_resume import main_gui as create_review_resume_gui
from tkinter import *
from tkinter import ttk

def main_gui():
    def open_salary_predictor():
        # Clear the mainframe and load the Salary Predictor GUI
        for widget in mainframe.winfo_children():
            widget.destroy()
        create_salary_gui(mainframe)
        back_button = ttk.Button(mainframe, text="Back", command=show_home)
        back_button.grid(row=99, column=0, columnspan=2, sticky=(W, E))

    def open_review_resume():
        # Clear the mainframe and load the Review Resume GUI
        for widget in mainframe.winfo_children():
            widget.destroy()
        create_review_resume_gui(mainframe)
        back_button = ttk.Button(mainframe, text="Back", command=show_home)
        back_button.grid(row=99, column=0, sticky=(W, E))

    root = Tk()
    root.title("Job Seeker")

    # Main frame for dynamic content
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    def show_home():
        # Clear the mainframe and display the home screen
        for widget in mainframe.winfo_children():
            widget.destroy()
        ttk.Label(mainframe, text="Welcome to Job Seeker!").grid(column=1, row=1, sticky=(W, E))
        ttk.Button(mainframe, text="Salary Predictor", command=open_salary_predictor).grid(column=1, row=2, sticky=(W, E))
        ttk.Button(mainframe, text="Review Resume", command=open_review_resume).grid(column=1, row=3, sticky=(W, E))

    # Show the home screen initially
    show_home()
    root.mainloop()

if __name__ == "__main__":
    main_gui()
