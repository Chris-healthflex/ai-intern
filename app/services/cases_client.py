import httpx

from app.config import settings
from app.schemas import CasesResponse, PatientCase


async def fetch_cases(
    offset: int = 0,
    limit: int | None = None,
) -> CasesResponse:
    limit = limit or settings.cases_fetch_limit
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            settings.cases_api_url,
            params={"offset": offset, "limit": limit},
        )
        response.raise_for_status()
        return CasesResponse.model_validate(response.json())


async def fetch_case_by_id(patient_id: str) -> PatientCase | None:
    data = await fetch_cases()
    for case in data.cases:
        if case.patient_id == patient_id:
            return case
    return None
