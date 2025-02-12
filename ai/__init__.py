import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

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
    file_path = filedialog.askopenfilename(
        title="Select Resume",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )
    
    if file_path:
        # Check if the selected file is a PDF
        if file_path.lower().endswith(".pdf"):
            messagebox.showinfo("File Selected", f"Successfully uploaded: {file_path.split('/')[-1]}")
            
            # Change the icon to a success image
            success_image = Image.open("ai/Success.png")  # replace with your image file
            success_image = success_image.resize((50, 50))  # Resize if needed
            success_icon = ImageTk.PhotoImage(success_image)
            icon_label.config(image=success_icon)
            icon_label.image = success_icon  # Keep a reference to the image
        else:
            messagebox.showerror("Invalid File", "Please upload a PDF file.")
    else:
        messagebox.showwarning("No File", "No file selected. Please try again.")

# Create and pack the upload button
upload_button = tk.Button(root, text="Upload Resume (PDF)", font=("Roboto", 14), command=upload_pdf)
upload_button.pack(pady=20)

# Run the application
root.mainloop()