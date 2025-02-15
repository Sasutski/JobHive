import os
from pathlib import Path
from google import genai
import base64
from google.genai import types  # helper methods for constructing Parts

# Configure Generative AI API
API_KEY = 'AIzaSyBlK25lcxrb9krNnh0PwDFyyae9Vn6rNqA'
client = genai.Client(api_key=API_KEY)

def select_resume():
    """Get file paths from user input in terminal."""
    while True:
        candidate_resume_path = "assets/resumes/test_candidate_resume.pdf".strip()
        if os.path.exists(candidate_resume_path) and candidate_resume_path.endswith('.pdf'):
            break
        print("Invalid path. Please enter a valid path to a PDF file.")

    while True:
        employer_resume_path = "assets/resumes/test_model_resume.pdf".strip()
        if os.path.exists(employer_resume_path) and employer_resume_path.endswith('.pdf'):
            break
        print("Invalid path. Please enter a valid path to a PDF file.")

    return candidate_resume_path, employer_resume_path

def review_resume(candidate_resume_path: Path, employer_resume_path: Path):
    """Review and compare the resumes, printing feedback in chunks."""
    try:
        # Read the files
        with open(candidate_resume_path, "rb") as doc_file:
            candidate_bytes = doc_file.read()
        with open(employer_resume_path, "rb") as model_file:
            employer_bytes = model_file.read()

        # Optional: create base64 strings (for prompt context)
        candidate_data = base64.standard_b64encode(candidate_bytes).decode("utf-8")
        employer_data = base64.standard_b64encode(employer_bytes).decode("utf-8")

        # Build prompt including both resumes (base64 encoded for reference)
        prompt_text = (
            "You are a professional resume reviewer. "
            "Please compare the following candidate's resume with the employer's model resume. "
            "Provide a brief summary of the employer's model resume and its strengths. "
            "Then provide detailed feedback on the candidate's resume, highlighting strengths, weaknesses, "
            "and areas for improvement. Be specific and constructive.\n\n"
            f"Employer's Model Resume (base64):\n{employer_data}\n\n"
            f"Candidate's Resume (base64):\n{candidate_data}\n\n"
            "Feedback:"
        )

        # Create Part objects using helper methods
        employer_part = types.Part.from_bytes(data=employer_bytes, mime_type="application/pdf")
        candidate_part = types.Part.from_bytes(data=candidate_bytes, mime_type="application/pdf")
        prompt_part = types.Part.from_text(text=prompt_text)

        # Call the API using generate_content_stream; it returns an iterator over chunks
        stream = client.models.generate_content_stream(
            model='gemini-1.5-flash',
            contents=[employer_part, candidate_part, prompt_part]
        )

        print("\nFeedback (printing in chunks):\n")
        for chunk in stream:
            text = chunk.text or ""
            print(text, end="", flush=True)
        print()  # add newline after completion

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    candidate_path, employer_path = select_resume()
    review_resume(candidate_path, employer_path)
