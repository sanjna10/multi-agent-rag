import time

from ..clients import langfuse
from ..config import PROPOSALS_NAMESPACE, KNOWLEDGE_NAMESPACE
from ..retrieval import search_pinecone
from ..state import RFPPipelineState

def _namespaces_for_section(section: str) -> list[str]:
    section_name = section.lower()

    if section_name == "cost and value":
        return [KNOWLEDGE_NAMESPACE, PROPOSALS_NAMESPACE]

    return [PROPOSALS_NAMESPACE, KNOWLEDGE_NAMESPACE]

def knowledge_retriever_agent(state: RFPPipelineState) -> dict:
    """
    Agent 2: section-aware retrieval with fallback query refinement.
    """

    trace = langfuse.trace(id=state["trace_id"])
    span = trace.span(name="knowledge-retriever")

    retrieved = {}
    retriever_metadata = {"sections": {}, "total_chunks_retrieved": 0}

    for section in state["sections_needed"]:
        section_span = span.span(name=f"retrieve-{section}")
        start_time = time.time()

        namespaces = _namespaces_for_section(section)

        section_requirements = [
            requirement
            for requirement in state["requirements"]
            if requirement.get("response_section", "").lower() == section.lower()
        ]

        req_text = "; ".join(
            requirement["description"]
            for requirement in section_requirements[:3]
        )
        primary_query = f"{section}: {req_text}" if req_text else section

        all_results = []
        seen_ids = set()

        for namespace in namespaces:
            for result in search_pinecone(primary_query, namespace, top_k=5):
                if result["id"] not in seen_ids:
                    seen_ids.add(result["id"])
                    all_results.append(result)

        high_relevance = [
            result for result in all_results if result["score"] > 0.7
        ]

        refinement_needed = len(high_relevance) < 3

        if refinement_needed and section_requirements:
            refined_query = section_requirements[0]["description"]

            for namespace in namespaces:
                for result in search_pinecone(refined_query, namespace, top_k=3):
                    if result["id"] not in seen_ids:
                        seen_ids.add(result["id"])
                        all_results.append(result)

        all_results.sort(key=lambda item: item["score"], reverse=True)
        all_results = all_results[:8]

        retrieved[section] = all_results
        elapsed = time.time() - start_time

        retriever_metadata["sections"][section] = {
            "chunks_retrieved": len(all_results),
            "namespaces_searched": namespaces,
            "refinement_needed": refinement_needed,
            "latency": elapsed,
        }
        retriever_metadata["total_chunks_retrieved"] += len(all_results)

        section_span.end(
            output={
                "chunks": len(all_results),
                "top_score": all_results[0]["score"] if all_results else 0,
            }
        )

    span.end(
        output={
            "sections_retrieved": len(retrieved),
            "total_chunks": retriever_metadata["total_chunks_retrieved"],
        }
    )

    return {
        "retrieved_knowledge": retrieved,
        "metadata": {
            **state.get("metadata", {}),
            "knowledge_retriever": retriever_metadata,
        },
    }
