from langgraph.graph import StateGraph, END

from .agents import (
    rfp_analyzer_agent,
    knowledge_retriever_agent,
    response_drafter_agent,
    quality_reviewer_agent,
)
from .config import (
    MAX_COST_PER_RFP,
    MAX_REVISION_CYCLES,
    MIN_QUALITY_SCORE,
)
from .guards import input_guard, output_guard
from .state import RFPPipelineState

def should_revise(state: RFPPipelineState) -> str:
    revision_count = state.get("revision_count", 0)
    cumulative_cost = state.get("cumulative_cost", 0)

    if revision_count >= MAX_REVISION_CYCLES:
        return "output_guard"

    if cumulative_cost >= MAX_COST_PER_RFP:
        return "output_guard"

    for scores in state.get("quality_scores", {}).values():
        if any(score < MIN_QUALITY_SCORE for score in scores.values()):
            return "increment_revision"

    return "output_guard"

def increment_revision(state: RFPPipelineState) -> dict:
    return {
        "revision_count": state.get("revision_count", 0) + 1,
    }

def build_rfp_pipeline():
    workflow = StateGraph(RFPPipelineState)

    workflow.add_node("input_guard", input_guard)
    workflow.add_node("rfp_analyzer", rfp_analyzer_agent)
    workflow.add_node("knowledge_retriever", knowledge_retriever_agent)
    workflow.add_node("response_drafter", response_drafter_agent)
    workflow.add_node("quality_reviewer", quality_reviewer_agent)
    workflow.add_node("increment_revision", increment_revision)
    workflow.add_node("output_guard", output_guard)

    workflow.set_entry_point("input_guard")
    workflow.add_edge("input_guard", "rfp_analyzer")
    workflow.add_edge("rfp_analyzer", "knowledge_retriever")
    workflow.add_edge("knowledge_retriever", "response_drafter")
    workflow.add_edge("response_drafter", "quality_reviewer")

    workflow.add_conditional_edges(
        "quality_reviewer",
        should_revise,
        {
            "increment_revision": "increment_revision",
            "output_guard": "output_guard",
        },
    )

    workflow.add_edge("increment_revision", "response_drafter")
    workflow.add_edge("output_guard", END)

    return workflow.compile()
