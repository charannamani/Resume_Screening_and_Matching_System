import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:5000/match";

export default function App() {
  const [jd, setJd] = useState("");
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setError("");
  };

  const handleMatch = async () => {
    if (!jd.trim() || files.length === 0) {
      setError("Please add a job description and at least one PDF resume.");
      return;
    }

    const formData = new FormData();
    formData.append("jd", jd);
    files.forEach((file) => formData.append("resumes", file));

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(API_URL, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResults(response.data.results || []);
    } catch (err) {
      console.error(err);
      setResults(null);
      setError("Failed to connect to the backend engine on http://127.0.0.1:5000.");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (score >= 75) return "#34d399";
    if (score >= 50) return "#fbbf24";
    return "#f87171";
  };

  const depthBadgeColor = (depth) => {
    const d = (depth || "").toLowerCase();
    if (d === "high") return { bg: "#064e3b", text: "#6ee7b7", border: "#047857" };
    if (d === "medium") return { bg: "#451a03", text: "#fcd34d", border: "#b45309" };
    return { bg: "#450a0a", text: "#fca5a5", border: "#b91c1c" };
  };

  return (
    <div className="app">
      <style>{`
        .app {
          min-height: 100vh;
          background: radial-gradient(circle at top, #141b26 0%, #080c14 70%);
          color: #e2e8f0;
          padding: 40px 20px 80px;
        }
        .shell { max-width: 960px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 36px; }
        .eyebrow {
          font-size: 11px;
          letter-spacing: 3px;
          text-transform: uppercase;
          color: #38bdf8;
          font-weight: 700;
        }
        .title {
          font-size: 34px;
          font-weight: 800;
          margin: 6px 0 0;
          letter-spacing: -0.5px;
          color: #f8fafc;
        }
        .panel {
          background: #111827;
          border: 1px solid #1f293d;
          border-radius: 14px;
          padding: 24px;
          margin-bottom: 28px;
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        }
        .label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          color: #94a3b8;
          margin-bottom: 8px;
          display: block;
          font-weight: 600;
        }
        textarea {
          width: 100%;
          min-height: 130px;
          background: #090d16;
          border: 1px solid #283548;
          border-radius: 10px;
          padding: 14px;
          color: #f1f5f9;
          font-size: 14px;
          resize: vertical;
          font-family: inherit;
        }
        textarea:focus, input:focus { outline: 2px solid #38bdf8; outline-offset: 1px; }
        .file-row {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-top: 6px;
        }
        input[type="file"] {
          color: #94a3b8;
          font-size: 13px;
        }
        .file-count {
          font-size: 12px;
          color: #38bdf8;
          font-weight: 600;
        }
        .run-btn {
          width: 100%;
          margin-top: 20px;
          padding: 14px;
          border-radius: 10px;
          border: none;
          background: linear-gradient(135deg, #38bdf8, #2563eb);
          color: #ffffff;
          font-weight: 700;
          font-size: 15px;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .run-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .run-btn:not(:disabled):hover { opacity: 0.92; transform: translateY(-1px); }
        .error-banner {
          background: #3b1219;
          border: 1px solid #7f1d1d;
          color: #fca5a5;
          padding: 12px 16px;
          border-radius: 10px;
          font-size: 13px;
          margin-bottom: 20px;
        }
        .results-header {
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          margin-bottom: 16px;
        }
        .results-header h2 { font-size: 20px; margin: 0; font-weight: 700; }
        .empty-state {
          text-align: center;
          padding: 48px 20px;
          color: #64748b;
          font-size: 14px;
          border: 1px dashed #1e293b;
          border-radius: 14px;
        }
        .card {
          background: #111827;
          border: 1px solid #1f293d;
          border-radius: 14px;
          padding: 22px;
          margin-bottom: 20px;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        .card-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 14px;
        }
        .candidate-id { font-size: 17px; font-weight: 700; color: #f8fafc; margin: 0; }
        .combined-score-box { text-align: right; }
        .combined-val { font-size: 24px; font-weight: 800; }
        .combined-tag { font-size: 10px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1px; display: block; }
        
        .scores-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin-bottom: 18px;
          background: #090d16;
          padding: 14px;
          border-radius: 10px;
        }
        .score-label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: #94a3b8;
          margin-bottom: 6px;
          display: flex;
          justify-content: space-between;
        }
        .score-bar-track {
          height: 6px;
          background: #1e293b;
          border-radius: 4px;
          overflow: hidden;
        }
        .score-bar-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.5s ease;
        }

        .llm-section {
          background: #0f172a;
          border: 1px solid #1e293b;
          border-radius: 10px;
          padding: 14px;
          margin-bottom: 16px;
        }
        .llm-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
        }
        .llm-title {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          color: #38bdf8;
          font-weight: 700;
        }
        .depth-badge {
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          padding: 3px 10px;
          border-radius: 999px;
          border: 1px solid transparent;
        }
        .llm-text {
          font-size: 13px;
          line-height: 1.5;
          color: #cbd5e1;
          margin: 4px 0;
        }
        .exp-tag {
          font-size: 12px;
          color: #94a3b8;
          margin-top: 6px;
        }

        .skills-container {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-top: 12px;
        }
        .skill-group-label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: #94a3b8;
          margin-bottom: 6px;
          display: block;
        }
        .chip {
          display: inline-block;
          padding: 3px 10px;
          margin: 3px 4px 3px 0;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 500;
        }
        .chip-matched {
          background: #064e3b;
          border: 1px solid #047857;
          color: #6ee7b7;
        }
        .chip-missing {
          background: #451a03;
          border: 1px solid #b45309;
          color: #fcd34d;
        }
        .none-text {
          font-size: 12px;
          color: #64748b;
          font-style: italic;
        }
      `}</style>

      <div className="shell">
        <div className="header">
          <div className="eyebrow">Production AI Engine</div>
          <h1 className="title">Resume Screening & Matcher</h1>
        </div>

        <div className="panel">
          <span className="label">Target Job Description</span>
          <textarea
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste complete job description requirements here..."
          />

          <div style={{ marginTop: "18px" }}>
            <span className="label">Candidate Resumes (PDF)</span>
            <div className="file-row">
              <input type="file" multiple accept=".pdf" onChange={handleFileChange} />
              {files.length > 0 && (
                <span className="file-count">{files.length} resume{files.length > 1 ? "s" : ""} selected</span>
              )}
            </div>
          </div>

          <button className="run-btn" onClick={handleMatch} disabled={loading}>
            {loading ? "Screening & Scoring Candidates..." : "Run AI Matching Pipeline"}
          </button>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <div className="results-header">
          <h2>Evaluation Leaderboard</h2>
          {results && <span style={{ color: "#94a3b8", fontSize: "13px" }}>{results.length} evaluated</span>}
        </div>

        {!results && !loading && (
          <div className="empty-state">Upload resumes and run the engine to view candidate rankings.</div>
        )}

        {results &&
          results.map((r, idx) => {
            const depthStyle = depthBadgeColor(r.llm_insight?.project_depth);
            return (
              <div className="card" key={r.candidate_id ?? idx}>
                <div className="card-top">
                  <div>
                    <h4 className="candidate-id">#{idx + 1} &nbsp; {r.candidate_id}</h4>
                    <span className="exp-tag">
                      Est. Experience: {r.llm_insight?.experience_years_estimate ? `${r.llm_insight.experience_years_estimate} yrs` : "Fresher / Not specified"}
                    </span>
                  </div>
                  <div className="combined-score-box">
                    <span className="combined-val" style={{ color: scoreColor(r.combined_score) }}>
                      {r.combined_score}%
                    </span>
                    <span className="combined-tag">Overall Fit</span>
                  </div>
                </div>

                <div className="scores-grid">
                  <div>
                    <div className="score-label">
                      <span>SBERT Semantic Match</span>
                      <strong style={{ color: scoreColor(r.sbert_score) }}>{r.sbert_score}%</strong>
                    </div>
                    <div className="score-bar-track">
                      <div
                        className="score-bar-fill"
                        style={{ width: `${r.sbert_score}%`, background: scoreColor(r.sbert_score) }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="score-label">
                      <span>TF-IDF Lexical Match</span>
                      <strong style={{ color: scoreColor(r.tfidf_score) }}>{r.tfidf_score}%</strong>
                    </div>
                    <div className="score-bar-track">
                      <div
                        className="score-bar-fill"
                        style={{ width: `${r.tfidf_score}%`, background: scoreColor(r.tfidf_score) }}
                      />
                    </div>
                  </div>
                </div>

                {r.llm_insight && (
                  <div className="llm-section">
                    <div className="llm-header">
                      <span className="llm-title">LLM Qualitative Analysis (Groq Llama 3.3)</span>
                      <span
                        className="depth-badge"
                        style={{
                          background: depthStyle.bg,
                          color: depthStyle.text,
                          borderColor: depthStyle.border,
                        }}
                      >
                        Project Depth: {r.llm_insight.project_depth || "Medium"}
                      </span>
                    </div>
                    <p className="llm-text">
                      <strong>Alignment:</strong> {r.llm_insight.jd_alignment_summary}
                    </p>
                    <p className="llm-text">
                      <strong>Reasoning:</strong> {r.llm_insight.depth_reasoning}
                    </p>
                  </div>
                )}

                <div className="skills-container">
                  <div>
                    <span className="skill-group-label">Matched Skills ({r.matched_skills?.length || 0})</span>
                    {r.matched_skills && r.matched_skills.length > 0 ? (
                      r.matched_skills.map((s) => (
                        <span className="chip chip-matched" key={s}>✓ {s}</span>
                      ))
                    ) : (
                      <span className="none-text">No direct keyword overlap</span>
                    )}
                  </div>

                  <div>
                    <span className="skill-group-label">Missing Skills ({r.missing_skills?.length || 0})</span>
                    {r.missing_skills && r.missing_skills.length > 0 ? (
                      r.missing_skills.map((s) => (
                        <span className="chip chip-missing" key={s}>✗ {s}</span>
                      ))
                    ) : (
                      <span className="none-text" style={{ color: "#34d399" }}>All required skills matched!</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}