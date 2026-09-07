const reportList = document.querySelector("#reportList");
const refreshReports = document.querySelector("#refreshReports");
const memoryButton = document.querySelector("#memoryButton");
const memoryQuery = document.querySelector("#memoryQuery");
const memoryResults = document.querySelector("#memoryResults");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadReports() {
  const response = await fetch("/api/reports");
  const payload = await response.json();
  reportList.innerHTML = payload.reports.length
    ? payload.reports
        .map(
          (item) => `
            <article class="mini-card">
              <div>
                <strong>${escapeHtml(item.query)}</strong>
                <small>${escapeHtml(item.created_at)}</small>
              </div>
              <p>${escapeHtml(item.payload.summary)}</p>
            </article>
          `,
        )
        .join("")
    : `<p class="muted">No saved reports yet.</p>`;
}

async function searchMemory() {
  const query = memoryQuery.value.trim();
  if (!query) return;
  const response = await fetch(`/api/memory?q=${encodeURIComponent(query)}`);
  const payload = await response.json();
  memoryResults.innerHTML = payload.results.length
    ? payload.results
        .map(
          (item) => `
            <article class="mini-card">
              <div>
                <strong>${escapeHtml(item.title)}</strong>
                <small>score ${item.score}</small>
              </div>
              <p>${escapeHtml(item.snippet)}</p>
              <a href="${item.url}" target="_blank" rel="noreferrer">${escapeHtml(item.url)}</a>
            </article>
          `,
        )
        .join("")
    : `<p class="muted">No memory matches yet.</p>`;
}

refreshReports.addEventListener("click", loadReports);
memoryButton.addEventListener("click", searchMemory);
loadReports();
