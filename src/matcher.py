from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from extractor import extract_metadata
from llm_analyzer import analyze_resume_against_jd
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_tfidf_score(resume_text, jd_text):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)

def get_sbert_score(resume_text, jd_text):
    embeddings = model.encode([jd_text, resume_text])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(score) * 100, 2)

def find_skill_gaps(resume_text, jd_text):
    jd_skills = set(extract_metadata(jd_text)["skills_found"])
    resume_skills = set(extract_metadata(resume_text)["skills_found"])
    
    missing_skills = list(jd_skills - resume_skills)
    return missing_skills

# Converts the LLM's qualitative project_depth rating into a number, so it
# can be combined mathematically with the SBERT score. Without this, SBERT
# (pure text similarity) and the LLM's judgment (actual skill/experience fit)
# can disagree and produce a ranking that contradicts the LLM's own reasoning -
# e.g. the top-ranked candidate being the one the LLM says is the worst fit.
DEPTH_TO_SCORE = {
    "low": 0,
    "medium": 50,
    "high": 100,
    "unknown": 50  # neutral fallback if the LLM call failed
}

def get_combined_score(sbert_score, llm_insight):
    """
    Blends the SBERT semantic score with the LLM's project_depth judgment
    into one final ranking score.

    Weights: 60% SBERT (grounded in actual text similarity),
             40% LLM depth judgment (softer, more subjective signal).
    These weights are tunable - the point is that the LLM's opinion now
    actually influences the ranking instead of sitting next to it unused.
    """
    depth_score = DEPTH_TO_SCORE.get(llm_insight.get("project_depth", "unknown"), 50)
    combined = (sbert_score * 0.6) + (depth_score * 0.4)
    return round(combined, 2)

def rank_resumes(resume_list, jd_text):
    ranked_results = []
    
    for idx, resume_text in enumerate(resume_list):
        tfidf = get_tfidf_score(resume_text, jd_text)
        sbert = get_sbert_score(resume_text, jd_text)
        gaps = find_skill_gaps(resume_text, jd_text)
        llm_insight = analyze_resume_against_jd(resume_text, jd_text)
        combined_score = get_combined_score(sbert, llm_insight)
        
        ranked_results.append({
            "candidate_id": f"Candidate {idx + 1}",
            "tfidf_score": tfidf,
            "sbert_score": sbert,
            "combined_score": combined_score,
            "missing_skills": gaps,
            "llm_insight": llm_insight
        })
        
    # Rank by the combined score, not raw SBERT alone - this is what makes
    # the LLM's reasoning actually matter to the final order, not just be
    # displayed alongside it.
    ranked_results.sort(key=lambda x: x['combined_score'], reverse=True)
    return ranked_results

if __name__ == "__main__":
    sample_jd = "Looking for a software engineer skilled in javascript, react js, and node js for backend api development. Must know sql."
    
    candidates = [
        "Full stack web development using mern stack. Built application backend using express. Knows java and c.",
        "Frontend developer with strong html, css, and react js experience. No backend knowledge.",
        "Database administrator skilled in sql and mongodb. Knows python for scripting."
    ]
    
    print("\n--- Ranking Candidates ---")
    results = rank_resumes(candidates, sample_jd)
    print(json.dumps(results, indent=4))