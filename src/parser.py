import pdfplumber
import os

def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text from a PDF file using pdfplumber.
    We use pdfplumber instead of PyPDF2 because resumes often use 
    columns and tables, which older libraries fail to read correctly.
    """
    text = ""
    try:
        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            # Loop through every page in the resume
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
        
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    sample_pdf_path = os.path.join(current_dir, "..", "data", "sample_resume.pdf")
    
    print(f"Attempting to read: {sample_pdf_path}")
    
    raw_text = extract_text_from_pdf(sample_pdf_path)
    
    if raw_text:
        print("\n--- Successfully Extracted Text (First 500 characters) ---")
        print(raw_text[:500]) 
    else:
        print("\nFailed to extract text. Please check if the file exists in the data folder.")