# Stance Health Triage Backend

AI-powered patient triage API that fetches cases from the Stance health dataset, extracts red flags, classifies urgency, and uses web search for ambiguous cases.

**Model:** Groq `llama-3.1-8b-instant` via LangChain/LangGraph  
**Framework:** FastAPI

## Features

- Fetches patient cases from `https://ai-stance.vercel.app/api/cases`
- Classifies urgency: `self_care`, `see_a_doctor_as_soon_as_possible`, or `emergency`
- Extracts clinical red flags from patient messages
- Confidence scoring (0.0–1.0) with automatic escalation to emergency when confidence is low
- Web search fallback (Tavily if API key set, otherwise DuckDuckGo) for ambiguous cases
- Conservative safety rule: when in doubt, classify as emergency
- All responses include an AI disclaimer

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # then set GROQ_API_KEY
```

Required environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for llama-3.1-8b-instant |
| `TAVILY_API_KEY` | No | Tavily search (falls back to DuckDuckGo) |
| `CASES_API_URL` | No | Defaults to Stance cases API |

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/cases` | Fetch raw cases from upstream API |
| POST | `/triage` | Triage a single case (JSON body) |
| GET | `/triage/{patient_id}` | Fetch and triage a case by ID |
| POST | `/triage/batch` | Triage multiple cases (`offset`, `limit` query params) |

## Example

```bash
curl http://localhost:8000/triage/case_001
```

Response includes `urgency_level`, `red_flags`, `reasoning`, `confidence`, `used_web_search`, and `disclaimer`.

## Disclaimer

This system uses AI for informational triage only. It does not replace professional medical advice. In emergencies, call your local emergency number.
