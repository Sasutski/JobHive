from google import genai
import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def compare_resumes(model_resume_path, candidate_resume_path, html_label=None):
    # Extract text from both PDFs
    model_text = extract_text_from_pdf(model_resume_path)
    candidate_text = extract_text_from_pdf(candidate_resume_path)

    # Initialize Gemini AI client
    client = genai.Client(api_key="AIzaSyBlK25lcxrb9krNnh0PwDFyyae9Vn6rNqA")

    # Prepare the prompt for resume comparison with markdown formatting
    prompt = f"""Compare these two resumes and provide detailed feedback using markdown formatting:

Model Resume:
{model_text}

Candidate Resume:
{candidate_text}

Please analyze and format your response in markdown:
# Resume Analysis

## Key Skills and Qualifications
[Your analysis here]

## Experience and Achievements
[Your analysis here]

## Format and Presentation
[Your analysis here]

## Improvement Suggestions
[Your analysis here]

## Overall Match
[Percentage and summary]

Provide constructive feedback that will help improve the candidate's resume."""

    try:
        # Initialize feedback header
        feedback = "# Resume Comparison Analysis\n\n"
        if html_label:
            html_label.set_html(feedback)
            html_label.update()

        # Generate analysis using Gemini AI with streaming
        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
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
