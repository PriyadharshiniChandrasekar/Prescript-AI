/* dashboard.js */

(async function init() {
  const name = await requireAuth();
  if (!name) return;
  paintSidebar(name, "dashboard");

  document.getElementById("todayDate").textContent = fmtDate(new Date());
  liveClock("clock");

  await loadDashboard();
})();

async function loadDashboard() {
  const { ok, data } = await apiRequest("/dashboard");
  if (!ok) {
    showToast("Could not load dashboard data.");
    return;
  }

  // Today's intake
  document.getElementById("statIntake").innerHTML = `${data.taken} <span>/ ${data.total} taken</span>`;
  const pct = data.total ? Math.round((data.taken / data.total) * 100) : 0;
  document.getElementById("statIntakeBar").style.width = pct + "%";

  // Upcoming dose
  if (data.upcoming) {
    document.getElementById("statUpcoming").textContent = data.upcoming.medicine_name;
    document.getElementById("statUpcomingTime").textContent = data.upcoming.scheduled_time;
  } else {
    document.getElementById("statUpcoming").textContent = "All done";
    document.getElementById("statUpcomingTime").textContent = "No more doses today";
  }

  // Missed
  document.getElementById("statMissed").innerHTML = `${data.missed} <span>doses</span>`;
  const missedNote = document.getElementById("statMissedNote");
  if (data.missed > 0) {
    missedNote.textContent = "Please take your medicine soon";
    missedNote.className = "sub bad";
  } else {
    missedNote.textContent = "Perfect intake streak!";
    missedNote.className = "sub good";
  }

  // Active protocols
  document.getElementById("statActive").innerHTML = `${data.active_protocols} <span>prescriptions</span>`;
  document.getElementById("statActiveNote").textContent = `${data.total} directory records`;

  renderChecklist(data.checklist);
}

function renderChecklist(items) {
  const body = document.getElementById("checklistBody");
  if (!items.length) {
    body.innerHTML = `<div class="empty-state">No prescriptions yet. <br><a href="add_prescription.html" style="color:var(--teal-dark); font-weight:700;">Add your first prescription →</a></div>`;
    return;
  }

  body.innerHTML = items.map((item) => {
    const isDone = item.status === "taken" || item.status === "skipped";
    const statusTag = item.status !== "pending"
      ? `<span class="status-tag ${item.status}">${item.status}</span>`
      : "";
    return `
      <div class="med-row">
        <div class="med-info">
          <span class="name">${item.medicine_name}</span>
          <span class="dose">${item.dosage}</span><br>
          <span class="time">${item.scheduled_time}</span>
          ${statusTag}
        </div>
        <div class="med-actions">
          <button class="btn-sm btn-taken" ${isDone ? "disabled" : ""} onclick="markIntake(${item.log_id}, 'taken')">✓ Taken</button>
          <button class="btn-sm btn-skip" ${isDone ? "disabled" : ""} onclick="markIntake(${item.log_id}, 'skipped')">✕ Skip</button>
        </div>
      </div>
    `;
  }).join("");
}

async function markIntake(logId, status) {
  const { ok, data } = await apiRequest(`/intake/${logId}`, "POST", { status });
  if (ok) {
    showToast(data.message);
    await loadDashboard();
  } else {
    showToast("Could not update. Try again.");
  }
}

function quickAskSubmit() {
  const val = document.getElementById("quickAsk").value.trim();
  if (!val) return;
  sessionStorage.setItem("prefill_question", val);
  window.location.href = "ai_assistant.html";
}

document.getElementById("quickAsk")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") quickAskSubmit();
});
