import os
import sys
from datetime import datetime

from .config import (
    MAX_COST_PER_RFP,
    MAX_REVISION_CYCLES,
    MIN_QUALITY_SCORE,
)
from .data import SAMPLE_RFP
from .formatter import format_rfp_response
from .graph import build_rfp_pipeline
from .ingestion import ingest_documents
from .state import RFPPipelineState

def run_rfp_pipeline(rfp_text: str | None = None) -> dict:
    if rfp_text is None:
        rfp_text = SAMPLE_RFP

    trace_id = f"capstone-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    initial_state: RFPPipelineState = {
        "rfp_text": rfp_text,
        "sanitized_rfp": "",
        "requirements": [],
        "sections_needed": [],
        "complexity_score": 0,
        "retrieved_knowledge": {},
        "draft_sections": {},
        "revision_feedback": {},
        "quality_scores": {},
        "revision_count": 0,
        "metadata": {},
        "errors": [],
        "trace_id": trace_id,
        "cumulative_cost": 0.0,
    }

    print("=" * 70)
    print("RFP RESPONSE GENERATOR")
    print(f"Trace ID: {trace_id}")
    print(f"Cost Limit: ${MAX_COST_PER_RFP:.2f}")
    print(f"Max Revision Cycles: {MAX_REVISION_CYCLES}")
    print("=" * 70)

    pipeline = build_rfp_pipeline()

    try:
        final_state = pipeline.invoke(initial_state)
    except Exception as exc:
        return {"errors": [str(exc)], "trace_id": trace_id}

    print(format_rfp_response(final_state))

    metadata = final_state.get("metadata", {})
    summary = metadata.get("final_summary", {})

    print("\nPIPELINE METRICS")
    print(f"Total cost: ${summary.get('total_cost', 0):.4f}")
    print(f"Revision cycles: {summary.get('revision_cycles', 0)}")

    print("\nQuality Scores:")
    for section, scores in final_state.get("quality_scores", {}).items():
        average = sum(scores.values()) / len(scores) if scores else 0
        status = (
            "PASS"
            if all(score >= MIN_QUALITY_SCORE for score in scores.values())
            else "NEEDS REVIEW"
        )
        print(f"{section:30s} avg: {average:.1f}/10 [{status}]")

    host = os.getenv("LANGFUSE_HOST")
    if host:
        print(f"\nView trace: {host}/trace/{trace_id}")

    return final_state

if __name__ == "__main__":
    if "--ingest" in sys.argv:
        ingest_documents()
    else:
        run_rfp_pipeline()
