from google import genai
import PyPDF2
import base64

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def compare_resumes(model_resume_path, candidate_resume_path, html_label=None):
    # Read and encode the candidate's resume
    with open(candidate_resume_path, "rb") as doc_file:
        doc_data = base64.standard_b64encode(doc_file.read()).decode("utf-8")

    # Read and encode the employer's model resume
    with open(model_resume_path, "rb") as model_file:
        model_data = base64.standard_b64encode(model_file.read()).decode("utf-8")


    # Initialize Gemini AI client
    client = genai.Client(api_key="AIzaSyBlK25lcxrb9krNnh0PwDFyyae9Vn6rNqA")

    # Prepare the prompt for resume comparison with markdown formatting
    prompt = (
        "You are a professional resume reviewer. "
        "Please compare the following candidate's resume with the employer's model resume. "
        "Provide a brief summary of the employer's model resume and of the strengths of the employer's model resume. "
        "Provide detailed feedback on the candidate's resume, highlighting strengths, weaknesses, "
        "and areas for improvement. Be specific and constructive in your feedback.\n\n"
        f"Employer's Model Resume (encoded in base64):\n{doc_data}\n\n"
        f"Candidate's Resume (encoded in base64):\n{model_data}\n\n"
        "Feedback:"
    )

    try:
        # Initialize feedback header
        feedback = "# Resume Comparison Analysis\n\n"
        if html_label:
            html_label.set_html(feedback)
            html_label.update()

        # Generate analysis using Gemini AI with streaming
        response = client.models.generate_content_stream(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        # Process the streaming response
        for chunk in response:
            if chunk.text:
                feedback += chunk.text
                if html_label:
                    from markdown import markdown
                    html_content = markdown(feedback)
                    html_label.set_html(html_content)
                    html_label.update()

        return feedback
    except Exception as e:
        error_msg = f"Error analyzing resumes: {str(e)}"
        if html_label:
            html_label.set_html(f"<p style='color: red;'>{error_msg}</p>")
            html_label.update()
        return error_msg

def display_feedback_window(model_resume_path, candidate_resume_path):
    """Display resume feedback in a new Tkinter window with real-time updates and markdown rendering"""
    from tkinter import Tk, ttk
    from tkhtmlview import HTMLLabel
    
    # Create feedback window
    feedback_window = Tk()
    feedback_window.title("Resume Feedback")
    feedback_window.geometry("800x600")
    
    # Configure window style
    style = ttk.Style()
    style.configure('Feedback.TFrame', background='#2c3e50')
    
    # Create frame for the HTML label
    frame = ttk.Frame(feedback_window, style='Feedback.TFrame')
    frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Create HTML label for markdown rendering
    html_label = HTMLLabel(frame, html="<h1>Analyzing resumes...</h1>", background='#ffffff', padx=10, pady=10)
    html_label.pack(fill='both', expand=True)
    
    # Center window on screen
    feedback_window.update_idletasks()
    width = feedback_window.winfo_width()
    height = feedback_window.winfo_height()
    x = (feedback_window.winfo_screenwidth() // 2) - (width // 2)
    y = (feedback_window.winfo_screenheight() // 2) - (height // 2)
    feedback_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the analysis in the same thread since we're using streaming
    compare_resumes(model_resume_path, candidate_resume_path, html_label)
    
    feedback_window.mainloop()

def handle_resume_upload(model_resume_path=None):
    """Handle resume upload and feedback display in Tkinter UI"""
    from tkinter import filedialog, messagebox
    
    # If no model resume provided, ask user to select one
    if not model_resume_path:
        model_resume_path = filedialog.askopenfilename(
            title="Select Model Resume",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not model_resume_path:
            return
    
    # Ask user to select their resume
    candidate_resume_path = filedialog.askopenfilename(
        title="Select Your Resume",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    if candidate_resume_path:
        try:
            # Display feedback window with real-time updates
            display_feedback_window(model_resume_path, candidate_resume_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze resumes: {str(e)}")

if __name__ == "__main__":
    handle_resume_upload()