from fastapi import FastAPI
from pydantic import BaseModel

from graph import app

from fastapi.middleware.cors import CORSMiddleware


api = FastAPI()


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SymptomRequest(BaseModel):
    message: str



@api.get("/")
def home():
    return {
        "message": "Symptom Triage Agent API running"
    }



@api.post("/triage")
def triage(request: SymptomRequest):

    output = app.invoke(
        {
            "symptoms": request.message,
            "red_flags": [],
            "sources": [],
            "need_search": False,
            "emergency": False
        }
    )


    print("FINAL OUTPUT:")
    print(output)


    if "triage" in output:
        result = output["triage"]
    else:
        result = output


    return {

        "urgency_level": result.get("urgency_level"),

        "red_flags": result.get("red_flags"),

        "confidence": result.get("confidence"),

        "disclaimer": result.get(
            "disclaimer",
            "This AI-generated response is not a substitute for professional medical advice."
        ),

        "sources": result.get("sources")

    }