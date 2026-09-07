const form = document.querySelector("#researchForm");
const statusEl = document.querySelector("#status");
const reportEl = document.querySelector("#report");
const healthButton = document.querySelector("#healthButton");

function setStatus(message) {
  statusEl.textContent = message;
}

function renderReport(payload) {
  const { report, scraped, errors } = payload;
  reportEl.innerHTML = `
    <header class="report-header">
      <span>${scraped} sources analyzed</span>
      <h2>${escapeHtml(report.title)}</h2>
      <p>${escapeHtml(report.summary)}</p>
    </header>
    ${
      payload.discovered?.length
        ? `<section><h3>Discovered by search</h3><div class="source-list">${payload.discovered
            .map(
              (item) => `
                <a href="${item.url}" target="_blank" rel="noreferrer">
                  <strong>${escapeHtml(item.title)}</strong>
                  <p>${escapeHtml(item.snippet)}</p>
                </a>
              `,
            )
            .join("")}</div></section>`
        : ""
    }
    <section>
      <h3>Key insights</h3>
      <ol class="insight-list">
        ${report.key_insights.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ol>
    </section>
    <section>
      <h3>Related terms</h3>
      <div class="chips">${report.related_terms.map((term) => `<span>${escapeHtml(term)}</span>`).join("")}</div>
    </section>
    <section>
      <h3>Sources</h3>
      <div class="source-list">
        ${report.sources
          .map(
            (source) => `
              <a href="${source.url}" target="_blank" rel="noreferrer">
                <strong>${escapeHtml(source.title)}</strong>
                <small>${escapeHtml(source.site)}</small>
                <p>${escapeHtml(source.description)}</p>
              </a>
            `,
          )
          .join("")}
      </div>
    </section>
    ${
      errors.length
        ? `<section><h3>Skipped sources</h3><ul>${errors
            .map((item) => `<li>${escapeHtml(item.url)}: ${escapeHtml(item.error)}</li>`)
            .join("")}</ul></section>`
        : ""
    }
  `;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = document.querySelector("#query").value.trim();
  const urls = document
    .querySelector("#urls")
    .value.split(/\n+/)
    .map((url) => url.trim())
    .filter(Boolean);

  setStatus("Researching sources...");
  const response = await fetch("/api/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, urls }),
  });
  const payload = await response.json();
  if (!response.ok) {
    setStatus(payload.error || "Unable to generate report.");
    return;
  }
  renderReport(payload);
  setStatus("Report generated and saved.");
});

healthButton.addEventListener("click", async () => {
  const response = await fetch("/api/health");
  setStatus(response.ok ? "Backend is healthy." : "Backend is not responding.");
});
