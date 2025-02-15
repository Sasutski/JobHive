'''Initialize Tkinter UI and launch the dashboard'''
from tkinter import Tk
from GUI.dashboard import DashboardApp

def main():
    root = Tk()
    app = DashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
