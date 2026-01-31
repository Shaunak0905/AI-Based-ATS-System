import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"
MAX_CHARS = 3000


PROMPT = """
You are an information extraction system.

Extract structured information from the job description below.
Return ONLY valid JSON. No explanation. No markdown.

Schema:
{{
  "skills": [string],
  "min_experience": number,
  "role": string
}}

Job Description:
{text}
"""



def extract_json(text: str):
    """
    Robust JSON extraction from LLM output.
    Handles missing closing braces.
    """
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object start found")

    json_text = text[start:].strip()

    # If JSON is missing closing brace, fix it
    if not json_text.endswith("}"):
        json_text = json_text + "}"

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print("❌ FIXED JSON ATTEMPT:\n", json_text)
        raise



def extract_jd_info(text: str):
    text = text[:MAX_CHARS]

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": PROMPT.format(text=text),
            "stream": False
        },
        timeout=120
    )

    llm_output = response.json().get("response", "").strip()

    if not llm_output:
        raise ValueError("Empty response from LLM")

    try:
        return extract_json(llm_output)
    except Exception as e:
        print("❌ LLM RAW OUTPUT:\n", llm_output)
        raise RuntimeError("Failed to parse JD JSON") from e
