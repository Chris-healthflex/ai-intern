from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import csv
from datetime import datetime
import json, re

load_dotenv()

app = FastAPI(title="Stance Health Triage API")
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
search = DuckDuckGoSearchRun()

DISCLAIMER = "This is AI-generated triage and NOT a substitute for professional medical advice. In an emergency, call 108 or 112 immediately."
def save_to_csv(data):
    file = "triage_results.csv"

    file_exists = False

    try:
        with open(file, "r"):
            file_exists = True
    except:
        pass

    with open(file, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "patient_id",
                "urgency_level",
                "red_flags",
                "confidence",
                "recommendation",
                "web_search_used",
                "timestamp"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "patient_id": data["patient_id"],
            "urgency_level": data["urgency_level"],
            "red_flags": ", ".join(data["red_flags"]),
            "confidence": data["confidence"],
            "recommendation": data["recommendation"],
            "web_search_used": data["web_search_used"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

class TriageRequest(BaseModel):
    patient_id: str
    message: str


def parse_llm_json(content: str) -> dict:
    content = re.sub(r"```json|```", "", content).strip()
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found in: " + content[:200])


def classify(message: str) -> dict:
    prompt = f"""You are a clinical triage AI. Return ONLY a raw JSON object.
DO NOT use markdown. Start with {{ end with }}.

Patient message: {message}

{{
  "urgency_level": "emergency or see_doctor_soon or self_care",
  "red_flags": ["list any red flags"],
  "confidence": 0.95,
  "recommendation": "what to do",
  "needs_search": false
}}

Rules:
- emergency = life-threatening (chest pain+radiation, stroke, anaphylaxis, not breathing)
- see_doctor_soon = needs doctor within hours/days
- self_care = manageable at home
- needs_search = true only for rare/ambiguous, always false for emergency"""

    response = llm.invoke(prompt)
    print("LLM RAW:", repr(response.content[:300]))  # shows in your terminal
    return parse_llm_json(response.content)


@app.get("/")
def home():
    return {"message": "Triage API Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triage")
def triage(request: TriageRequest):
    try:
        result = classify(request.message)
    except Exception as e:
        print(f"CLASSIFY ERROR: {e}")  # shows in your terminal
        result = {
            "urgency_level": "see_doctor_soon",
            "red_flags": [],
            "confidence": 0.5,
            "recommendation": "Consult a doctor.",
            "needs_search": False
        }

    web_search_used = False
    sources = []

    if result.get("needs_search") and result.get("urgency_level") != "emergency":
        try:
            search_result = search.run(f"medical symptoms triage {request.message[:80]}")
            web_search_used = True
            sources = ["DuckDuckGo Search"]

            update_prompt = f"""Patient: {request.message}
Initial triage: {json.dumps(result)}
Web search context: {search_result[:800]}
Return ONLY raw JSON starting with {{:
{{
  "urgency_level": "...",
  "red_flags": [...],
  "confidence": 0.0,
  "recommendation": "..."
}}"""
            updated = llm.invoke(update_prompt)
            result = parse_llm_json(updated.content)
        except Exception as e:
            print(f"SEARCH ERROR: {e}")

    result["patient_id"] = request.patient_id
    result["web_search_used"] = web_search_used
    result["sources"] = sources
    result["disclaimer"] = DISCLAIMER
    result.pop("needs_search", None)

    try:
        save_to_csv(result)
    except Exception as e:
        print("CSV ERROR:", e)
        return result

    return result