import asyncio
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from app.exceptions import triage_error_detail
from app.graph.triage_graph import triage_case
from app.schemas import (
    AI_DISCLAIMER,
    BatchTriageResponse,
    PatientCase,
    TriageAssessment,
)
from app.services.cases_client import fetch_case_by_id, fetch_cases

app = FastAPI(
    title="Stance Health Triage API",
    description=(
        "AI-powered patient triage backend using LangGraph and Groq llama-3.1-8b-instant. "
        "Classifies urgency, extracts red flags, and uses web search for ambiguous cases."
    ),
    version="1.0.0",
)


async def _run_triage(case: PatientCase) -> TriageAssessment:
    try:
        return await asyncio.to_thread(triage_case, case)
    except Exception as exc:
        status_code, detail = triage_error_detail(exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc


@app.get("/health")
async def health():
    return {"status": "ok", "disclaimer": AI_DISCLAIMER}


@app.get("/cases")
async def list_cases(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return await fetch_cases(offset=offset, limit=limit)


@app.post("/triage", response_model=TriageAssessment)
async def triage_patient_case(case: PatientCase):
    return await _run_triage(case)


@app.get("/triage/{patient_id}", response_model=TriageAssessment)
async def triage_by_patient_id(patient_id: str):
    case = await fetch_case_by_id(patient_id)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Patient case '{patient_id}' not found")
    return await _run_triage(case)


@app.get("/triage/batch", response_model=BatchTriageResponse)
async def triage_batch(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    data = await fetch_cases(offset=offset, limit=limit)
    assessments = await asyncio.gather(*[_run_triage(case) for case in data.cases])
    return BatchTriageResponse(
        total_processed=len(assessments),
        assessments=list(assessments),
        disclaimer=AI_DISCLAIMER,
    )
