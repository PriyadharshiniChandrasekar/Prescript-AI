/* auth.js - login + register form handlers */

function showFormError(message) {
  const box = document.getElementById("errorBox");
  if (!box) return;
  box.textContent = message;
  box.classList.add("show");
}

const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("loginBtn");
    btn.disabled = true;
    btn.textContent = "Logging in...";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const { ok, data } = await apiRequest("/login", "POST", { email, password });

    if (ok && data.success) {
      window.location.href = "dashboard.html";
    } else {
      showFormError(data.message || "Login failed. Please try again.");
      btn.disabled = false;
      btn.textContent = "Log In";
    }
  });
}

const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("registerBtn");
    btn.disabled = true;
    btn.textContent = "Creating account...";

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const { ok, data } = await apiRequest("/register", "POST", { name, email, password });

    if (ok && data.success) {
      window.location.href = "dashboard.html";
    } else {
      showFormError(data.message || "Registration failed. Please try again.");
      btn.disabled = false;
      btn.textContent = "Create Account";
    }
  });
}
