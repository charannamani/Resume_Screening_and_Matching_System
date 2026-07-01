import spacy
import json

print("Loading spaCy model for extraction...")
nlp = spacy.load("en_core_web_sm")


SKILL_DB = [
    "java", "c", "python", "javascript", "sql", "html", "css", 
    "node js", "express js", "react js", "mongodb", "mern",
    "ai", "ml", "nlp", "data science", "full stack", "backend", "api"
]

def extract_metadata(cleaned_text):
    """
    Extracts structured metadata (skills and entities) from cleaned text.
    """
    doc = nlp(cleaned_text)
    
    metadata = {
        "entities": [],
        "skills_found": []
    }
    
    for ent in doc.ents:
        if ent.label_ in ["GPE", "ORG", "PERSON"]:
            metadata["entities"].append({"text": ent.text, "label": ent.label_})
            
    for skill in SKILL_DB:
        if skill.replace("-", " ") in cleaned_text:
            metadata["skills_found"].append(skill)
            
    return metadata

if __name__ == "__main__":
    sample_clean_text = "namani sai charan hyderabad email phone github github com charannamani computer science datum science undergraduate hand experience stack web development ai ml application backend api java python react js"
    
    print("\n--- Extracting Metadata ---")
    extracted_data = extract_metadata(sample_clean_text)
    
    print(json.dumps(extracted_data, indent=4))