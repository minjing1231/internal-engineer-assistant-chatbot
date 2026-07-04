from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .clients.data_client import DataClient
from .clients.llm_client import LlmClient
from .clients.rag_client import RagClient
from .config import DATA_SERVICE_URL, LLM_SERVICE_URL, RAG_SERVICE_URL, SERVICE_TIMEOUT_SECONDS
from .logging_utils import install_file_logging
from .orchestration.troubleshooting_flow import TroubleshootingFlow
from .schemas import (
    ApiChatRequest,
    ApiChatResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ServiceError,
    StateReference,
)
from .ui import UI_HTML

app = FastAPI(
    title="Chat API Service",
    version="0.1.0",
    description="Public orchestration API for the manufacturing repair assistant.",
)
install_file_logging(app, "chat-api")

data_client = DataClient(DATA_SERVICE_URL, SERVICE_TIMEOUT_SECONDS)
rag_client = RagClient(RAG_SERVICE_URL, SERVICE_TIMEOUT_SECONDS)
llm_client = LlmClient(LLM_SERVICE_URL, SERVICE_TIMEOUT_SECONDS)
flow = TroubleshootingFlow(data_client, rag_client, llm_client)


@app.get("/", response_class=HTMLResponse, tags=["ui"])
async def index() -> str:
    return UI_HTML
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Repair Engineer Assistant</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7f9;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #5e6b78;
      --line: #dbe1e8;
      --accent: #116466;
      --accent-dark: #0b4f51;
      --soft: #eef4f4;
      --warn: #8a5b00;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    .shell {
      width: min(920px, calc(100vw - 32px));
      margin: 34px auto;
    }
    header {
      border-bottom: 1px solid var(--line);
      padding-bottom: 16px;
      margin-bottom: 18px;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 28px;
      line-height: 1.2;
    }
    p { color: var(--muted); margin: 0; line-height: 1.5; }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }
    label {
      display: block;
      font-weight: 650;
      margin-bottom: 8px;
    }
    textarea {
      width: 100%;
      min-height: 132px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      font: inherit;
      line-height: 1.45;
      background: #fff;
    }
    button {
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: white;
      font-weight: 650;
      padding: 10px 14px;
      cursor: pointer;
    }
    button:hover { background: var(--accent-dark); }
    .samples {
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }
    .sample-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 10px;
    }
    .sample {
      text-align: left;
      background: var(--soft);
      color: var(--ink);
      font-weight: 550;
      padding: 9px 10px;
    }
    .sample:hover { background: #dfecec; }
    .actions {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 12px;
    }
    .status {
      color: var(--muted);
      font-size: 14px;
    }
    .result {
      margin-top: 18px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin: 12px 0 16px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfd;
    }
    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }
    h2 {
      font-size: 17px;
      margin: 18px 0 8px;
    }
    .empty {
      color: var(--muted);
      padding: 18px;
      border: 1px dashed var(--line);
      border-radius: 6px;
      background: #fbfcfd;
    }
    ul, ol {
      margin: 8px 0 0 22px;
      padding: 0;
      line-height: 1.55;
    }
    .sources, .warnings {
      font-size: 14px;
      color: var(--muted);
    }
    .warnings {
      color: var(--warn);
    }
    pre {
      white-space: pre-wrap;
      background: #f3f5f7;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      overflow: auto;
    }
    @media (max-width: 820px) {
      .sample-grid { grid-template-columns: 1fr; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <h1>Manufacturing Repair Assistant</h1>
      <p>Ask an equipment troubleshooting question. The answer is grounded in SOP context and mock equipment data.</p>
    </header>

    <section class="panel">
      <form id="chat-form">
        <label for="question">Troubleshooting question</label>
        <textarea id="question" name="question">Etcher-03 triggered RF101 during plasma ignition. What should I check first?</textarea>
        <div class="actions">
          <button type="submit">Ask Assistant</button>
          <span class="status" id="status">Ready</span>
        </div>
      </form>

      <div class="samples">
        <label>Sample Questions</label>
        <div class="sample-grid">
          <button type="button" class="sample" data-q="Etcher-03 triggered RF101 during plasma ignition. What should I check first?">RF101 first checks</button>
          <button type="button" class="sample" data-q="CMP-02 has low pad pressure. What are the likely causes and recovery steps?">CMP low pressure</button>
          <button type="button" class="sample" data-q="CVD-05 triggered GAS012 during deposition. Should I escalate?">GAS012 escalation</button>
          <button type="button" class="sample" data-q="Litho-01 cannot align wafer properly. What SOP steps should I follow?">Litho alignment</button>
          <button type="button" class="sample" data-q="Unknown equipment triggered alarm ABC999. What should I do?">Unknown alarm</button>
          <button type="button" class="sample" data-q="Etcher-03 had RF101 three times this week. What should be escalated?">Repeated RF101</button>
        </div>
      </div>
    </section>

    <section class="panel result" id="result">
      <div class="empty">Submit a question to generate a troubleshooting response.</div>
    </section>
  </main>

  <script>
    const form = document.getElementById("chat-form");
    const question = document.getElementById("question");
    const statusEl = document.getElementById("status");
    const result = document.getElementById("result");

    document.querySelectorAll("[data-q]").forEach((button) => {
      button.addEventListener("click", () => {
        question.value = button.dataset.q;
        question.focus();
      });
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      statusEl.textContent = "Thinking...";
      result.innerHTML = `<div class="empty">Retrieving SOP context and preparing answer...</div>`;
      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: question.value, top_k: 3, include_incidents: true }),
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "Request failed");
        }
        renderAnswer(data);
        statusEl.textContent = "Done";
      } catch (error) {
        statusEl.textContent = "Error";
        result.innerHTML = `<pre>${escapeHtml(error.message)}</pre>`;
      }
    });

    function renderAnswer(data) {
      const answer = data.answer || {};
      const summary = answer.issue_summary || {};
      result.innerHTML = `
        <div class="grid">
          ${metric("Equipment", summary.equipment)}
          ${metric("Alarm / Symptom", summary.alarm_or_symptom)}
          ${metric("Severity", summary.severity)}
        </div>
        ${section("Relevant SOP Context", (answer.relevant_sop_context || []).map((item) =>
          `${item.source_id}: ${item.title}${item.section ? " (" + item.section + ")" : ""}`
        ))}
        ${section("Recommended Checks", answer.recommended_checks, true)}
        ${section("Safety Precautions", answer.safety_precautions)}
        ${section("Escalation Criteria", answer.escalation_criteria)}
        ${section("Uncertainty / Missing Information", answer.uncertainty)}
        ${section("Sources", (data.sources || []).map((item) =>
          `${item.type}: ${item.id}${item.section ? " / " + item.section : ""}`
        ), false, "sources")}
        ${section("Warnings", data.warnings || [], false, "warnings")}
      `;
    }

    function metric(label, value) {
      return `<div class="metric"><span>${escapeHtml(label)}</span>${escapeHtml(value || "Unknown")}</div>`;
    }

    function section(title, items, ordered = false, className = "") {
      if (!items || items.length === 0) return "";
      const tag = ordered ? "ol" : "ul";
      return `
        <h2>${escapeHtml(title)}</h2>
        <${tag} class="${className}">
          ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </${tag}>
      `;
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }
  </script>
