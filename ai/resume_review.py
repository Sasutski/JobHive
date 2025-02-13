import os
from google import genai
import base64
from tkinter import *
from tkinter import ttk, filedialog
from tkhtmlview import HTMLLabel
import markdown

# Configure Generative AI API
API_KEY = 'AIzaSyBlK25lcxrb9krNnh0PwDFyyae9Vn6rNqA'
client = genai.Client(api_key=API_KEY)

# Function to select a file
def select_file(var):
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    var.set(file_path)

# Function to render markdown in Tkinter
def render_markdown_in_tkinter(output_text):
    """Render markdown text in a Tkinter widget."""
    # Create a Text widget if it doesn't exist
    if not hasattr(result_text, 'text_widget'):
        result_text.text_widget = Text(result_text, wrap=WORD, bg='black', fg='white', font=('Helvetica', 10))
        result_text.text_widget.pack(fill=BOTH, expand=True)
        result_text.text_widget.configure(state='normal')
    
    # Clear existing content
    result_text.text_widget.delete('1.0', END)
    
    # Insert new content
    html_content = markdown.markdown(output_text)
    result_text.text_widget.insert('1.0', html_content)
    
    # Make it read-only to prevent editing
    result_text.text_widget.configure(state='disabled')
    html_content = f"<div style='color: white;'>{html_content}</div>"
    result_text.set_html(html_content)

# Function to review the resumes
def review_resume():
    candidate_resume_path = candidate_resume_var.get()
    employer_model_resume_path = employer_model_resume_var.get()

    if not candidate_resume_path or not employer_model_resume_path:
        result_var.set("Please select both resumes.")
        return

    # Read and encode the candidate's resume
    with open(candidate_resume_path, "rb") as doc_file:
        doc_data = base64.standard_b64encode(doc_file.read()).decode("utf-8")

    # Read and encode the employer's model resume
    with open(employer_model_resume_path, "rb") as model_file:
        model_data = base64.standard_b64encode(model_file.read()).decode("utf-8")

    prompt = (
        "You are a professional resume reviewer. "
        "Please compare the following candidate's resume with the employer's model resume. "
        "Provide a brief summary of the employer's model resume and of the strengths of the employer's model resume. "
        "Provide detailed feedback on the candidate's resume, highlighting strengths, weaknesses, "
        "and areas for improvement. Be specific and constructive in your feedback.\n\n"
        f"Employer's Model Resume (encoded in base64):\n{model_data}\n\n"
        f"Candidate's Resume (encoded in base64):\n{doc_data}\n\n"
        "Feedback:"
    )

    try:
        response = client.models.generate_content_stream(
            model='gemini-1.5-flash',
            contents=[
                {'mime_type': 'application/pdf', 'data': model_data}, 
                {'mime_type': 'application/pdf', 'data': doc_data}, 
                prompt
            ]
        )
        # Accumulate text chunks from the stream
        markdown_output = ""
        for chunk in response:
            if chunk.text:
                markdown_output += chunk.text
    except Exception as e:
        markdown_output = f"An error occurred: {e}"

    # Render the markdown output
    render_markdown_in_tkinter(markdown_output)

def main_gui(parent_frame=None):
    global candidate_resume_var, employer_model_resume_var, result_var, result_text

    if parent_frame is None:
        root = Tk()  # Create a standalone Tkinter window
    else:
        root = parent_frame  # Use the provided parent frame for embedding

    # Variables for storing file paths and results
    candidate_resume_var = StringVar()
    employer_model_resume_var = StringVar()
    result_var = StringVar()

    # Main content frame
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Candidate Resume Selection
    ttk.Label(mainframe, text="Candidate's Resume:").grid(column=1, row=1, sticky=W)
    ttk.Entry(mainframe, width=50, textvariable=candidate_resume_var).grid(column=2, row=1, sticky=(W, E))
    ttk.Button(mainframe, text="Browse", command=lambda: select_file(candidate_resume_var)).grid(column=3, row=1, sticky=W)

    # Employer Model Resume Selection
    ttk.Label(mainframe, text="Employer's Model Resume:").grid(column=1, row=2, sticky=W)
    ttk.Entry(mainframe, width=50, textvariable=employer_model_resume_var).grid(column=2, row=2, sticky=(W, E))
    ttk.Button(mainframe, text="Browse", command=lambda: select_file(employer_model_resume_var)).grid(column=3, row=2, sticky=W)

    # Review Resume Button
    ttk.Button(mainframe, text="Review Resume", command=review_resume).grid(column=2, row=3, sticky=W)

    # Result Frame
    result_frame = ttk.Frame(mainframe)
    result_frame.grid(column=1, row=4, columnspan=3, sticky=(W, E, N, S))
    result_frame.columnconfigure(0, weight=1)
    result_frame.rowconfigure(0, weight=1)

    # Create a Frame to hold the result text and scrollbar
    result_text = Frame(result_frame, bg='black')
    result_text.grid(column=0, row=0, sticky=(N, S, E, W))
    result_text.columnconfigure(0, weight=1)
    result_text.rowconfigure(0, weight=1)

    # Scrollbar for result text
    scrollbar = ttk.Scrollbar(result_frame, orient=VERTICAL)
    scrollbar.grid(column=1, row=0, sticky=(N, S))

    if parent_frame is None:
        root.mainloop()  # Run the main loop only in standalone mode

if __name__ == "__main__":
    main_gui()