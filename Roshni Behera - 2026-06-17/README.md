# Stance Health AI Triage API

## Problem Statement

Patients often have difficulty deciding how urgent their symptoms are.
Many people delay medical help for serious symptoms, while others visit hospitals for minor issues.

The goal of this project is to build an AI-powered triage system that analyzes patient symptoms and classifies them into:

- Emergency
- See Doctor Soon
- Self Care

The system provides urgency level, detected red flags, confidence score, and recommended action.

---

# Solution

I built an AI-based medical triage API using FastAPI and Large Language Models.

The user provides:

- Patient ID
- Symptoms description

The system:

1. Sends symptoms to an LLM for analysis.
2. Classifies urgency level.
3. Identifies possible red flags.
4. Generates recommendation.
5. Provides confidence score.
6. Saves results into CSV for tracking.

For ambiguous symptoms, the system optionally uses web search context before finalizing the response.

---

# Tech Stack

## Backend
- FastAPI
- Python

## AI / LLM
- Groq Llama 3.3 70B model
- LangChain

## Tools
- DuckDuckGo Search
- Pydantic
- CSV logging

---
## Why LangChain instead of LangGraph?

I chose LangChain because the current problem was a straightforward sequential AI workflow.

The flow of the application is:

Patient symptoms → LLM analysis → urgency classification → optional web search for ambiguous cases → final response

LangChain already provides the required LLM integration and tool-calling capabilities needed for this workflow. Using LangGraph at this stage would introduce additional complexity without providing significant benefits for this prototype.

Since this project was developed within a limited time frame, the focus was on building a reliable end-to-end AI pipeline using LangChain. The architecture was kept modular so it can be extended to LangGraph in the future for more complex production workflows such as multi-step reasoning, state management, human-in-the-loop approval, doctor escalation, and advanced healthcare automation.

---

# How the System Works

User Input

↓

FastAPI Endpoint `/triage`

↓

Pydantic validates request

↓

LangChain sends symptom description to LLM

↓

LLM analyzes:

- Urgency level
- Red flags
- Confidence
- Recommendation

↓

If symptoms are unusual/ambiguous:

↓

DuckDuckGo search provides extra context

↓

Final response generated

↓

Result stored in CSV

---

# Example Input

```json
{
 "patient_id":"case_001",
 "message":"Crushing chest pain radiating to left arm with sweating"
}
```

# Production Improvements

For a real healthcare production system, I would improve it with:

- **RAG:** Connect trusted medical documents and clinical guidelines to improve accuracy and reduce hallucinations.

- **Database:** Replace CSV storage with PostgreSQL/MongoDB for secure patient history management and scalability.

- **Guardrails & Safety Layer:** Add emergency detection rules, input/output validation, unsafe response prevention, and doctor escalation for critical cases.

- **AI Governance:** Maintain audit logs, monitor model performance, ensure explainability, and protect patient privacy.

- **Better Confidence Scoring:** Improve confidence calculation using model evaluation and rule-based checks instead of relying only on LLM-generated scores.

- **Monitoring:** Track model accuracy, failures, latency, and feedback using tools like MLflow or LangSmith.

- **Frontend Dashboard:** Add patient and doctor interfaces for symptom submission, case monitoring, and real-world usage.
- **Better Confidence Scoring:** Improve confidence calculation using model evaluation and rule-based checks instead of relying only on LLM-generated scores.

- **Monitoring:** Track model accuracy, failures, latency, and feedback using tools like MLflow or LangSmith.

- **Frontend Dashboard:** Add patient and doctor interfaces for symptom submission, case monitoring, and real-world usage.
  
# Author

**Roshni Behera**

GitHub:

https://github.com/roshnib1

Linkedin: https://www.linkedin.com/in/roshnibehera
