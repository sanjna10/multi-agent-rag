from .state import RFPPipelineState

def format_rfp_response(state: RFPPipelineState) -> str:
    lines = [
        "=" * 70,
        "  ACME CORPORATION",
        "  Proposal Response to Meridian Healthcare Systems",
        "  RFP-2024-MH-0847: AI-Powered Analytics Platform Enhancement",
        "=" * 70,
        "",
    ]

    for section in state.get("sections_needed", []):
        draft = state.get("draft_sections", {}).get(
            section,
            "[Section not generated]",
        )
        scores = state.get("quality_scores", {}).get(section, {})

        lines.extend([
            "─" * 70,
            f"  {section.upper()}",
        ])

        if scores:
            score_str = " | ".join(
                f"{name}: {score}/10" for name, score in scores.items()
            )
            lines.append(f"  Quality Scores: {score_str}")

        lines.extend([
            "─" * 70,
            "",
            draft,
            "",
        ])

    return "\n".join(lines)
