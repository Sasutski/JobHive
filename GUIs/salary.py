import tkinter as tk
from GUIs.model import predict_salary, model

def create_gui(parent_frame=None):
    def on_predict():
        try:
            age = int(age_entry.get())
            gender = gender_entry.get()
            education_level = education_level_entry.get()
            job_title = job_title_entry.get()
            years_of_experience = int(years_of_experience_entry.get())
            country = country_entry.get()
            race = race_entry.get()
            senior = senior_entry.get()

            predicted_salary = predict_salary(age, gender, education_level, job_title, years_of_experience, country, race, senior)
            result_label.config(text=f"Predicted Salary: ${predicted_salary:.2f}")
        except Exception as e:
            result_label.config(text=f"Error: {str(e)}")

    if parent_frame is None:
        root = tk.Tk()
    else:
        root = parent_frame

    tk.Label(root, text="Age").grid(row=1, column=0)
    age_entry = tk.Entry(root)
    age_entry.grid(row=1, column=1)

    tk.Label(root, text="Gender").grid(row=2, column=0)
    gender_entry = tk.Entry(root)
    gender_entry.grid(row=2, column=1)

    tk.Label(root, text="Education Level").grid(row=3, column=0)
    education_level_entry = tk.Entry(root)
    education_level_entry.grid(row=3, column=1)

    tk.Label(root, text="Job Title").grid(row=4, column=0)
    job_title_entry = tk.Entry(root)
    job_title_entry.grid(row=4, column=1)

    tk.Label(root, text="Years of Experience").grid(row=5, column=0)
    years_of_experience_entry = tk.Entry(root)
    years_of_experience_entry.grid(row=5, column=1)

    tk.Label(root, text="Country").grid(row=6, column=0)
    country_entry = tk.Entry(root)
    country_entry.grid(row=6, column=1)

    tk.Label(root, text="Race").grid(row=7, column=0)
    race_entry = tk.Entry(root)
    race_entry.grid(row=7, column=1)

    tk.Label(root, text="Senior").grid(row=8, column=0)
    senior_entry = tk.Entry(root)
    senior_entry.grid(row=8, column=1)

    predict_button = tk.Button(root, text="Predict Salary", command=on_predict)
    predict_button.grid(row=9, column=0, columnspan=2)

    result_label = tk.Label(root, text="")
    result_label.grid(row=10, column=0, columnspan=2)

    if parent_frame is None:
        root.mainloop()

if __name__ == "__main__":
    model()
    create_gui()
