/* add_prescription.js */

let times = [];

(async function init() {
  const name = await requireAuth();
  if (!name) return;
  paintSidebar(name, "add");
  document.getElementById("startDate").valueAsDate = new Date();
})();

function addTime() {
  const input = document.getElementById("newTime");
  if (!input.value) return;
  if (!times.includes(input.value)) {
    times.push(input.value);
    times.sort();
    renderTimes();
  }
  input.value = "";
}

function removeTime(t) {
  times = times.filter((x) => x !== t);
  renderTimes();
}

function renderTimes() {
  const box = document.getElementById("timesBox");
  box.innerHTML = times.map((t) => `
    <div class="time-chip">${t} <button type="button" onclick="removeTime('${t}')">×</button></div>
  `).join("") || `<span style="color:var(--muted); font-size:13px;">No times added yet</span>`;
}

document.getElementById("prescriptionForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  if (times.length === 0) {
    showToast("Please add at least one reminder time.");
    return;
  }

  const btn = document.getElementById("submitBtn");
  btn.disabled = true;
  btn.textContent = "Analyzing with Aura AI...";

  const payload = {
    medicine_name: document.getElementById("medicineName").value.trim(),
    dosage: document.getElementById("dosage").value.trim(),
    frequency: document.getElementById("frequency").value,
    times,
    start_date: document.getElementById("startDate").value,
    end_date: document.getElementById("endDate").value || null,
    notes: document.getElementById("notes").value.trim(),
  };

  const { ok, data } = await apiRequest("/prescriptions", "POST", payload);

  btn.disabled = false;
  btn.textContent = "✨ Save & Analyze with AI";

  if (!ok) {
    showToast(data.message || "Could not save prescription.");
    return;
  }

  showToast("Prescription saved successfully!");
  renderAiSummary(data.ai_summary);
  document.getElementById("prescriptionForm").reset();
  times = [];
  renderTimes();
  document.getElementById("startDate").valueAsDate = new Date();
});

function renderAiSummary(summary) {
  const container = document.getElementById("aiSummaryContainer");
  if (!summary) {
    container.innerHTML = "";
    return;
  }
  const sideEffects = (summary.common_side_effects || []).map((s) => `<li>${s}</li>`).join("");
  const precautions = (summary.precautions || []).map((s) => `<li>${s}</li>`).join("");

  container.innerHTML = `
    <div class="ai-summary-box">
      <h4>✨ Aura's AI Analysis</h4>
      <div class="row"><b>Used for:</b> ${summary.used_for || "N/A"}</div>
      <div class="row"><b>Common side effects:</b><ul>${sideEffects || "<li>None reported</li>"}</ul></div>
      <div class="row"><b>Precautions:</b><ul>${precautions || "<li>None specific</li>"}</ul></div>
      <div class="row"><b>Food interaction:</b> ${summary.food_interaction || "N/A"}</div>
    </div>
  `;
}
