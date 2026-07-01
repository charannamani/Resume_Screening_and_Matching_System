from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import os

from parser import extract_text_from_pdf
from preprocessor import clean_text
from matcher import rank_resumes

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Resume Matcher API Running"


def init_db():
    conn = sqlite3.connect("matches.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS results
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     timestamp TEXT,
     jd_text TEXT,
     resume_text TEXT,
     tfidf_score REAL,
     sbert_score REAL)
    """)
    conn.commit()
    conn.close()


@app.route("/match", methods=["POST"])
def match_endpoint():

    jd_text = request.form.get("jd")
    uploaded_files = request.files.getlist("resumes")

    if not jd_text or not uploaded_files:
        return jsonify({"error": "Missing JD or files"}), 400

    resumes = []

    os.makedirs("temp_uploads", exist_ok=True)

    for file in uploaded_files:
        path = os.path.join("temp_uploads", file.filename)
        file.save(path)

        raw_text = extract_text_from_pdf(path)

        if raw_text:
            cleaned = clean_text(raw_text)
            resumes.append(cleaned)

        os.remove(path)

    ranked_results = rank_resumes(resumes, jd_text)

    return jsonify({
        "status": "success",
        "results": ranked_results
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)