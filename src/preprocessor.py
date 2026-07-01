import spacy
import re

# Load the lightweight English NLP model you downloaded yesterday
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """
    Sanitizes raw resume text for the ML model.
    Handles lowercase, regex stripping, and spaCy lemmatization.
    """
    if not text:
        return ""

    # 1. Lowercase everything 
    text = text.lower()

    # 2. Regex Cleaning
    # Remove URLs and emails
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    # Remove all punctuation and numbers, replacing them with a space
    text = re.sub(r'[^a-z\s]', ' ', text)

    # 3. The NLP Magic: Tokenization, Stopwords, and Lemmatization
    doc = nlp(text)
    
    cleaned_tokens = []
    for token in doc:
        # Keep only alphabetic tokens that are NOT stopwords ("the", "and", "with")
        # and ignore tiny 1-letter artifacts
        if token.is_alpha and not token.is_stop and len(token.text) > 1:
            # Append the lemma_ (the base dictionary form of the word)
            cleaned_tokens.append(token.lemma_)
            
    # Rejoin the clean words into a single string separated by spaces
    return " ".join(cleaned_tokens)

# --- Testing the pipeline ---
if __name__ == "__main__":
    # Your actual raw resume snippet
    sample_raw_text = """Namani Sai Charan
Hyderabad | Email: charannamani.cn7@gmail.com | Phone: +91 6301484459| GitHub: github.com/charannamani
Computer Science (Data Science) undergraduate with hands-on experience in full-stack web development, AI/ML applications, and backend API"""
    
    print("\n--- Original Raw Text ---")
    print(sample_raw_text)
    
    print("\n--- Cleaned ML-Ready Text ---")
    print(clean_text(sample_raw_text))