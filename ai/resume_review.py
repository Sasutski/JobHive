from google import genai
import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def compare_resumes(model_resume_path, candidate_resume_path):
    # Extract text from both PDFs
    model_text = extract_text_from_pdf(model_resume_path)
    candidate_text = extract_text_from_pdf(candidate_resume_path)

    # Initialize Gemini AI client
    client = genai.Client(api_key="AIzaSyBlK25lcxrb9krNnh0PwDFyyae9Vn6rNqA")

    # Prepare the prompt for resume comparison
    prompt = f"""Compare these two resumes and provide detailed feedback:

Model Resume:
{model_text}

Candidate Resume:
{candidate_text}

Please analyze:
1. Key skills and qualifications comparison
2. Experience and achievements alignment
3. Format and presentation
4. Specific improvement suggestions
5. Overall match percentage

Provide constructive feedback that will help improve the candidate's resume."""

    # Generate analysis using Gemini AI
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text

def main():
    model_resume_path = 'assets/resumes/test_model_resume.pdf'
    candidate_resume_path = 'assets/resumes/test_candidate_resume.pdf'
    
    try:
        feedback = compare_resumes(model_resume_path, candidate_resume_path)
        print("\nResume Comparison Analysis:")
        print("-" * 50)
        print(feedback)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()


'''
Modify `compare_resumes` function to return feedback as a string
Add a function to handle resume upload and feedback display in Tkinter UI
'''