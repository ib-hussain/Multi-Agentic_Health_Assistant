// Config: change to your real endpoint when ready
const LOGIN_ENDPOINT = "/api/login"; // e.g. Flask/Streamlit route

const $ = (sel) => document.querySelector(sel);
const showError = (msg) => {
  const el = $("#form-error");
  if (!el) return;
  el.textContent = msg || "";
  el.style.display = msg ? "block" : "none";
};

// Password toggle
(() => {
  const toggle = $("#toggle-pass");
  const input = $("#password");
  if (toggle && input) {
    toggle.addEventListener("click", () => {
      const isPwd = input.type === "password";
      input.type = isPwd ? "text" : "password";
      toggle.textContent = isPwd ? "Hide" : "Show";
    });
  }
})();

// Remember me (stores just the name locally)
(() => {
  const nameEl = $("#name");
  const remember = $("#remember");
  if (!nameEl || !remember) return;

  // Load
  const saved = localStorage.getItem("vha_name");
  if (saved) {
    nameEl.value = saved;
    remember.checked = true;
  }

  function sync() {
    if (remember.checked && nameEl.value.trim()) {
      localStorage.setItem("vha_name", nameEl.value.trim());
    } else {
      localStorage.removeItem("vha_name");
    }
  }
  nameEl.addEventListener("input", sync);
  remember.addEventListener("change", sync);
})();

// Form submit
(() => {
  const form = $("#login-form");
  const nameEl = $("#name");
  const passEl = $("#password");
  const button = $("#login-btn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    showError("");

    const name = (nameEl?.value || "").trim();
    const password = passEl?.value || "";

    if (!name) return showError("Please enter your full name.");
    if (!password) return showError("Please enter your password.");

    // optimistic UI
    const old = button.textContent;
    button.disabled = true;
    button.textContent = "Signing in...";

    try {
      // If you don’t have an API yet, you can fake it:
      // await new Promise(r => setTimeout(r, 600));
      // const data = { status: "success", id: 1 };

      const res = await fetch(LOGIN_ENDPOINT, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ name, password })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      if (data.status === "success") {
        // Redirect to your app (change URL as you like)
        window.location.href = "home.html";
      } else {
        showError(data.message || "Invalid credentials.");
      }
    } catch (err) {
      console.error(err);
      showError("Network or server error. Please try again.");
    } finally {
      button.disabled = false;
      button.textContent = old;
    }
  });
})();
