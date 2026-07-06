UI_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Repair Knowledge Workspace</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4f6f8;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #60707f;
      --line: #d8e0e8;
      --soft: #edf4f4;
      --accent: #116466;
      --accent-dark: #0b4f51;
      --amber: #9a6700;
      --danger: #ad343e;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    .topbar {
      height: 58px;
      display: flex;
      align-items: center;
      justify-content: flex-start;
      gap: 16px;
      padding: 0 18px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    .brand strong { display: block; font-size: 16px; }
    .brand span { color: var(--muted); font-size: 13px; }
    [hidden] { display: none !important; }
    .sample-toggle, .sample, .nav-item, .clear, .send, .ref-card, .login-submit {
      border: 0;
      border-radius: 6px;
      font: inherit;
      cursor: pointer;
    }
    .login-screen {
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
      background:
        linear-gradient(135deg, rgba(17, 100, 102, 0.08), transparent 38%),
        var(--bg);
    }
    .login-card {
      width: min(420px, 100%);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 24px;
      box-shadow: 0 16px 40px rgba(23, 32, 42, 0.08);
    }
    .login-card h1 {
      font-size: 22px;
      margin-bottom: 6px;
    }
    .login-card p {
      margin: 0 0 18px;
    }
    .login-form {
      display: grid;
      gap: 12px;
    }
    .login-form label {
      display: grid;
      gap: 7px;
      font-size: 13px;
      font-weight: 700;
      color: var(--ink);
    }
    .login-form input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      font: inherit;
      background: #fff;
    }
    .login-submit {
      margin-top: 4px;
      background: var(--accent);
      color: #fff;
      padding: 10px 12px;
      font-weight: 700;
    }
    .login-submit:hover {
      background: var(--accent-dark);
    }
    .login-error {
      min-height: 18px;
      color: var(--danger);
      font-size: 13px;
      font-weight: 650;
    }
    .workspace {
      height: calc(100vh - 58px);
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 14px;
      padding: 14px;
    }
    .panel {
      min-height: 0;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    .document-panel {
      overflow: visible;
    }
    .panel-head {
      padding: 14px;
      border-bottom: 1px solid var(--line);
    }
    h1, h2, h3 { margin: 0; }
    h2 { font-size: 15px; }
    h3 { font-size: 14px; margin-top: 16px; }
    .muted { color: var(--muted); font-size: 13px; line-height: 1.45; }
    .nav-list {
      padding: 10px;
      overflow: auto;
      height: calc(100% - 68px);
    }
    .nav-item {
      width: 100%;
      text-align: left;
      padding: 10px;
      background: transparent;
      border: 1px solid transparent;
      margin-bottom: 6px;
      color: var(--ink);
    }
    .nav-item span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 3px;
    }
    .nav-item.active {
      background: var(--soft);
      border-color: #c9dddd;
    }
    .detail {
      padding: 12px;
      overflow: visible;
      height: auto;
    }
    .meta-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      margin: 10px 0;
    }
    .meta {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      background: #fbfcfd;
    }
    .meta span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }
    .doc-sections {
      display: grid;
      gap: 8px;
      margin: 10px 0;
    }
    .doc-section {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: #fbfcfd;
      line-height: 1.42;
    }
    .doc-section h3 {
      margin-top: 0;
      margin-bottom: 7px;
    }
    .doc-section p {
      margin: 0;
      color: #26333f;
    }
    .doc-section ol {
      margin: 0;
      padding-left: 22px;
      color: #26333f;
    }
    .doc-section li {
      margin-bottom: 4px;
    }
    .doc-section li:last-child {
      margin-bottom: 0;
    }
    .doc-section.highlight {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(17, 100, 102, 0.15);
    }
    .chat {
      display: grid;
      grid-template-rows: auto 1fr auto;
      height: 100%;
    }
    .chat-head {
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 10px;
    }
    .clear {
      background: #f1f4f6;
      color: var(--muted);
      padding: 7px 9px;
      font-weight: 600;
    }
    .messages {
      padding: 14px;
      overflow: auto;
      background: #f8fafb;
    }
    .message {
      max-width: 94%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 10px;
      line-height: 1.5;
      background: #fff;
      white-space: pre-wrap;
    }
    .message.user {
      margin-left: auto;
      background: var(--soft);
      border-color: #c9dddd;
    }
    .message.assistant {
      margin-right: auto;
    }
    .chat-bottom {
      padding: 12px;
      border-top: 1px solid var(--line);
      background: var(--panel);
    }
    .sample-toggle {
      width: 100%;
      background: #edf1f4;
      color: var(--ink);
      padding: 9px 10px;
      text-align: left;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .sample-toggle span {
      float: right;
      color: var(--muted);
      font-weight: 600;
    }
    .sample-wrap {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 7px;
      margin-bottom: 10px;
    }
    .sample-wrap[hidden] {
      display: none;
    }
    .sample {
      background: #edf1f4;
      color: var(--ink);
      padding: 8px;
      text-align: left;
      font-size: 12px;
      font-weight: 600;
    }
    textarea {
      width: 100%;
      resize: vertical;
      min-height: 76px;
      max-height: 160px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      font: inherit;
      line-height: 1.4;
    }
    .send-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-top: 8px;
    }
    .send {
      background: var(--accent);
      color: white;
      padding: 9px 12px;
      font-weight: 700;
    }
    .status { color: var(--muted); font-size: 13px; }
    .ref-card {
      display: inline-flex;
      align-items: center;
      width: auto;
      max-width: 100%;
      text-align: left;
      background: #fff8ea;
      border: 1px solid #f0d8a0;
      color: var(--ink);
      padding: 5px 8px;
      font-size: 12px;
      font-weight: 700;
      line-height: 1.2;
    }
    .ref-card strong { color: var(--amber); }
    .ref-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
      white-space: normal;
    }
    @media (max-width: 1040px) {
      .workspace {
        height: auto;
        grid-template-columns: 1fr;
      }
      .panel { min-height: 300px; }
      .chat { min-height: 620px; }
    }
  </style>
