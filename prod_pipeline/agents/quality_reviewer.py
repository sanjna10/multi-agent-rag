import json
import re

from ..clients import langfuse
from ..config import (
    CLAUDE_MODEL,
    MAX_COST_PER_RFP,
    MIN_QUALITY_SCORE,
)
from ..llm import call_claude
from ..state import RFPPipelineState

def _parse_review(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    return {
        "relevance": 6,
        "completeness": 6,
        "accuracy": 6,
        "feedback": "Unable to parse reviewer output.",
    }

def quality_reviewer_agent(state: RFPPipelineState) -> dict:
    """
    Agent 4: score relevance, completeness and accuracy, then provide feedback.
    """

    trace = langfuse.trace(id=state["trace_id"])
    generation = trace.generation(
        name="quality-reviewer",
        model=CLAUDE_MODEL,
    )

    quality_scores = {}
    revision_feedback = {}
    reviewer_metadata = {"sections": {}}
    total_cost = 0.0

    for section, draft in state.get("draft_sections", {}).items():
        if "[COST LIMIT REACHED" in draft:
            quality_scores[section] = {
                "relevance": 0,
                "completeness": 0,
                "accuracy": 0,
            }
            revision_feedback[section] = (
                "Section was not generated due to cost limits."
            )
            continue

        current_cost = state.get("cumulative_cost", 0) + total_cost
        if current_cost >= MAX_COST_PER_RFP:
            quality_scores[section] = {
                "relevance": 5,
                "completeness": 5,
                "accuracy": 5,
            }
            continue

        section_span = trace.span(name=f"review-{section}")

        section_reqs = [
            requirement
            for requirement in state.get("requirements", [])
            if requirement.get("response_section", "").lower() == section.lower()
        ]

        reqs_text = "\n".join(
            f"- [{requirement.get('priority', 'MEDIUM')}] {requirement['description']}"
            for requirement in section_reqs
        )

        section_docs = state.get("retrieved_knowledge", {}).get(section, [])
        evidence_text = "\n".join(
            f"[{doc['source']}]: {doc['text'][:200]}..."
            for doc in section_docs[:5]
        )

        system_prompt = """You are a senior quality reviewer for RFP responses.

Score each dimension from 0-10:
- relevance
- completeness
- accuracy

If any score is below 7, give specific actionable feedback describing:
1. what is wrong,
2. what needs to improve,
3. what evidence should be used.

Return valid JSON only:
{"relevance": N, "completeness": N, "accuracy": N, "feedback": "..."}
"""

        user_prompt = f"""Review this "{section}" section.

REQUIREMENTS:
{reqs_text if reqs_text else "No specific requirements extracted."}

AVAILABLE EVIDENCE:
{evidence_text if evidence_text else "No specific evidence available."}

DRAFT:
{draft}
"""

        response = call_claude(system_prompt, user_prompt, max_tokens=600)
        total_cost += response["cost"]
        review = _parse_review(response["content"])

        scores = {
            "relevance": review.get("relevance", 5),
            "completeness": review.get("completeness", 5),
            "accuracy": review.get("accuracy", 5),
        }
        quality_scores[section] = scores

        feedback = review.get("feedback", "")
        if feedback:
            revision_feedback[section] = feedback

        reviewer_metadata["sections"][section] = {
            "scores": scores,
            "needs_revision": any(
                score < MIN_QUALITY_SCORE for score in scores.values()
            ),
            "cost": response["cost"],
            "latency": response["latency"],
        }

        section_span.end(
            output={"scores": scores, "has_feedback": bool(feedback)}
        )

    generation.end(
        output={
            "sections_reviewed": len(quality_scores),
            "sections_needing_revision": sum(
                1
                for scores in quality_scores.values()
                if any(score < MIN_QUALITY_SCORE for score in scores.values())
            ),
        }
    )

    return {
        "quality_scores": quality_scores,
        "revision_feedback": revision_feedback,
        "cumulative_cost": state.get("cumulative_cost", 0) + total_cost,
        "metadata": {
            **state.get("metadata", {}),
            f"reviewer_cycle_{state.get('revision_count', 0)}": reviewer_metadata,
        },
    }
