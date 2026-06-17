from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from app.config import settings
from app.prompts import INITIAL_TRIAGE_PROMPT, REFINED_TRIAGE_PROMPT
from app.schemas import (
    AI_DISCLAIMER,
    InitialTriageResult,
    PatientCase,
    TriageAssessment,
    UrgencyLevel,
)
from app.services.llm import get_llm
from app.services.search import search_medical_context


class TriageState(TypedDict):
    patient_id: str
    message: str
    initial_result: InitialTriageResult | None
    search_context: str | None
    used_web_search: bool
    final_assessment: TriageAssessment | None


def _escalate_if_low_confidence(urgency: UrgencyLevel, confidence: float) -> UrgencyLevel:
    if confidence < settings.confidence_threshold and urgency != UrgencyLevel.EMERGENCY:
        return UrgencyLevel.EMERGENCY
    return urgency


def _run_initial_triage(state: TriageState) -> dict:
    llm = get_llm().with_structured_output(InitialTriageResult)
    result: InitialTriageResult = llm.invoke(
        [HumanMessage(content=INITIAL_TRIAGE_PROMPT.format(message=state["message"]))]
    )
    return {"initial_result": result}


def _should_search(state: TriageState) -> Literal["search", "finalize"]:
    result = state["initial_result"]
    if result is None:
        return "finalize"

    needs_search = (
        result.is_ambiguous
        or result.confidence < settings.confidence_threshold
        or (
            result.urgency_level == UrgencyLevel.EMERGENCY
            and result.confidence < 0.85
        )
    )
    return "search" if needs_search else "finalize"


def _run_web_search(state: TriageState) -> dict:
    result = state["initial_result"]
    if result is None:
        return {"search_context": None, "used_web_search": False}

    query = result.search_query or state["message"][:200]
    context = search_medical_context(query)
    return {"search_context": context, "used_web_search": True}


def _finalize_without_search(state: TriageState) -> dict:
    result = state["initial_result"]
    if result is None:
        raise ValueError("Initial triage result missing")

    urgency = _escalate_if_low_confidence(result.urgency_level, result.confidence)
    assessment = TriageAssessment(
        patient_id=state["patient_id"],
        message=state["message"],
        urgency_level=urgency,
        red_flags=result.red_flags,
        reasoning=result.reasoning,
        confidence=result.confidence,
        used_web_search=False,
        search_context=None,
        disclaimer=AI_DISCLAIMER,
    )
    return {"final_assessment": assessment}


def _finalize_with_search(state: TriageState) -> dict:
    result = state["initial_result"]
    if result is None:
        raise ValueError("Initial triage result missing")

    llm = get_llm().with_structured_output(InitialTriageResult)
    refined: InitialTriageResult = llm.invoke(
        [
            HumanMessage(
                content=REFINED_TRIAGE_PROMPT.format(
                    message=state["message"],
                    initial_urgency=result.urgency_level.value,
                    initial_red_flags=", ".join(result.red_flags) or "none",
                    initial_reasoning=result.reasoning,
                    initial_confidence=result.confidence,
                    search_context=state.get("search_context") or "No context available",
                )
            )
        ]
    )

    urgency = _escalate_if_low_confidence(refined.urgency_level, refined.confidence)
    reasoning = (
        f"{refined.reasoning} "
        f"(Refined using web search. Initial confidence: {result.confidence:.2f}, "
        f"refined confidence: {refined.confidence:.2f})"
    )

    assessment = TriageAssessment(
        patient_id=state["patient_id"],
        message=state["message"],
        urgency_level=urgency,
        red_flags=refined.red_flags,
        reasoning=reasoning,
        confidence=refined.confidence,
        used_web_search=state.get("used_web_search", False),
        search_context=state.get("search_context"),
        disclaimer=AI_DISCLAIMER,
    )
    return {"final_assessment": assessment}


def build_triage_graph():
    graph = StateGraph(TriageState)

    graph.add_node("initial_triage", _run_initial_triage)
    graph.add_node("web_search", _run_web_search)
    graph.add_node("finalize_direct", _finalize_without_search)
    graph.add_node("finalize_refined", _finalize_with_search)

    graph.set_entry_point("initial_triage")
    graph.add_conditional_edges(
        "initial_triage",
        _should_search,
        {"search": "web_search", "finalize": "finalize_direct"},
    )
    graph.add_edge("web_search", "finalize_refined")
    graph.add_edge("finalize_direct", END)
    graph.add_edge("finalize_refined", END)

    return graph.compile()


triage_graph = build_triage_graph()


def triage_case(case: PatientCase) -> TriageAssessment:
    result = triage_graph.invoke(
        {
            "patient_id": case.patient_id,
            "message": case.message,
            "initial_result": None,
            "search_context": None,
            "used_web_search": False,
            "final_assessment": None,
        }
    )
    assessment = result.get("final_assessment")
    if assessment is None:
        raise RuntimeError(f"Triage failed for patient {case.patient_id}")
    return assessment
