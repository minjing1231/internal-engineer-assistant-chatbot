from ..schemas import GenerateRequest


SYSTEM_PROMPT = """You are a manufacturing equipment repair assistant.
Use only the provided SOP context and structured data.
Do not invent missing facts.
Prioritize safety precautions and escalation criteria.
Return valid JSON only. Do not return markdown.
The JSON schema must be:
{
  "action_decision": {
    "primary_action": "string or null",
    "escalate": "Yes, No, Conditional, or Unknown",
    "reason": "string or null"
  },
  "issue_summary": {
    "equipment": "string or null",
    "alarm_or_symptom": "string or null",
    "severity": "Low, Medium, High, or null"
  },
  "relevant_sop_context": [
    {"source_id": "string", "title": "string", "section": "string or null"}
  ],
  "recommended_checks": ["string"],
  "likely_causes": ["string"],
  "recovery_next_steps": ["string"],
  "safety_precautions": ["string"],
  "escalation_criteria": ["string"],
  "uncertainty": ["string"]
}
Use action_decision to answer the user's intent first. For escalation questions, set escalate clearly.
All list fields must be JSON arrays, even if there is only one item."""


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
