import json
import re

from ..clients import langfuse
from ..config import CLAUDE_MODEL
from ..llm import call_claude
from ..state import RFPPipelineState

DEFAULT_SECTIONS = [
    "Technical Approach",
    "Healthcare Experience",
    "Team Qualifications",
    "Timeline",
    "Cost and Value",
]

def _parse_analysis(content: str) -> dict:
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
        "requirements": [],
        "sections_needed": DEFAULT_SECTIONS,
        "complexity_score": 5,
    }

def rfp_analyzer_agent(state: RFPPipelineState) -> dict:
    """Agent 1: extract structured requirements and required proposal sections."""

    trace = langfuse.trace(id=state["trace_id"])
    generation = trace.generation(
        name="rfp-analyzer",
        model=CLAUDE_MODEL,
        input={"rfp_length": len(state["sanitized_rfp"])},
    )

    system_prompt = """You are an expert RFP analyst at Acme Corporation.

Extract:
1. requirements: each with id, description, category, priority, response_section
2. sections_needed
3. complexity_score from 1-10

Requirement categories:
technical, experience, team, timeline, cost, compliance.

Return valid JSON only with keys:
requirements, sections_needed, complexity_score.
"""

    user_prompt = f"""Analyze this RFP and extract structured requirements:

{state['sanitized_rfp']}"""

    response = call_claude(system_prompt, user_prompt, max_tokens=2000)
    parsed = _parse_analysis(response["content"])

    requirements = parsed.get("requirements", [])
    sections_needed = parsed.get("sections_needed", DEFAULT_SECTIONS)
    complexity_score = parsed.get("complexity_score", 5)

    generation.end(
        output={
            "requirements_count": len(requirements),
            "sections": sections_needed,
            "complexity": complexity_score,
        },
        usage={
            "input": response["input_tokens"],
            "output": response["output_tokens"],
        },
    )

    return {
        "requirements": requirements,
        "sections_needed": sections_needed,
        "complexity_score": complexity_score,
        "cumulative_cost": state.get("cumulative_cost", 0) + response["cost"],
        "metadata": {
            **state.get("metadata", {}),
            "rfp_analyzer": {
                "requirements_count": len(requirements),
                "complexity_score": complexity_score,
                "cost": response["cost"],
                "latency": response["latency"],
                "input_tokens": response["input_tokens"],
                "output_tokens": response["output_tokens"],
            },
        },
    }
