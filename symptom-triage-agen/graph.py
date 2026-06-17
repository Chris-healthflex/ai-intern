from typing import TypedDict, List

from langgraph.graph import StateGraph, END

from nodes import (
    detect_red_flags,
    emergency_router,
    decide_search,
    search_node,
    final_triage
)



class AgentState(TypedDict):

    symptoms: str
    red_flags: List[str]
    sources: List[str]
    need_search: bool
    emergency: bool
    triage: dict



workflow = StateGraph(AgentState)



workflow.add_node(
    "red_flags",
    detect_red_flags
)


workflow.add_node(
    "router",
    lambda state:{
        "emergency": state.get("emergency",False)
    }
)


workflow.add_node(
    "search_decision",
    decide_search
)


workflow.add_node(
    "search",
    search_node
)


workflow.add_node(
    "triage",
    final_triage
)




workflow.set_entry_point(
    "red_flags"
)



workflow.add_edge(
    "red_flags",
    "router"
)



def route(state):

    if state.get("emergency"):

        return "triage"

    return "search_decision"




workflow.add_conditional_edges(
    "router",
    route,
    {
        "triage":"triage",
        "search_decision":"search_decision"
    }
)



workflow.add_edge(
    "search_decision",
    "search"
)



workflow.add_edge(
    "search",
    "triage"
)



workflow.add_edge(
    "triage",
    END
)



app = workflow.compile()