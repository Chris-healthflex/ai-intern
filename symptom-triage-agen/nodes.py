from typing import TypedDict, List
from pydantic import BaseModel

from llm import llm
from tools import web_search


# ---------------- STATE ----------------

class AgentState(TypedDict):
    symptoms: str
    red_flags: List[str]
    sources: List[str]
    need_search: bool
    emergency: bool
    triage: dict



# ---------------- OUTPUT ----------------

class TriageResult(BaseModel):
    urgency_level: str
    red_flags: List[str]
    confidence: float
    disclaimer: str
    sources: List[str]



# ---------------- RED FLAG NODE ----------------

def detect_red_flags(state):

    text = state["symptoms"].lower()

    flags = []

    keywords = {
        "chest pain": "Chest pain",
        "difficulty breathing": "Breathing difficulty",
        "shortness of breath": "Breathing difficulty",
        "can't breathe": "Breathing difficulty",
        "stroke": "Possible stroke",
        "face droop": "Stroke symptom",
        "weak arm": "Stroke symptom",
        "seizure": "Seizure",
        "unconscious": "Loss of consciousness",
        "heavy bleeding": "Severe bleeding",
        "worst headache": "Sudden severe headache",
        "thunderclap": "Sudden severe headache"
    }


    for key,value in keywords.items():

        if key in text:
            flags.append(value)


    return {
        "red_flags": flags,
        "emergency": len(flags) > 0
    }




# ---------------- ROUTER ----------------

def emergency_router(state):

    if state.get("emergency"):

        return "emergency"

    return "normal"




# ---------------- SEARCH DECISION ----------------

def decide_search(state):

    if state.get("emergency"):

        return {
            "need_search": False
        }


    return {
        "need_search": True
    }




# ---------------- SEARCH NODE ----------------

def search_node(state):

    if not state.get("need_search"):

        return {
            "sources":[]
        }


    try:

        result = web_search(
            state["symptoms"]
        )


        return {
            "sources": result
        }


    except:

        return {
            "sources":[]
        }




# ---------------- FINAL TRIAGE ----------------

def final_triage(state):


    structured_llm = llm.with_structured_output(
        TriageResult
    )


    prompt = f"""

You are a medical symptom triage assistant.

Symptoms:
{state.get("symptoms")}


Detected red flags:
{state.get("red_flags")}


Rules:

If red flags exist:
urgency_level = emergency

Otherwise choose:
low
medium
high


Give confidence score between 0 and 1.

Example:
confidence: 0.98


Return:

urgency_level
red_flags
confidence
sources
disclaimer


"""


    result = structured_llm.invoke(prompt)


    data = result.model_dump()



    # guarantee confidence exists

    if data.get("confidence") is None:

        data["confidence"] = 0.85



    if not data.get("sources"):

        data["sources"] = state.get(
            "sources",
            []
        )


    if not data.get("red_flags"):

        data["red_flags"] = state.get(
            "red_flags",
            []
        )


    data["disclaimer"] = (
        "This AI-generated response is not a substitute "
        "for professional medical advice."
    )


    return {
        "triage": data
    }