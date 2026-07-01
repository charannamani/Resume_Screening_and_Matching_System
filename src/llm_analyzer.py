import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"  # strong, fast, free-tier friendly

ANALYSIS_PROMPT_TEMPLATE = """You are an expert technical recruiter assistant.
Read the JOB DESCRIPTION and the CANDIDATE RESUME below, then analyze the candidate
strictly based on what is written. Do not invent details that aren't present.

JOB DESCRIPTION:
{jd_text}

CANDIDATE RESUME:
{resume_text}

Return ONLY a valid JSON object (no markdown, no backticks, no extra text) with
exactly these keys:

{{
  "experience_years_estimate": <number, your best estimate of relevant years of experience, 0 if unclear>,
  "project_depth": "<one of: low, medium, high>",
  "depth_reasoning": "<one short sentence explaining the project_depth rating>",
  "jd_alignment_summary": "<one short sentence on how well the candidate's actual project/work experience matches the JD's core requirements>"
}}
"""


def analyze_resume_against_jd(resume_text, jd_text):
    """
    Sends the resume + JD to the LLM and returns structured reasoning
    about experience depth and JD alignment.

    Returns a dict. On any failure, returns a safe fallback dict instead
    of crashing the whole pipeline - a flaky third-party API call should
    never take down the rest of the ranking.
    """
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(jd_text=jd_text, resume_text=resume_text)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        raw_text = response.choices[0].message.content.strip()
        parsed = json.loads(raw_text)
        return parsed

    except Exception as e:
        print(f"[llm_analyzer] LLM call failed, using fallback: {repr(e)}")
        return {
            "experience_years_estimate": None,
            "project_depth": "unknown",
            "depth_reasoning": "LLM analysis unavailable for this candidate.",
            "jd_alignment_summary": "LLM analysis unavailable for this candidate.",
        }


if __name__ == "__main__":
    sample_jd = (
        "Looking for a software engineer skilled in javascript, react js, "
        "and node js for backend api development. Must know sql."
    )
    sample_resume = (
        "Full stack web development using mern stack. Built application "
        "backend using express. Knows java and c."
    )

    print("\n--- Running LLM analysis (Groq) ---")
    result = analyze_resume_against_jd(sample_resume, sample_jd)
    print(json.dumps(result, indent=4))