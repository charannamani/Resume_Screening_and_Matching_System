import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
MODEL_NAME = "qwen/qwen3.6-27b"

ANALYSIS_PROMPT = """You are an expert technical recruiter.
Analyze the CANDIDATE RESUME against the JOB DESCRIPTION strictly based on what is written.

JOB DESCRIPTION:
{jd_text}

CANDIDATE RESUME:
{resume_text}

Provide your analysis strictly in valid JSON format with these exact keys:
{{
  "experience_years_estimate": <number, estimated relevant years, 0 if fresher>,
  "project_depth": "<one of: low, medium, high>",
  "depth_reasoning": "<1 short sentence explaining candidate project depth>",
  "jd_alignment_summary": "<1 short sentence summarizing match to JD>",
  "key_strengths": ["<strength 1>", "<strength 2>"]
}}
"""

def extract_json_from_response(text: str) -> dict:
    """Cleanly extracts JSON object even with thinking tags or trailing commentary."""
    if not text:
        raise ValueError("Empty response text")
    
    # 1. Remove reasoning / think tags if present
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # 2. Remove markdown code fences
    cleaned = re.sub(r'```(?:json)?', '', cleaned)
    cleaned = cleaned.strip()

    # 3. Find the first '{' and parse only the valid JSON payload
    start_idx = cleaned.find('{')
    if start_idx == -1:
        raise ValueError("No JSON bracket '{' found in response")

    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(cleaned[start_idx:])
    return obj

def analyze_resume_against_jd(resume_text: str, jd_text: str) -> dict:
    """
    Calls Groq API to analyze candidate depth and alignment.
    """
    fallback_result = {
        "experience_years_estimate": 0,
        "project_depth": "medium",
        "depth_reasoning": "Standard evaluation applied (LLM qualitative metrics unavailable).",
        "jd_alignment_summary": "Candidate profile processed via semantic and lexical algorithms.",
        "key_strengths": []
    }

    if not client or not GROQ_API_KEY:
        print("[llm_analyzer] Warning: GROQ_API_KEY is not set.")
        return fallback_result

    prompt = ANALYSIS_PROMPT.format(
        jd_text=jd_text[:3000],
        resume_text=resume_text[:4000]
    )

    try:
        print(f"[llm_analyzer] Sending prompt to Groq ({MODEL_NAME})...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a recruiter that outputs valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        raw_content = response.choices[0].message.content.strip()
        parsed = extract_json_from_response(raw_content)

        # Validate project_depth value
        depth = str(parsed.get("project_depth", "medium")).lower()
        if depth not in ["low", "medium", "high"]:
            parsed["project_depth"] = "medium"

        print("[llm_analyzer] Successfully parsed live LLM reasoning from Groq!")
        return parsed

    except Exception as e:
        print(f"[llm_analyzer] ERROR during Groq execution: {repr(e)}")
        return fallback_result


if __name__ == "__main__":
    test_jd = "Looking for a software engineer skilled in React and Node.js."
    test_resume = "Full stack developer with 1 year experience building React and Express apps."
    print("Testing live Groq connection...")
    res = analyze_resume_against_jd(test_resume, test_jd)
    print(json.dumps(res, indent=2))