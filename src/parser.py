import os
import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts structured text from multi-column PDF resumes using pdfplumber.
    """
    if not os.path.exists(pdf_path):
        print(f"[parser] Error: File not found at {pdf_path}")
        return ""

    extracted_pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text(layout=True)
                if page_text:
                    extracted_pages.append(page_text.strip())

        return "\n\n".join(extracted_pages).strip()

    except Exception as e:
        print(f"[parser] Error reading PDF {pdf_path}: {e}")
        return ""


if __name__ == "__main__":
    sample_path = os.path.join(os.path.dirname(__file__), "..", "temp_uploads", "sample.pdf")
    text = extract_text_from_pdf(sample_path)
    print("Extracted Length:", len(text))