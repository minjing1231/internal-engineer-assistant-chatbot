from ..schemas import GenerateRequest


SYSTEM_PROMPT = """You are a manufacturing equipment repair assistant.
Use only the provided SOP context and structured data.
Do not invent missing facts.
Prioritize safety precautions and escalation criteria.
Return valid JSON with these keys: issue_summary, relevant_sop_context, recommended_checks, safety_precautions, escalation_criteria, uncertainty."""


def build_messages(request: GenerateRequest) -> list[dict[str, str]]:
    sop_context = "\n\n".join(
        f"[{chunk.source_id} | {chunk.section}]\n{chunk.content}"
        for chunk in request.sop_context
    )
    structured = request.structured_context.model_dump_json(indent=2)
    user_prompt = f"""Question:
{request.question}

SOP Context:
{sop_context}

Structured Context:
{structured}

Generate the troubleshooting answer as grounded JSON."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
