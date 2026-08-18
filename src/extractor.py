import re
import spacy

print("[extractor] Initializing NER & Skill Extractor...")
nlp = spacy.load("en_core_web_sm")

TECHNICAL_SKILLS = [
    # Languages
    "python", "java", "c++", "c", "c#", "javascript", "typescript", "golang", "rust", "sql", "r", "php",
    # Frontend
    "react", "react js", "next js", "vue", "angular", "html", "css", "tailwind", "bootstrap", "redux",
    # Backend & Frameworks
    "node js", "express", "express js", "fastapi", "flask", "django", "spring boot", "rest api", "graphql", "microservices",
    # Databases & Caching
    "mongodb", "postgresql", "mysql", "redis", "sqlite", "oracle", "elasticsearch",
    # Cloud & DevOps
    "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "git", "github", "linux", "jenkins",
    # AI / ML / Data
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "scikit-learn", "data science", "pandas", "numpy", "opencv", "llm", "genai", "sbert",
    # Concepts & Stacks
    "mern", "mean", "full stack", "backend", "frontend", "devops", "system design"
]


def extract_metadata(raw_text: str) -> dict:
    """
    Extracts named entities (spaCy) and technical skills (regex word boundaries)
    from candidate text.
    """
    if not raw_text:
        return {"entities": [], "skills_found": []}

    doc = nlp(raw_text[:4000])

    metadata = {
        "entities": [],
        "skills_found": []
    }

    # Extract high-confidence entities
    for ent in doc.ents:
        if ent.label_ in ["GPE", "ORG", "PERSON"]:
            metadata["entities"].append({
                "text": ent.text.strip(),
                "label": ent.label_
            })

    # Exact word-boundary skill matching (prevents substrings like "c" in "experience")
    text_lower = raw_text.lower()
    for skill in TECHNICAL_SKILLS:
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, text_lower):
            metadata["skills_found"].append(skill)

    metadata["skills_found"] = list(dict.fromkeys(metadata["skills_found"]))
    return metadata


if __name__ == "__main__":
    test_text = "Experienced full stack engineer in Hyderabad with hands-on skills in Python, C, React JS, Docker, and SQL."
    print(extract_metadata(test_text))