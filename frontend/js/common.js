/* common.js - shared helpers used by every page */

const API_BASE = "https://prescriptai-backend.onrender.com/api";

/** Generic fetch wrapper that always sends session cookies */
async function apiRequest(path, method = "GET", body = null) {
  const options = {
    method,
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  };
  if (body) options.body = JSON.stringify(body);
  try {
    const res = await fetch(`${API_BASE}${path}`, options);
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    console.error("Network/CORS error calling API:", err);
    return { ok: false, status: 0, data: { success: false, message: "Cannot reach the server. Is the backend running on port 5000?" } };
  }
}

/** Small bottom-right toast notification */
function showToast(message) {
  let toast = document.getElementById("global-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "global-toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toast._hideTimer);
  toast._hideTimer = setTimeout(() => toast.classList.remove("show"), 2800);
}

/** Redirects to login if the user has no active session. Returns the user name if logged in. */
async function requireAuth() {
  const { data } = await apiRequest("/me");
  if (!data.authenticated) {
    window.location.href = "login.html";
    return null;
  }
  return data.name;
}

function initials(name) {
  if (!name) return "?";
  return name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

/** Fills the sidebar's user block + highlights the active nav link */
function paintSidebar(userName, activePage) {
  document.querySelectorAll("[data-user-name]").forEach((el) => {
    el.textContent = userName || "User";
  });
  const avatarEl = document.querySelector("[data-user-avatar]");
  if (avatarEl) avatarEl.textContent = initials(userName);

  document.querySelectorAll(".nav-item[data-page]").forEach((el) => {
    el.classList.toggle("active", el.dataset.page === activePage);
  });
}

async function logout() {
  await apiRequest("/logout", "POST");
  window.location.href = "login.html";
}

function fmtDate(d) {
  const opts = { weekday: "short", month: "short", day: "numeric", year: "numeric" };
  return new Date(d).toLocaleDateString(undefined, opts);
}

function liveClock(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  const tick = () => {
    el.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  };
  tick();
  setInterval(tick, 1000);
}
