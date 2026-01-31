import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT = """
You are an ATS system.
Explain in simple recruiter language why this candidate scored {score}%.

Matched skills: {matched}
Missing skills: {missing}
Experience: {exp} years
Job requires: {req} years
"""

def generate_explanation(match_result, resume, jd):
    payload = {
        "model": "llama3",
        "prompt": PROMPT.format(
            score=match_result["final_score"],
            matched=", ".join(match_result["skill_match"]["matched"]),
            missing=", ".join(match_result["skill_match"]["missing"]),
            exp=resume["years_of_experience"],
            req=jd["min_experience"]
        ),
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"]
