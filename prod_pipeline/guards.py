import re

from .clients import langfuse, pii_analyzer, pii_anonymizer
from .config import MAX_COST_PER_RFP
from .state import RFPPipelineState

def input_guard(state: RFPPipelineState) -> dict:
    trace = langfuse.trace(id=state["trace_id"], name="rfp-pipeline")
    span = trace.span(name="input-guard")

    rfp = state["rfp_text"]
    errors = list(state.get("errors", []))

    if len(rfp) > 50000:
        rfp = rfp[:50000]
        errors.append("RFP text truncated to 50,000 characters")

    patterns = [
        r"ignore\s+(previous|above|all)\s+(instructions|prompts)",
        r"you\s+are\s+now\s+",
        r"system\s*:\s*",
        r"<\s*system\s*>",
        r"OVERRIDE",
        r"bypass\s+(safety|security|guard)",
        r"forget\s+(everything|all|your)",
    ]

    sanitized = rfp
    for pattern in patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            sanitized = re.sub(
                pattern,
                "[FILTERED]",
                sanitized,
                flags=re.IGNORECASE,
            )
            errors.append(f"Injection pattern filtered in RFP: {pattern}")

    span.end(
        input={"rfp_length": len(rfp)},
        output={"sanitized_length": len(sanitized), "errors": errors},
    )

    return {
        "sanitized_rfp": sanitized,
        "errors": errors,
        "cumulative_cost": 0.0,
    }

def output_guard(state: RFPPipelineState) -> dict:
    trace = langfuse.trace(id=state["trace_id"])
    span = trace.span(name="output-guard")

    errors = list(state.get("errors", []))
    draft_sections = dict(state.get("draft_sections", {}))
    total_pii_entities = 0

    for section, text in draft_sections.items():
        pii_results = pii_analyzer.analyze(
            text=text,
            language="en",
            entities=[
                "PHONE_NUMBER",
                "EMAIL_ADDRESS",
                "CREDIT_CARD",
                "US_SSN",
                "US_PASSPORT",
                "IBAN_CODE",
                "PERSON",
            ],
        )

        sensitive_results = [
            result for result in pii_results if result.entity_type != "PERSON"
        ]

        if sensitive_results:
            anonymized = pii_anonymizer.anonymize(
                text=text,
                analyzer_results=sensitive_results,
            )
            draft_sections[section] = anonymized.text
            total_pii_entities += len(sensitive_results)

    cumulative_cost = state.get("cumulative_cost", 0)
    metadata = dict(state.get("metadata", {}))
    metadata["final_summary"] = {
        "total_cost": cumulative_cost,
        "cost_limit": MAX_COST_PER_RFP,
        "cost_utilization": (
            f"{(cumulative_cost / MAX_COST_PER_RFP) * 100:.1f}%"
            if MAX_COST_PER_RFP
            else "N/A"
        ),
        "revision_cycles": state.get("revision_count", 0),
        "pii_entities_redacted": total_pii_entities,
        "sections_generated": len(draft_sections),
    }

    span.end(output=metadata["final_summary"])
    langfuse.flush()

    return {
        "draft_sections": draft_sections,
        "errors": errors,
        "metadata": metadata,
    }
