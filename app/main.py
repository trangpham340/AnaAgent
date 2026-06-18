from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-powered project analysis agent API.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(analysis_router, prefix="/api/v1", tags=["analysis"])

    @app.get("/", response_class=HTMLResponse, tags=["root"])
    def root() -> str:
        return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Analysis Agent AI</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #172026;
      background: #f4f7f9;
    }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; }
    main { width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 48px; }
    header { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 24px; }
    h1 { font-size: 32px; line-height: 1.1; margin: 0 0 8px; }
    p { margin: 0; color: #58656f; }
    a { color: #0b6bcb; text-decoration: none; }
    .shell { display: grid; grid-template-columns: 360px 1fr; gap: 20px; align-items: start; }
    .panel { background: #ffffff; border: 1px solid #dce4ea; border-radius: 8px; padding: 18px; box-shadow: 0 8px 24px rgba(18, 38, 63, 0.06); }
    label { display: block; font-size: 13px; font-weight: 650; color: #26343d; margin-bottom: 8px; }
    input, textarea {
      width: 100%;
      border: 1px solid #cbd6df;
      border-radius: 6px;
      padding: 10px 12px;
      font: inherit;
      color: #172026;
      background: #fff;
      resize: vertical;
    }
    textarea { min-height: 112px; }
    .field { margin-bottom: 16px; }
    .content-area { min-height: 320px; }
    button {
      border: 0;
      border-radius: 6px;
      padding: 11px 16px;
      font: inherit;
      font-weight: 700;
      color: #fff;
      background: #0a7a4f;
      cursor: pointer;
      min-height: 44px;
    }
    button:disabled { opacity: .65; cursor: wait; }
    .toolbar { display: flex; gap: 12px; align-items: center; margin-top: 14px; }
    .status { color: #58656f; font-size: 14px; }
    .result { display: grid; gap: 14px; }
    .empty { color: #6c7882; border: 1px dashed #c8d4dd; border-radius: 8px; padding: 24px; background: #fbfcfd; }
    .finding { border-left: 4px solid #0b6bcb; padding: 12px 14px; background: #f8fbfd; border-radius: 6px; }
    .finding h3 { margin: 0 0 6px; font-size: 16px; }
    .meta { font-size: 12px; text-transform: uppercase; letter-spacing: .04em; color: #5d6b76; font-weight: 700; }
    .error { border-left-color: #b42318; background: #fff7f6; color: #8a1f16; }
    ul { margin: 8px 0 0; padding-left: 20px; }
    @media (max-width: 860px) {
      main { width: min(100% - 24px, 720px); padding-top: 20px; }
      header, .shell { display: block; }
      .panel { margin-bottom: 16px; }
      h1 { font-size: 26px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Analysis Agent AI</h1>
        <p>Business performance analysis powered by the FastAPI agent.</p>
      </div>
      <p><a href="/docs">API docs</a> · <a href="/health">Health</a></p>
    </header>

    <div class="shell">
      <section class="panel">
        <div class="field">
          <label for="projectName">Project or report name</label>
          <input id="projectName" value="Weekly performance review">
        </div>
        <div class="field">
          <label for="goals">Goals</label>
          <textarea id="goals">Identify business performance drivers
Find risks and next-week actions</textarea>
        </div>
        <div class="field">
          <label for="constraints">Constraints</label>
          <textarea id="constraints">Do not overclaim causality without campaign context</textarea>
        </div>
      </section>

      <section class="panel">
        <div class="field">
          <label for="content">Business data, requirements, notes, or source summary</label>
          <textarea id="content" class="content-area" placeholder="Paste weekly performance data, CSV rows, requirements, or project notes here."></textarea>
        </div>
        <div class="toolbar">
          <button id="analyzeBtn" type="button">Analyze</button>
          <span id="status" class="status">Ready</span>
        </div>
      </section>
    </div>

    <section class="panel result" id="result" style="margin-top:20px;">
      <div class="empty">Submit data to see summary, findings, and next steps.</div>
    </section>
  </main>

  <script>
    const splitLines = (value) => value.split("\\n").map((item) => item.trim()).filter(Boolean);
    const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    }[char]));

    function renderResult(data) {
      const findings = (data.findings || []).map((finding) => `
        <article class="finding">
          <div class="meta">${escapeHtml(finding.severity || "medium")}</div>
          <h3>${escapeHtml(finding.title)}</h3>
          <p>${escapeHtml(finding.detail)}</p>
          <p><strong>Recommendation:</strong> ${escapeHtml(finding.recommendation)}</p>
        </article>
      `).join("");
      const steps = (data.next_steps || []).map((step) => `<li>${escapeHtml(step)}</li>`).join("");
      document.getElementById("result").innerHTML = `
        <div>
          <div class="meta">Summary</div>
          <p>${escapeHtml(data.summary)}</p>
        </div>
        <div>
          <div class="meta">Findings</div>
          ${findings || "<p>No findings returned.</p>"}
        </div>
        <div>
          <div class="meta">Next steps</div>
          <ul>${steps}</ul>
        </div>
        <p class="status">Source: ${escapeHtml(data.source)} | Model: ${escapeHtml(data.model_used)}</p>
      `;
    }

    function renderError(message) {
      document.getElementById("result").innerHTML = `<div class="finding error">${escapeHtml(message)}</div>`;
    }

    document.getElementById("analyzeBtn").addEventListener("click", async () => {
      const button = document.getElementById("analyzeBtn");
      const status = document.getElementById("status");
      const payload = {
        project_name: document.getElementById("projectName").value.trim(),
        content: document.getElementById("content").value.trim(),
        goals: splitLines(document.getElementById("goals").value),
        constraints: splitLines(document.getElementById("constraints").value)
      };

      if (!payload.project_name) {
        renderError("Project or report name is required.");
        return;
      }
      if (payload.content.length < 10) {
        renderError("Content must contain at least 10 characters.");
        return;
      }

      button.disabled = true;
      status.textContent = "Analyzing...";
      try {
        const response = await fetch("/api/v1/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || `API returned ${response.status}`);
        }
        renderResult(data);
        status.textContent = "Complete";
      } catch (error) {
        renderError(error.message || "Analysis failed.");
        status.textContent = "Failed";
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>
        """.strip()

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    return app


app = create_app()
