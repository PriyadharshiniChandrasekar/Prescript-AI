/* ai_assistant.js */

(async function init() {
  const name = await requireAuth();
  if (!name) return;
  paintSidebar(name, "ai");

  await loadHistory();

  const prefill = sessionStorage.getItem("prefill_question");
  if (prefill) {
    document.getElementById("chatInput").value = prefill;
    sessionStorage.removeItem("prefill_question");
  }
})();

async function loadHistory() {
  const { ok, data } = await apiRequest("/chat/history");
  if (!ok || !data.history || !data.history.length) return;

  const body = document.getElementById("chatBody");
  body.innerHTML = data.history.map((m) => `<div class="msg ${m.role}">${escapeHtml(m.message)}</div>`).join("");
  scrollChatToBottom();
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function scrollChatToBottom() {
  const body = document.getElementById("chatBody");
  body.scrollTop = body.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  const body = document.getElementById("chatBody");
  body.insertAdjacentHTML("beforeend", `<div class="msg user">${escapeHtml(message)}</div>`);
  input.value = "";
  scrollChatToBottom();

  const typingId = "typing-" + Date.now();
  body.insertAdjacentHTML("beforeend", `<div class="msg assistant typing" id="${typingId}">Aura is typing...</div>`);
  scrollChatToBottom();

  const { ok, data } = await apiRequest("/chat", "POST", { message });

  document.getElementById(typingId)?.remove();

  if (ok) {
    body.insertAdjacentHTML("beforeend", `<div class="msg assistant">${escapeHtml(data.reply)}</div>`);
  } else {
    body.insertAdjacentHTML("beforeend", `<div class="msg assistant">Sorry, something went wrong. Please try again.</div>`);
  }
  scrollChatToBottom();
}

document.getElementById("chatInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
