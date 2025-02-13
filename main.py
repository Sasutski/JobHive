'''Initialize Tkinter UI and launch the dashboard'''
from tkinter import Tk
from gui.dashboard import DashboardApp

def main():
    root = Tk()
    app = DashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
