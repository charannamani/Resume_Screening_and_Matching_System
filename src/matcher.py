import concurrent.futures
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from extractor import extract_metadata
from preprocessor import normalize_raw_text, clean_text_for_lexical
from llm_analyzer import analyze_resume_against_jd

print("[matcher] Loading SentenceTransformer (all-MiniLM-L6-v2)...")
sbert_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

DEPTH_WEIGHTS = {
    "low": 30.0,
    "medium": 70.0,
    "high": 100.0,
    "unknown": 50.0
}


def get_tfidf_score(clean_resume: str, clean_jd: str) -> float:
    """Calculates TF-IDF lexical similarity."""
    if not clean_resume.strip() or not clean_jd.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([clean_jd, clean_resume])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(score) * 100, 2)
    except Exception:
        return 0.0


def get_sbert_score(raw_resume: str, raw_jd: str) -> float:
    """Calculates SBERT semantic embedding similarity on natural text."""
    if not raw_resume.strip() or not raw_jd.strip():
        return 0.0
    try:
        embeddings = sbert_model.encode([raw_jd, raw_resume], show_progress_bar=False)
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return round(float(score) * 100, 2)
    except Exception:
        return 0.0


def analyze_skills(raw_resume: str, raw_jd: str) -> dict:
    """Extracts matched and missing skills between JD and Resume."""
    jd_skills = set(extract_metadata(raw_jd)["skills_found"])
    resume_skills = set(extract_metadata(raw_resume)["skills_found"])

    missing = list(jd_skills - resume_skills)
    matched = list(jd_skills.intersection(resume_skills))

    return {
        "matched_skills": matched,
        "missing_skills": missing
    }


def calculate_combined_score(sbert_score: float, tfidf_score: float, llm_insight: dict) -> float:
    """
    Weighted blended ranking score:
    - 50% SBERT (Dense Semantic Fit)
    - 20% TF-IDF (Exact Lexical Fit)
    - 30% LLM Qualitative Project Depth
    """
    depth_str = llm_insight.get("project_depth", "medium").lower()
    depth_score = DEPTH_WEIGHTS.get(depth_str, 50.0)

    combined = (sbert_score * 0.50) + (tfidf_score * 0.20) + (depth_score * 0.30)
    return round(combined, 2)


def process_single_candidate(candidate_id: str, raw_resume: str, norm_jd: str, clean_jd: str) -> dict:
    """Evaluates an individual candidate across all scoring layers."""
    norm_resume = normalize_raw_text(raw_resume)
    clean_resume = clean_text_for_lexical(raw_resume)

    tfidf = get_tfidf_score(clean_resume, clean_jd)
    sbert = get_sbert_score(norm_resume, norm_jd)
    skills = analyze_skills(norm_resume, norm_jd)
    llm_insight = analyze_resume_against_jd(norm_resume, norm_jd)

    combined = calculate_combined_score(sbert, tfidf, llm_insight)

    return {
        "candidate_id": candidate_id,
        "tfidf_score": tfidf,
        "sbert_score": sbert,
        "combined_score": combined,
        "matched_skills": skills["matched_skills"],
        "missing_skills": skills["missing_skills"],
        "llm_insight": llm_insight
    }


def rank_resumes(resume_tuples: list, raw_jd: str) -> list:
    """
    Processes all candidate resumes concurrently using a thread pool.
    resume_tuples: list of (candidate_name, raw_resume_text)
    """
    norm_jd = normalize_raw_text(raw_jd)
    clean_jd = clean_text_for_lexical(raw_jd)

    ranked_results = []

    # Parallel evaluation cuts batch API roundtrips from ~15s to ~1.5s
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_map = {
            executor.submit(process_single_candidate, cid, text, norm_jd, clean_jd): cid
            for cid, text in resume_tuples
        }

        for future in concurrent.futures.as_completed(future_map):
            try:
                res = future.result()
                ranked_results.append(res)
            except Exception as e:
                cid = future_map[future]
                print(f"[matcher] Failed candidate {cid}: {e}")

    ranked_results.sort(key=lambda x: x["combined_score"], reverse=True)
    return ranked_results