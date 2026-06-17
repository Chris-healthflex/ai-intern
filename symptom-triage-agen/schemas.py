from pydantic import BaseModel
from typing import List



class TriageResult(BaseModel):

    urgency_level: str

    red_flags: List[str]

    confidence: float

    reasoning: str

    disclaimer: str

    sources: List[str]