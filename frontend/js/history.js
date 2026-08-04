/* history.js */

(async function init() {
  const name = await requireAuth();
  if (!name) return;
  paintSidebar(name, "history");
  await loadHistory();
})();

async function loadHistory() {
  const { ok, data } = await apiRequest("/history");
  const wrap = document.getElementById("historyTableWrap");

  if (!ok || !data.history.length) {
    wrap.innerHTML = `<div class="empty-state">No intake history yet.</div>`;
    return;
  }

  const rows = data.history.map((h) => `
    <tr>
      <td>${h.log_date}</td>
      <td>${h.scheduled_time}</td>
      <td>${h.medicine_name}</td>
      <td>${h.dosage}</td>
      <td><span class="status-tag ${h.status === 'taken' ? 'taken' : h.status === 'missed' ? 'missed' : 'skipped'}">${h.status}</span></td>
    </tr>
  `).join("");

  wrap.innerHTML = `
    <table class="history-table">
      <thead>
        <tr><th>Date</th><th>Time</th><th>Medicine</th><th>Dosage</th><th>Status</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}
