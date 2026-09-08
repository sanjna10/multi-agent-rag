from typing import TypedDict

class RFPPipelineState(TypedDict):
    rfp_text: str
    sanitized_rfp: str
    requirements: list[dict]
    sections_needed: list[str]
    complexity_score: int
    retrieved_knowledge: dict
    draft_sections: dict
    revision_feedback: dict
    quality_scores: dict
    revision_count: int
    metadata: dict
    errors: list[str]
    trace_id: str
    cumulative_cost: float