</body>
</html>
    """


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    dependencies = {}
    status = "ok"
    for name, client in {
        "mock_data": data_client,
        "rag_retrieval": rag_client,
        "llm_reasoning": llm_client,
    }.items():
        try:
            dependencies[name] = (await client.health()).get("status", "ok")
        except ServiceError:
            dependencies[name] = "error"
            status = "degraded"
    return HealthResponse(service="chat-api", status=status, dependencies=dependencies)


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    return await flow.answer(request)


@app.post("/api/chat", response_model=ApiChatResponse, tags=["ui"])
async def api_chat(request: ApiChatRequest) -> ApiChatResponse:
    chat_request = ChatRequest(
        question=request.message,
        top_k=3,
        include_incidents=True,
    )
    response = await flow.answer(chat_request)
    return ApiChatResponse(
        answer=_answer_to_text(response),
        model_name="LiquidAI/LFM2.5-1.2B-Instruct",
        retrieval_count=len([source for source in response.sources if source.type == "sop"]),
        generated=not response.warnings,
        state_references=[
            StateReference(
                source_id=source.id,
                title=_source_title(source.id, response),
                section=source.section,
                region=source.id,
            )
            for source in response.sources
            if source.type == "sop"
        ],
        warnings=response.warnings,
    )


def _answer_to_text(response: ChatResponse) -> str:
    answer = response.answer
    if answer.direct_response:
        return answer.direct_response
    lines = []
    decision = answer.action_decision
    lines.append("Action Decision:")
    lines.append(f"- Primary Action: {decision.primary_action or 'Unknown'}")
    lines.append(f"- Escalate: {decision.escalate}")
    lines.append(f"- Reason: {decision.reason or 'Not enough information to determine.'}")
    lines.append("")
    summary = answer.issue_summary
    lines.append("Issue Summary:")
    lines.append(f"- Equipment: {summary.equipment or 'Unknown equipment'}")
    lines.append(f"- Alarm / Symptom: {summary.alarm_or_symptom or 'Unknown alarm or symptom'}")
    lines.append(f"- Severity: {summary.severity or 'Unknown severity'}")
    _extend_sop_context(lines, answer.relevant_sop_context)
    _extend_section(lines, "Recommended Checks", answer.recommended_checks)
    _extend_section(lines, "Likely Causes", answer.likely_causes)
    _extend_section(lines, "Recovery / Next Steps", answer.recovery_next_steps)
    _extend_section(lines, "Safety Precautions", answer.safety_precautions)
    _extend_section(lines, "Escalation Criteria", answer.escalation_criteria)
    _extend_section(lines, "Uncertainty / Missing Information", answer.uncertainty)
    return "\n".join(lines)


def _extend_section(lines: list[str], title: str, items: list[str]) -> None:
    if not items:
        return
    lines.append("")
    lines.append(f"{title}:")
    if title in {"Recommended Checks", "Likely Causes", "Recovery / Next Steps"}:
        lines.extend(f"{index}. {item}" for index, item in enumerate(items, start=1))
        return
    lines.extend(f"- {item}" for item in items)


def _extend_sop_context(lines: list[str], refs: list) -> None:
    if not refs:
        return
    sections = []
    for ref in refs:
        label = ref.section or ref.title or ref.source_id
        if label and label not in sections:
            sections.append(label)
    if not sections:
        return
    lines.append("")
    lines.append("Relevant SOP Context:")
    lines.append(f"- SOP section(s) used: {', '.join(sections)}")


def _source_title(source_id: str, response: ChatResponse) -> str:
    for item in response.answer.relevant_sop_context:
        if item.source_id == source_id:
            return item.title
    return source_id
