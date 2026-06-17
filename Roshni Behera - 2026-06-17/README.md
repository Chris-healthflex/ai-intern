# Stance Health — AI Symptom Triage API

An AI-powered clinical triage system that analyzes patient symptoms and classifies urgency in real time — built with FastAPI and LangChain.

---

## Problem Statement

Patients often struggle to decide how urgent their symptoms are. Many delay medical help for serious conditions, while others visit hospitals for minor issues — overloading the healthcare system.

The goal of this project is to build an AI-powered triage system that analyzes patient symptoms and classifies them into:

- 🔴 **Emergency** — call 108/112 immediately
- 🟡 **See Doctor Soon** — needs medical attention within hours or days
- 🟢 **Self Care** — manageable at home

The system provides urgency level, detected red flags, confidence score, recommended action, and optional web-searched context — all in one structured API response.

---

## Quick Start

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```

Run:
```bash
uvicorn main:app --reload
```

Test at: `http://127.0.0.1:8000/docs`

---

## API Usage

**POST /triage**

```json
{
  "patient_id": "case_001",
  "message": "Crushing chest pain radiating to my left arm. I am sweating and feeling nauseous."
}
```

**Response:**

```json
{
  "urgency_level": "emergency",
  "red_flags": [
    "crushing chest pain",
    "radiation to left arm",
    "sweating",
    "nausea"
  ],
  "confidence": 0.99,
  "recommendation": "Call emergency services immediately or go to the emergency room",
  "patient_id": "case_001",
  "web_search_used": false,
  "sources": [],
  "disclaimer": "This is AI-generated triage and NOT a substitute for professional medical advice. In an emergency, call 108 or 112 immediately."
}
```

All results are automatically saved to `triage_results.csv` for tracking and audit.

---

## Solution

I built an AI-based medical triage API using FastAPI and Large Language Models.

The user provides:
- Patient ID
- Symptom description

The system:
1. Sends symptoms to an LLM for analysis
2. Classifies urgency level
3. Identifies possible red flags
4. Generates a clear recommendation
5. Provides a confidence score
6. Saves results to CSV for tracking

For ambiguous or unusual symptoms, the system optionally uses DuckDuckGo web search to gather extra clinical context before finalizing the response.

---

## How the System Works

```
User Input
    ↓
FastAPI Endpoint /triage
    ↓
Pydantic validates request
    ↓
LangChain sends symptoms to Groq LLM
    ↓
LLM analyzes:
  - Urgency level
  - Red flags
  - Confidence score
  - Recommendation
  - Needs web search?
    ↓
If symptoms are ambiguous or unusual:
  → DuckDuckGo search adds clinical context
  → LLM updates response with search results
    ↓
Final structured response returned
    ↓
Result saved to triage_results.csv
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | FastAPI + Uvicorn |
| AI / LLM | Groq — Llama 3.3 70B |
| LLM Orchestration | LangChain |
| Web Search | DuckDuckGo Search |
| Validation | Pydantic v2 |
| Result Logging | CSV |
| Config | python-dotenv |

---

## Why LangChain Instead of LangGraph?

I chose **LangChain** because the current problem is a straightforward sequential AI workflow:

```
Patient symptoms → LLM analysis → urgency classification → optional web search → final response
```

LangChain already provides the required LLM integration and tool-calling capabilities for this flow. Using LangGraph at this stage would introduce additional complexity without significant benefit for this prototype.

Since this project was developed within a 60-minute time frame, the focus was on building a reliable end-to-end AI pipeline. The architecture is intentionally kept modular so it can be extended to **LangGraph** in the future for more complex production workflows such as:

- Multi-step reasoning across nodes
- Explicit state management
- Human-in-the-loop doctor approval
- Conditional routing with audit trails
- Advanced healthcare automation pipelines

---

## Why High Accuracy?
 
Three decisions improved accuracy significantly:
 
**1. Temperature = 0**
The LLM is set to `temperature=0` — no randomness. Same symptom always gives the same classification. Critical for medical consistency.
 
**2. Concrete examples in the prompt**
Instead of just listing rules, the prompt shows the LLM exactly what JSON to return with real values. This reduces hallucination and formatting errors.
 
**3. Selective web search**
Web search only fires for ambiguous cases. Emergencies skip it entirely — this keeps the model focused and prevents search results from diluting a clear emergency signal.
 
**4. Robust JSON parsing**
The `parse_llm_json()` function uses regex to extract JSON even if the LLM wraps it in markdown — preventing fallback to the default `0.5 confidence` response.
 
---

## Production Improvements

For a real healthcare production system, I would improve it with:

**RAG (Retrieval Augmented Generation)**
Connect trusted medical documents, clinical guidelines, and drug databases to improve accuracy and reduce hallucinations. The LLM would reason over verified sources instead of relying purely on training data.

**Database**
Replace CSV storage with PostgreSQL or MongoDB for secure patient history management, scalability, and HIPAA-compliant data handling.

**Guardrails and Safety Layer**
Add emergency detection rules, input/output validation, unsafe response prevention, and automatic doctor escalation for critical or low-confidence cases.

**AI Governance**
Maintain full audit logs of every triage decision, monitor model performance over time, ensure explainability for clinical review, and enforce patient data privacy.

**Better Confidence Scoring**
Improve confidence calculation using rule-based checks combined with model evaluation — not just LLM-generated scores, which can be overconfident on ambiguous cases.

**Switch to LangGraph**
Build a proper StateGraph with explicit nodes (classify → route → search → synthesize → respond) and conditional edges. This makes routing logic visible, testable, and auditable — critical for regulated healthcare environments.

**Monitoring and Observability**
Track model accuracy, failure rates, latency, and clinician feedback using tools like **LangSmith** or **MLflow**. Set up alerts for unusual patterns or confidence degradation.

**Batch Processing**
Add a `POST /triage/batch` endpoint that accepts all 100 patient cases at once, processes them asynchronously using `asyncio.gather()`, and returns a downloadable CSV — 10x faster than sequential calls.

**Frontend Dashboard**
Add patient and clinician interfaces for symptom submission, real-time case monitoring, and triage history review.


---

## Project Structure

```
stance_triage/
├── main.py              # FastAPI app + LangChain triage agent
├── requirements.txt     # All dependencies
├── .env                 # API keys (not committed to GitHub)
├── .gitignore           # Excludes .env and generated files
├── triage_results.csv   # Auto-generated on first run
└── README.md
```

---

## Author

**Roshni Behera**

- GitHub: [github.com/roshnib1](https://github.com/roshnib1)
- LinkedIn: [linkedin.com/in/roshnibehera](https://www.linkedin.com/in/roshnibehera)

---