</head>
<body>
  <main class="login-screen" id="login-screen">
    <section class="login-card">
      <h1>Repair Knowledge Workspace</h1>
      <p class="muted">Sign in to access SOP guidance and the repair assistant.</p>
      <form class="login-form" id="login-form">
        <label>
          Username
          <input id="login-username" name="username" autocomplete="username" />
        </label>
        <label>
          Password
          <input id="login-password" name="password" type="password" autocomplete="current-password" />
        </label>
        <button type="submit" class="login-submit">Login</button>
        <div class="login-error" id="login-error" aria-live="polite"></div>
      </form>
    </section>
  </main>

  <div id="workspace-shell" hidden>
    <header class="topbar">
      <div class="brand">
        <strong>Repair Knowledge Workspace</strong>
        <span>SOP-guided manufacturing equipment assistant</span>
      </div>
    </header>

    <main class="workspace">
      <!--
      <aside class="panel">
        <div class="panel-head">
          <h2>SOP Regions</h2>
          <p class="muted">Select a document to inspect its full SOP guidance.</p>
        </div>
        <div class="nav-list" id="region-list"></div>
      </aside>

      <section class="panel document-panel">
        <div class="panel-head">
          <h2 id="region-title"></h2>
          <p class="muted" id="region-description"></p>
        </div>
        <div class="detail">
          <div class="meta-grid">
            <div class="meta"><span>Equipment</span><strong id="equipment"></strong></div>
            <div class="meta"><span>Alarm</span><strong id="alarm"></strong></div>
            <div class="meta"><span>Severity</span><strong id="severity"></strong></div>
          </div>
          <div class="doc-sections" id="doc-sections"></div>
        </div>
      </section>
      -->

      <section class="panel chat">
        <div class="panel-head chat-head">
          <div>
            <h2>Repair Assistant</h2>
            <p class="muted">Conversation history stays visible during the session.</p>
          </div>
          <button type="button" class="clear" id="clear-chat">Clear</button>
        </div>
        <div class="messages" id="messages"></div>
        <div class="chat-bottom">
          <button type="button" class="sample-toggle" id="sample-toggle" aria-expanded="false">
            Sample questions <span id="sample-toggle-label">Show</span>
          </button>
          <div class="sample-wrap" id="sample-wrap" hidden>
            <button type="button" class="sample" data-q="Etcher-03 triggered RF101 during plasma ignition. What should I check first?">RF101 first checks</button>
            <button type="button" class="sample" data-q="CMP-02 has low pad pressure. What are the likely causes and recovery steps?">CMP low pressure</button>
            <button type="button" class="sample" data-q="CVD-05 triggered GAS012 during deposition. Should I escalate?">GAS012 escalation</button>
            <button type="button" class="sample" data-q="PVD-02 triggered VAC033 during pump-down. What should I check?">VAC033 pump-down</button>
          </div>
          <form id="chat-form">
            <textarea id="chat-input" placeholder="Ask a troubleshooting question..."></textarea>
            <div class="send-row">
              <span class="status" id="status">Ready</span>
              <button type="submit" class="send">Send</button>
            </div>
          </form>
        </div>
      </section>
    </main>
  </div>

  <script>
    const regions = [
      {
        id: "SOP-ETCH-001",
        scope: ["all", "etch-cmp"],
        title: "Etcher RF Power Instability",
        description: "RF101 troubleshooting for plasma ignition or steady-state RF instability.",
        equipment: "Etcher-03",
        alarm: "RF101",
        severity: "High",
        entryFrom: "Alarm detected during plasma step",
        exitTo: "Restart or escalation",
        anomaly: "Yes",
        states: [
          ["Symptoms", "RF generator output fluctuates, alarm appears during plasma ignition, or RF trend shows sudden dip or oscillation."],
          ["Safety Precautions", "Confirm safe state, avoid RF cables while enabled, and follow lockout/tagout before hardware inspection."],
          ["Troubleshooting Steps", "Verify RF generator output, check RF trend, inspect cable connectors, review matching network and PM records."],
          ["Escalation Criteria", "Escalate if downtime exceeds 30 minutes, RF101 repeats more than twice in 7 days, or RF hardware fault is suspected."]
        ]
      },
      {
        id: "SOP-CMP-002",
        scope: ["all", "etch-cmp"],
        title: "CMP Pad Pressure Low",
        description: "CMP205 troubleshooting for pressure below recipe range.",
        equipment: "CMP-02",
        alarm: "CMP205",
        severity: "Medium",
        entryFrom: "Pressure alarm from polishing process",
        exitTo: "Calibration, replacement, or escalation",
        anomaly: "Yes",
        states: [
          ["Symptoms", "Pad pressure is below operating range, noisy, or lower than recipe setpoint."],
          ["Safety Precautions", "Keep hands away from moving platen or carrier head and stop the tool before inspection."],
          ["Troubleshooting Steps", "Check pressure reading, inspect sensor stability, look for hydraulic leakage, check pad age, run calibration."],
          ["Escalation Criteria", "Escalate if pressure remains low, leak is suspected, or alarm repeats after pad replacement."]
        ]
      },
      {
        id: "SOP-CVD-003",
        scope: ["all", "deposition-litho"],
        title: "CVD Gas Flow Deviation",
        description: "GAS012 high-priority gas flow deviation handling.",
        equipment: "CVD-05",
        alarm: "GAS012",
        severity: "High",
        entryFrom: "Gas flow alarm during deposition",
        exitTo: "Hold lot or process engineer review",
        anomaly: "Yes",
        states: [
          ["Symptoms", "Measured gas flow deviates from recipe setting or MFC reading is unstable."],
          ["Safety Precautions", "Treat gas alarms as high priority. Do not bypass gas interlocks."],
          ["Troubleshooting Steps", "Compare MFC reading with recipe target, check supply pressure, calibration record, leak check, valve status."],
          ["Escalation Criteria", "Escalate for any gas safety concern, MFC drift, leak suspicion, or affected lot during deviation."]
        ]
      },
      {
        id: "SOP-LITHO-004",
        scope: ["all", "deposition-litho"],
        title: "Lithography Wafer Alignment Failure",
        description: "ALIGN011 workflow when wafer alignment marks cannot be detected.",
        equipment: "Litho-01",
        alarm: "ALIGN011",
        severity: "Low",
        entryFrom: "Alignment attempt failed",
        exitTo: "Retry, calibration, or escalation",
        anomaly: "Yes",
        states: [
          ["Symptoms", "Tool cannot detect wafer alignment mark or notch, camera image may be unclear."],
          ["Safety Precautions", "Do not manually move wafer stage unless approved and avoid touching optical components."],
          ["Troubleshooting Steps", "Clean camera viewing window, inspect wafer orientation, check recipe, run calibration, retry with test wafer."],
          ["Escalation Criteria", "Escalate if alignment fails after cleaning/calibration, multiple wafers fail, or camera remains unclear."]
        ]
      },
      {
        id: "SOP-TEMP-005",
        scope: ["all", "etch-cmp", "deposition-litho"],
        title: "Chamber Temperature High",
        description: "TEMP008 troubleshooting for abnormal chamber temperature.",
        equipment: "Etcher / CVD / Furnace",
        alarm: "TEMP008",
        severity: "Medium",
        entryFrom: "Temperature threshold exceeded",
        exitTo: "Stabilize or escalate",
        anomaly: "Yes",
        states: [
          ["Symptoms", "Chamber temperature exceeds threshold or trend rises above normal profile."],
          ["Safety Precautions", "Do not open hot chamber until safe. Use heat-resistant PPE if inspection is required."],
          ["Troubleshooting Steps", "Check temperature trend, cooling water flow, heater output, thermocouple reading, then stabilize before restart."],
          ["Escalation Criteria", "Escalate if temperature remains high, sensor reading is unstable, or alarm repeats after restart."]
        ]
      },
      {
        id: "SOP-VAC-006",
        scope: ["all", "deposition-litho"],
        title: "Vacuum Pressure High",
        description: "VAC033 troubleshooting for chamber pump-down or high pressure.",
        equipment: "PVD-02",
        alarm: "VAC033",
        severity: "High",
        entryFrom: "Vacuum pressure alarm",
        exitTo: "Leak check, pump recovery, or escalation",
        anomaly: "Yes",
        states: [
          ["Symptoms", "Chamber cannot reach vacuum pressure or remains higher than target after pump-down."],
          ["Safety Precautions", "Do not open chamber until vent sequence is complete. Follow vacuum pump safety procedure."],
          ["Troubleshooting Steps", "Check door status, seal condition, pump-down curve, pump alarms, leak check, and pressure gauge."],
          ["Escalation Criteria", "Escalate if vacuum cannot recover in 20 minutes, leak check fails, pump alarm exists, or lot is inside."]
        ]
      },
      {
        id: "SOP-ROBOT-007",
        scope: ["all"],
        title: "Wafer Transfer Error",
        description: "ROBOT017 troubleshooting for wafer handling robot transfer failures.",
        equipment: "Wafer Handling Robot",
        alarm: "ROBOT017",
        severity: "Medium",
        entryFrom: "Robot pick/place failure",
        exitTo: "Dry-cycle, cleaning, or escalation",
        anomaly: "Yes",
        states: [
          ["Symptoms", "Robot fails to pick, place, or transfer wafer; sensor or end-effector may be abnormal."],
          ["Safety Precautions", "Do not reach into transfer area while robot power is enabled. Stop automatic transfer first."],
          ["Troubleshooting Steps", "Check home position, inspect end-effector, verify wafer sensor, dry-cycle, check wafer alignment."],
          ["Escalation Criteria", "Escalate if wafer damage is suspected, dry-cycle fails, or sensor remains abnormal after cleaning."]
        ]
      },
      {
        id: "SOP-PART-008",
        scope: ["all", "etch-cmp", "deposition-litho"],
        title: "Particle Count High",
        description: "PART090 troubleshooting for chamber contamination or quality risk.",
        equipment: "Etch / Deposition / PVD",
        alarm: "PART090",
        severity: "High",
        entryFrom: "Particle alarm or process control result",
        exitTo: "Cleaning, qualification, or process disposition",
        anomaly: "Yes",
        states: [
          ["Symptoms", "Particle count exceeds process control limit; chamber contamination or worn consumables may be present."],
          ["Safety Precautions", "Hold affected lot until process disposition and do not resume until qualification is completed if required."],
          ["Troubleshooting Steps", "Check cleaning records, inspect consumables, run particle wafer, review recent maintenance, compare trend."],
          ["Escalation Criteria", "Escalate if particle count remains high, production lot is at risk, or repeated alarm occurs within 7 days."]
        ]
      }
    ];

    let activeRegion = regions[0].id;
    const regionList = document.getElementById("region-list");
    const messages = document.getElementById("messages");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const statusEl = document.getElementById("status");
    const sampleToggle = document.getElementById("sample-toggle");
    const sampleToggleLabel = document.getElementById("sample-toggle-label");
    const sampleWrap = document.getElementById("sample-wrap");
    const loginScreen = document.getElementById("login-screen");
    const workspaceShell = document.getElementById("workspace-shell");
    const loginForm = document.getElementById("login-form");
    const loginUsername = document.getElementById("login-username");
    const loginPassword = document.getElementById("login-password");
    const loginError = document.getElementById("login-error");

    function showWorkspace() {
      loginScreen.hidden = true;
      workspaceShell.hidden = false;
    }

    if (sessionStorage.getItem("repair-assistant-authenticated") === "true") {
      showWorkspace();
    } else {
      loginUsername.focus();
    }

    loginForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const username = loginUsername.value.trim();
      const password = loginPassword.value;
      if (username === "hana" && password === "123") {
        sessionStorage.setItem("repair-assistant-authenticated", "true");
        loginError.textContent = "";
        showWorkspace();
        return;
      }
      loginError.textContent = "Invalid username or password.";
      loginPassword.value = "";
      loginPassword.focus();
    });

    sampleToggle.addEventListener("click", () => {
      const willShow = sampleWrap.hidden;
      sampleWrap.hidden = !willShow;
      sampleToggle.setAttribute("aria-expanded", String(willShow));
      sampleToggleLabel.textContent = willShow ? "Hide" : "Show";
    });

    document.querySelectorAll(".sample").forEach((button) => {
      button.addEventListener("click", () => {
        input.value = button.dataset.q;
        sampleWrap.hidden = true;
        sampleToggle.setAttribute("aria-expanded", "false");
        sampleToggleLabel.textContent = "Show";
        input.focus();
      });
    });

    input.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || event.shiftKey) return;
      event.preventDefault();
      form.requestSubmit();
    });

    document.getElementById("clear-chat").addEventListener("click", () => {
      messages.innerHTML = "";
      statusEl.textContent = "Ready";
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const message = input.value.trim();
      if (!message) return;
      appendMessage("user", message);
      input.value = "";
      statusEl.textContent = "Working...";
      const working = appendMessage("assistant", "Retrieving SOP context and preparing answer...");
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({message, configuration: "all", region: activeRegion})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Request failed");
        working.remove();
        appendAssistant(data);
        statusEl.textContent = "Done";
      } catch (error) {
        working.textContent = error.message;
        statusEl.textContent = "Error";
      }
    });

    function filteredRegions() {
      return regions;
    }

    function render() {
      if (!regionList) return;
      renderNav();
      renderDetail();
    }

    function renderNav() {
      regionList.innerHTML = filteredRegions().map((region) => `
        <button type="button" class="nav-item ${region.id === activeRegion ? "active" : ""}" data-region="${region.id}">
          ${escapeHtml(region.title)}
          <span>${escapeHtml(region.alarm)} / ${escapeHtml(region.equipment)}</span>
        </button>
      `).join("");
      regionList.querySelectorAll("[data-region]").forEach((button) => {
        button.addEventListener("click", () => {
          activeRegion = button.dataset.region;
          render();
        });
      });
    }

    function renderDetail() {
      const region = regions.find((item) => item.id === activeRegion) || filteredRegions()[0];
      if (!document.getElementById("region-title")) return;
      document.getElementById("region-title").textContent = region.title;
      document.getElementById("region-description").textContent = region.description;
      document.getElementById("equipment").textContent = region.equipment;
      document.getElementById("alarm").textContent = region.alarm;
      document.getElementById("severity").textContent = region.severity;
      document.getElementById("doc-sections").innerHTML = region.states.map((state, index) => `
        <section class="doc-section" data-section-index="${index}">
          <h3>${escapeHtml(state[0])}</h3>
          ${renderSectionBody(state[0], state[1])}
        </section>
      `).join("");
    }

    function renderSectionBody(title, detail) {
      if (title !== "Safety Precautions" && title !== "Troubleshooting Steps" && title !== "Escalation Criteria") {
        return `<p>${escapeHtml(detail)}</p>`;
      }
      const items = detail
        .replace(/\\.$/, "")
        .split(/,\\s+(?:and\\s+)?/)
        .map((item) => item.trim())
        .filter(Boolean);
      return `<ol>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`;
    }

    function appendMessage(role, text) {
      const node = document.createElement("div");
      node.className = `message ${role}`;
      node.textContent = text;
      messages.appendChild(node);
      messages.scrollTop = messages.scrollHeight;
      return node;
    }

    function appendAssistant(data) {
      const node = appendMessage("assistant", data.answer || "No answer returned.");
      /*
      const refs = data.state_references || [];
      if (refs.length) {
        const refList = document.createElement("div");
        refList.className = "ref-list";
        refs.forEach((ref) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "ref-card";
        card.innerHTML = `<strong>${escapeHtml(ref.source_id)}${ref.section ? " / " + escapeHtml(ref.section) : ""}</strong>`;
        card.addEventListener("click", () => navigateToReference(ref));
          refList.appendChild(card);
        });
        node.appendChild(refList);
      }
      */
      if (data.warnings && data.warnings.length) {
        const warning = document.createElement("div");
        warning.className = "muted";
        warning.textContent = data.warnings.join(" ");
        node.appendChild(warning);
      }
    }

    function navigateToReference(ref) {
      const region = regions.find((item) => item.id === ref.source_id);
      if (!region) return;
      activeRegion = region.id;
      const stateIndex = ref.section && ref.section !== "Summary"
        ? region.states.findIndex((state) => state[0] === ref.section)
        : -1;
      render();
      if (stateIndex < 0) return;
      const section = document.querySelector(`[data-section-index="${stateIndex}"]`);
      if (!section) return;
      section.scrollIntoView({behavior: "smooth", block: "center"});
      section.classList.add("highlight");
      window.setTimeout(() => section.classList.remove("highlight"), 1400);
    }

    function escapeHtml(value) {
      return String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    render();
  </script>
</body>
</html>
"""
