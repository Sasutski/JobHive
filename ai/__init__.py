import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
###from resume_review import compare_resumes  # Import the compare_resumes function from resume_review.py

# Set up the main window
root = tk.Tk()
root.title("Job Hive")

# Create and pack the main label with the word "Jobhive"
MainLabel = tk.Label(root, text="Jobhive", font=("Roboto", 24))
MainLabel.pack(pady=50)

# Create a label for the icon (initially empty)
icon_label = tk.Label(root)
icon_label.pack(pady=20)

# Function to handle PDF upload
def upload_pdf():
    global uploaded_resume  # Store the uploaded resume path
    file_path = filedialog.askopenfilename(
        title="Select Resume",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )
    
    if file_path:
        if file_path.lower().endswith(".pdf"):  # Check if it's a valid PDF
            uploaded_resume = file_path
            messagebox.showinfo("File Selected", f"Successfully uploaded: {file_path.split('/')[-1]}")
            
            # Change the icon to a success image
            try:
                success_image = Image.open("ai/Success.png")  # Replace with your actual image path
                success_image = success_image.resize((50, 50))  # Resize if needed
                success_icon = ImageTk.PhotoImage(success_image)
                icon_label.config(image=success_icon)
                icon_label.image = success_icon  # Keep a reference to the image
            except Exception as e:
                messagebox.showerror("Image Error", f"Error loading image: {e}")
        else:
            messagebox.showerror("Invalid File", "Please upload a PDF file.")
    else:
        messagebox.showwarning("No File", "No file selected. Please try again.")

# Function to analyze the uploaded resume and provide feedback
def analyze_resume():
    global uploaded_resume  # Use the uploaded resume file
    if 'uploaded_resume' in globals():  # Check if a resume has been uploaded
        try:
            ###feedback = compare_resumes('<path_to_model_resume>', uploaded_resume)  # Comparing with a model resume
            messagebox.showinfo("Resume Analysis", "testing suck my dick")  # Show the feedback in a messagebox
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during analysis: {e}")
    else:
        messagebox.showwarning("No Resume", "Please upload a resume first.")

# Create and pack the upload button
upload_button = tk.Button(root, text="Upload Resume (PDF)", font=("Roboto", 14), command=upload_pdf)
upload_button.pack(pady=20)

# Create and pack the "Analyze Resume" button
analyze_button = tk.Button(root, text="Analyze Resume", font=("Roboto", 14), command=analyze_resume)
analyze_button.pack(pady=20)

# Run the application
root.mainloop()
