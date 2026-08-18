import re
import spacy

print("[preprocessor] Loading spaCy model (en_core_web_sm)...")
nlp = spacy.load("en_core_web_sm")


def normalize_raw_text(text: str) -> str:
    """
    Normalizes whitespace and special Unicode characters while PRESERVING
    full sentence structures, capitalization, and punctuation for SBERT and LLMs.
    """
    if not text:
        return ""
    # Normalize bullet points and dashes
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25CB\u25CF]', ' ', text)
    # Normalize line breaks and multiple spaces
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def clean_text_for_lexical(text: str) -> str:
    """
    Strips punctuation, numbers, and stopwords with lemmatization.
    Used strictly for TF-IDF vectorization and keyword matching.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)

    doc = nlp(text)
    cleaned_tokens = [
        token.lemma_
        for token in doc
        if token.is_alpha and not token.is_stop and len(token.text) > 1
    ]

    return " ".join(cleaned_tokens)


if __name__ == "__main__":
    sample = "Namani Sai Charan | +91 6301484459 | charannamani.cn7@gmail.com | Built REST APIs with FastAPI & Docker."
    print("Normalized Raw:\n", normalize_raw_text(sample))
    print("\nLexical Cleaned:\n", clean_text_for_lexical(sample))