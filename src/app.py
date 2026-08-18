import os
import json
import sqlite3
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from parser import extract_text_from_pdf
from matcher import rank_resumes

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "matches.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "temp_uploads")


def init_db():
    """Initializes the SQLite results table with full analytical schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        candidate_name TEXT,
        tfidf_score REAL,
        sbert_score REAL,
        combined_score REAL,
        matched_skills TEXT,
        missing_skills TEXT,
        llm_reasoning TEXT
    )
    """)
    conn.commit()
    conn.close()


def save_matches_to_db(results: list):
    """Persists ranking runs into SQLite for historical review."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()

        for r in results:
            c.execute("""
            INSERT INTO results (
                timestamp, candidate_name, tfidf_score, sbert_score, 
                combined_score, matched_skills, missing_skills, llm_reasoning
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now,
                r.get("candidate_id"),
                r.get("tfidf_score"),
                r.get("sbert_score"),
                r.get("combined_score"),
                json.dumps(r.get("matched_skills", [])),
                json.dumps(r.get("missing_skills", [])),
                json.dumps(r.get("llm_insight", {}))
            ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[app] Database save error: {e}")


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "service": "AI Resume Matcher & Screening Engine",
        "version": "2.0.0"
    })


@app.route("/match", methods=["POST"])
def match_endpoint():
    jd_text = request.form.get("jd", "").strip()
    uploaded_files = request.files.getlist("resumes")

    if not jd_text:
        return jsonify({"error": "Job description cannot be empty"}), 400

    if not uploaded_files or len(uploaded_files) == 0:
        return jsonify({"error": "At least one PDF resume must be uploaded"}), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    resume_tuples = []

    for file in uploaded_files:
        if not file.filename.lower().endswith(".pdf"):
            continue

        temp_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(temp_path)

        extracted_text = extract_text_from_pdf(temp_path)
        if extracted_text:
            # Preserve original filename as candidate label
            display_name = os.path.splitext(file.filename)[0]
            resume_tuples.append((display_name, extracted_text))

        if os.path.exists(temp_path):
            os.remove(temp_path)

    if not resume_tuples:
        return jsonify({"error": "Unable to extract valid text from provided PDF(s)"}), 400

    ranked_results = rank_resumes(resume_tuples, jd_text)
    save_matches_to_db(ranked_results)

    return jsonify({
        "status": "success",
        "total_evaluated": len(ranked_results),
        "results": ranked_results
    })


@app.route("/history", methods=["GET"])
def get_history():
    """Returns recent evaluation history from SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM results ORDER BY id DESC LIMIT 50")
        rows = c.fetchall()
        conn.close()

        history = [
            {
                "id": row[0],
                "timestamp": row[1],
                "candidate_name": row[2],
                "tfidf_score": row[3],
                "sbert_score": row[4],
                "combined_score": row[5],
                "matched_skills": json.loads(row[6]),
                "missing_skills": json.loads(row[7]),
                "llm_reasoning": json.loads(row[8])
            }
            for row in rows
        ]
        return jsonify({"status": "success", "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    init_db()
    print("[app] Starting AI Resume Matcher API on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)