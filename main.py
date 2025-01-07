# from salary.py
from salary import *
from tkinter import *
from tkinter import ttk

    
def salary_expectation():
    age = int(input("Enter your age: "))
    gender = input("Enter your gender (Male/Female): ")
    education_level = int(input("Enter your education level (1-5): "))
    job_title = input("Enter your job title: ")
    years_of_experience = int(input("Enter your years of experience: "))
    country = input("Enter your country: ")
    race = input("Enter you race: ")
    senior = int(input("Enter 1 if you are a senior, 0 otherwise: "))
    return predict_salary(age, gender, education_level, job_title, years_of_experience, country, race, senior)

def predict_salary_gui():
    age = int(age_var.get())
    gender = gender_var.get()
    education_level = int(education_level_var.get())
    job_title = job_title_var.get()
    years_of_experience = int(years_of_experience_var.get())
    country = country_var.get()
    race = race_var.get()
    senior = int(senior_var.get())
    predicted_salary = predict_salary(age, gender, education_level, job_title, years_of_experience, country, race, senior)
    result_var.set(f"Predicted Salary: ${predicted_salary:.0f} per year")

root = Tk()
root.title("Job Seeker")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

age_var = StringVar()
gender_var = StringVar()
education_level_var = StringVar()
job_title_var = StringVar()
years_of_experience_var = StringVar()
country_var = StringVar()
race_var = StringVar()
senior_var = StringVar()
result_var = StringVar()

ttk.Label(mainframe, text="Age").grid(column=1, row=1, sticky=W)
ttk.Entry(mainframe, width=7, textvariable=age_var).grid(column=2, row=1, sticky=(W, E))

ttk.Label(mainframe, text="Gender").grid(column=1, row=2, sticky=W)
ttk.Combobox(mainframe, textvariable=gender_var, values=["Male", "Female"]).selection_clear()


ttk.Label(mainframe, text="Education Level (1-5)").grid(column=1, row=3, sticky=W)
ttk.Entry(mainframe, width=7, textvariable=education_level_var).grid(column=2, row=3, sticky=(W, E))

ttk.Label(mainframe, text="Job Title").grid(column=1, row=4, sticky=W)
ttk.Entry(mainframe, width=7, textvariable=job_title_var).grid(column=2, row=4, sticky=(W, E))

ttk.Label(mainframe, text="Years of Experience").grid(column=1, row=5, sticky=W)
ttk.Entry(mainframe, width=7, textvariable=years_of_experience_var).grid(column=2, row=5, sticky=(W, E))

ttk.Label(mainframe, text="Country").grid(column=1, row=6, sticky=W)
ttk.Entry(mainframe, width=7, textvariable=country_var).grid(column=2, row=6, sticky=(W, E))

ttk.Label(mainframe, text="Race").grid(column=1, row=7, sticky=W)
ttk.Entry(mainframe, width=7, textvariable=race_var).grid(column=2, row=7, sticky=(W, E))

ttk.Label(mainframe, text="Senior (1/0)").grid(column=1, row=8, sticky=W)
ttk.Entry(mainframe, width=7, textvariable=senior_var).grid(column=2, row=8, sticky=(W, E))

ttk.Button(mainframe, text="Predict Salary", command=predict_salary_gui).grid(column=2, row=9, sticky=W)
ttk.Label(mainframe, textvariable=result_var).grid(column=2, row=10, sticky=(W, E))

root.mainloop()




