import { useState } from "react";
import axios from "axios";

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
      setError("Add a job description and at least one resume PDF before running the engine.");
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

      const sorted = [...(response.data.results || [])].sort(
        (a, b) => b.combined_score - a.combined_score
      );
      setResults(sorted);
    } catch (err) {
      console.error(err);
      setResults(null);
      setError("Couldn't reach the matching engine. Confirm the backend is running on port 5000.");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (score >= 75) return "#3ddc84";
    if (score >= 50) return "#ffc857";
    return "#ff6b6b";
  };

  return (
    <div className="app">
      <style>{`
        * { box-sizing: border-box; }
        body { margin: 0; }
        .app {
          min-height: 100vh;
          background: radial-gradient(circle at top, #12161c 0%, #0a0c10 60%);
          color: #e6e9ef;
          font-family: 'Segoe UI', system-ui, sans-serif;
          padding: 40px 20px 80px;
        }
        .shell { max-width: 880px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 36px; }
        .eyebrow {
          font-size: 12px;
          letter-spacing: 3px;
          text-transform: uppercase;
          color: #57c7ff;
          font-weight: 600;
        }
        .title {
          font-size: 32px;
          font-weight: 700;
          margin: 6px 0 0;
          letter-spacing: 0.5px;
        }
        .panel {
          background: #12161d;
          border: 1px solid #232935;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 24px;
        }
        .label {
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          color: #8b93a3;
          margin-bottom: 10px;
          display: block;
        }
        textarea {
          width: 100%;
          min-height: 120px;
          background: #0d1015;
          border: 1px solid #2a3140;
          border-radius: 8px;
          padding: 14px;
          color: #e6e9ef;
          font-size: 14px;
          resize: vertical;
        }
        textarea:focus, input:focus { outline: 2px solid #57c7ff; outline-offset: 2px; }
        .file-row {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-top: 6px;
        }
        input[type="file"] {
          color: #8b93a3;
          font-size: 13px;
        }
        .file-count {
          font-size: 12px;
          color: #57c7ff;
        }
        .run-btn {
          width: 100%;
          margin-top: 20px;
          padding: 14px;
          border-radius: 8px;
          border: none;
          background: linear-gradient(135deg, #57c7ff, #3d8bff);
          color: #05070a;
          font-weight: 700;
          font-size: 14px;
          letter-spacing: 0.5px;
          cursor: pointer;
          transition: opacity 0.15s ease;
        }
        .run-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .run-btn:not(:disabled):hover { opacity: 0.9; }
        .error-banner {
          background: #2a1418;
          border: 1px solid #5c2530;
          color: #ff9aa6;
          padding: 12px 16px;
          border-radius: 8px;
          font-size: 13px;
          margin-bottom: 20px;
        }
        .results-header {
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          margin-bottom: 16px;
        }
        .results-header h2 { font-size: 18px; margin: 0; }
        .results-count { font-size: 12px; color: #8b93a3; }
        .empty-state {
          text-align: center;
          padding: 40px 20px;
          color: #56606f;
          font-size: 13px;
          border: 1px dashed #232935;
          border-radius: 12px;
        }
        .card {
          background: #12161d;
          border: 1px solid #232935;
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 16px;
        }
        .card-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 14px;
        }
        .candidate-id { font-size: 15px; font-weight: 700; margin: 0; }
        .combined-badge {
          font-size: 20px;
          font-weight: 800;
          color: #05070a;
          background: none;
        }
        .scores {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 16px;
        }
        .score-block { }
        .score-label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: #8b93a3;
          margin-bottom: 6px;
        }
        .score-bar-track {
          height: 6px;
          background: #1c212b;
          border-radius: 4px;
          overflow: hidden;
        }
        .score-bar-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.4s ease;
        }
        .score-value {
          font-size: 13px;
          font-weight: 600;
          margin-top: 4px;
        }
        .gap-section { border-top: 1px solid #1c212b; padding-top: 14px; }
        .gap-label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: #8b93a3;
          margin-bottom: 8px;
          display: block;
        }
        .perfect-match {
          color: #3ddc84;
          font-size: 13px;
          font-weight: 600;
        }
        .skill-chip {
          display: inline-block;
          background: #2a2013;
          border: 1px solid #5c4720;
          color: #ffc857;
          padding: 4px 12px;
          margin: 3px 6px 3px 0;
          border-radius: 999px;
          font-size: 12px;
        }
      `}</style>

      <div className="shell">
        <div className="header">
          <div className="eyebrow">Resume &rarr; JD Matching Engine</div>
          <h1 className="title">Console</h1>
        </div>

        <div className="panel">
          <span className="label">Job Description</span>
          <textarea
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste the job description here..."
          />

          <div style={{ marginTop: "18px" }}>
            <span className="label">Resumes (PDF)</span>
            <div className="file-row">
              <input type="file" multiple accept=".pdf" onChange={handleFileChange} />
              {files.length > 0 && (
                <span className="file-count">{files.length} file{files.length > 1 ? "s" : ""} selected</span>
              )}
            </div>
          </div>

          <button className="run-btn" onClick={handleMatch} disabled={loading}>
            {loading ? "Analyzing..." : "Run ML Engine"}
          </button>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <div className="results-header">
          <h2>Results</h2>
          {results && <span className="results-count">{results.length} candidate{results.length !== 1 ? "s" : ""}</span>}
        </div>

        {!results && !loading && (
          <div className="empty-state">Run the engine to see candidate scores  here.</div>
        )}

        {results &&
          results.map((r, idx) => (
            <div className="card" key={r.candidate_id ?? idx}>
              <div className="card-top">
                <h4 className="candidate-id">{r.candidate_id}</h4>
                <span className="combined-badge" style={{ color: scoreColor(r.combined_score) }}>
                  {r.combined_score}%
                </span>
              </div>

              <div className="scores">
                <div className="score-block">
                  <div className="score-label">SBERT (Semantic)</div>
                  <div className="score-bar-track">
                    <div
                      className="score-bar-fill"
                      style={{ width: `${r.sbert_score}%`, background: scoreColor(r.sbert_score) }}
                    />
                  </div>
                  <div className="score-value">{r.sbert_score}%</div>
                </div>

                <div className="score-block">
                  <div className="score-label">TF-IDF (Lexical)</div>
                  <div className="score-bar-track">
                    <div
                      className="score-bar-fill"
                      style={{ width: `${r.tfidf_score}%`, background: scoreColor(r.tfidf_score) }}
                    />
                  </div>
                  <div className="score-value">{r.tfidf_score}%</div>
                </div>
              </div>

              <div className="gap-section">
                <span className="gap-label">Skill Gap</span>
                {(!r.missing_skills || r.missing_skills.length === 0) ? (
                  <span className="perfect-match">Perfect match — no missing skills ✅</span>
                ) : (
                  <div>
                    {r.missing_skills.map((skill) => (
                      <span className="skill-chip" key={skill}>{skill}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}