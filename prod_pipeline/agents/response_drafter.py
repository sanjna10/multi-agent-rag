from ..clients import langfuse
from ..config import (
    CLAUDE_MODEL,
    MAX_COST_PER_RFP,
    MIN_QUALITY_SCORE,
)
from ..llm import call_claude
from ..state import RFPPipelineState

def _sections_to_draft(state: RFPPipelineState) -> list[str]:
    if state.get("revision_count", 0) > 0 and state.get("quality_scores"):
        return [
            section
            for section, scores in state["quality_scores"].items()
            if any(score < MIN_QUALITY_SCORE for score in scores.values())
        ]

    return state["sections_needed"]

def response_drafter_agent(state: RFPPipelineState) -> dict:
    """Agent 3: generate or revise proposal sections from retrieved evidence."""

    trace = langfuse.trace(id=state["trace_id"])
    generation = trace.generation(
        name="response-drafter",
        model=CLAUDE_MODEL,
    )

    draft_sections = dict(state.get("draft_sections", {}))
    drafter_metadata = {"sections": {}}
    total_cost = 0.0
    sections_to_draft = _sections_to_draft(state)

    for section in sections_to_draft:
        current_cost = state.get("cumulative_cost", 0) + total_cost
        if current_cost >= MAX_COST_PER_RFP:
            draft_sections[section] = (
                f"[COST LIMIT REACHED: ${current_cost:.2f} / "
                f"${MAX_COST_PER_RFP:.2f}. This section was not generated.]"
            )
            continue

        section_span = trace.span(name=f"draft-{section}")

        section_docs = state.get("retrieved_knowledge", {}).get(section, [])
        context_text = "\n\n---\n\n".join(
            f"[Source: {doc['source']}] (relevance: {doc['score']:.3f})\n{doc['text']}"
            for doc in section_docs
        )

        section_reqs = [
            requirement
            for requirement in state.get("requirements", [])
            if requirement.get("response_section", "").lower() == section.lower()
        ]

        reqs_text = "\n".join(
            f"- [{requirement.get('priority', 'MEDIUM')}] {requirement['description']}"
            for requirement in section_reqs
        )

        feedback = state.get("revision_feedback", {}).get(section, "")
        previous_draft = draft_sections.get(section, "")

        revision_context = ""
        if feedback and previous_draft:
            revision_context = f"""
REVISION INSTRUCTIONS:
This is revision cycle {state.get('revision_count', 0)}.

Previous draft:
{previous_draft}

Reviewer feedback:
{feedback}

Improve the existing draft using the reviewer feedback and evidence.
"""

        system_prompt = f"""You are a senior proposal writer at Acme Corporation.
You are writing section "{section}" of a proposal response to Meridian Healthcare Systems.

Writing guidelines:
- Address the extracted requirements explicitly.
- Ground claims in retrieved knowledge.
- Do not invent capabilities, case studies, or team members.
- Use a professional proposal tone.
- Target roughly 300-500 words.
- If evidence is unavailable, write [REQUIRES HUMAN INPUT].
"""

        user_prompt = f"""Write the "{section}" section.

REQUIREMENTS:
{reqs_text if reqs_text else "No specific requirements extracted."}

RETRIEVED KNOWLEDGE:
{context_text if context_text else "No relevant documents retrieved."}

{revision_context}

Write the section now."""

        response = call_claude(system_prompt, user_prompt, max_tokens=1200)
        total_cost += response["cost"]
        draft_sections[section] = response["content"]

        drafter_metadata["sections"][section] = {
            "word_count": len(response["content"].split()),
            "cost": response["cost"],
            "latency": response["latency"],
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "is_revision": state.get("revision_count", 0) > 0,
        }

        section_span.end(
            input={"requirements_count": len(section_reqs)},
            output={"word_count": len(response["content"].split())},
        )

    generation.end(
        output={
            "sections_drafted": len(sections_to_draft),
            "total_words": sum(len(text.split()) for text in draft_sections.values()),
        }
    )

    return {
        "draft_sections": draft_sections,
        "cumulative_cost": state.get("cumulative_cost", 0) + total_cost,
        "metadata": {
            **state.get("metadata", {}),
            f"drafter_cycle_{state.get('revision_count', 0)}": drafter_metadata,
        },
    }
