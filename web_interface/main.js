// BetterAlexa – main.js (drop‑in replacement)
// -------------------------------------------------
// Frontend logic + dynamic backend URL selection so that the same file works
// locally (http://localhost:8006) **and** in production (https://betteraIexa.adastruct.com).
// -------------------------------------------------

(() => {
  /* ─────────────────────────── DOM references ─────────────────────────── */
  const loginContainer   = document.getElementById("loginContainer");
  const settingsContainer= document.getElementById("settingsContainer");
  const loginBtn         = document.getElementById("loginBtn");
  const paceSlider       = document.getElementById("pace");
  const volumeSlider     = document.getElementById("volume");
  const paceValue        = document.getElementById("paceValue");
  const volumeValue      = document.getElementById("volumeValue");
  const saveBtn          = document.getElementById("saveBtn");
  const spotifyEnabled   = document.getElementById("spotifyEnabled");
  const spotifyUser      = document.getElementById("spotifyUser");
  const spotifyPass      = document.getElementById("spotifyPass");

  /* ──────────────────── Helper: backend base URL ──────────────────────── */
  const API_BASE = (() => {
    const { protocol, hostname } = window.location;
    // If we are running on localhost *or* 127.0.0.1 we assume the FastAPI dev
    // server is still listening on port 8006.
    if (["localhost", "127.0.0.1"].includes(hostname)) {
      return `${protocol}//${hostname}:8006`;
    }
    // Otherwise use exactly the same origin that served the frontend.
    return `${protocol}//${hostname}`;         // e.g. https://betteraIexa.adastruct.com
  })();

  /* ─────────────────────────── UI behaviour ───────────────────────────── */
  loginBtn.addEventListener("click", () => {
    loginContainer.classList.add("hidden");
    settingsContainer.classList.remove("hidden");
  });

  paceSlider.addEventListener("input", () => {
    paceValue.textContent = `${paceSlider.value}x`;
  });
  volumeSlider.addEventListener("input", () => {
    volumeValue.textContent = `${volumeSlider.value}%`;
  });

  spotifyEnabled.addEventListener("change", () => {
    toggleVisibility(spotifyUser, spotifyEnabled.checked);
    toggleVisibility(spotifyPass, spotifyEnabled.checked);
  });

  function toggleVisibility(el, show) {
    el.classList[show ? "remove" : "add"]("hidden");
  }

  /* ────────────────────── Persist settings to API ─────────────────────── */
  saveBtn.addEventListener("click", async () => {
    const settings = collectSettings();
    const user_id  = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!user_id || !password) {
      alert("Bitte Benutzername und Passwort eingeben.");
      return;
    }

    const payload = { user_id, password, settings };

    try {
      const res = await fetch(`${API_BASE}/save-settings`, {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify(payload),
      });

      if (res.ok) {
        alert("Einstellungen erfolgreich gespeichert.");
      } else {
        const { detail } = await res.json();
        alert(`Fehler: ${detail}`);
      }
    } catch (err) {
      console.error("Fehler beim Senden:", err);
      alert("Verbindung zum Server fehlgeschlagen.");
    }
  });

  /* ───────────────────────── Misc. helpers ────────────────────────────── */
  function collectSettings() {
    const data = {};
    settingsContainer.querySelectorAll("input, select, textarea").forEach((el) => {
      const { name, type, value, checked } = el;
      if (!name) return;
      if (type === "checkbox" || type === "radio") {
        data[name] = checked ? value : "false";
      } else if (type === "range") {
        data[name] = parseFloat(value);
      } else {
        data[name] = value;
      }
    });
    return data;
  }

  // optional: download settings as JSON (still available for future use)
  function downloadSettings(settings) {
    const blob = new Blob([JSON.stringify(settings, null, 2)], { type: "application/json" });
    const url  = URL.createObjectURL(blob);
    const a    = Object.assign(document.createElement("a"), { href: url, download: "einstellungen.json" });
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      URL.revokeObjectURL(url);
      a.remove();
    }, 100);
  }

  // Initial slider labels
  paceValue.textContent   = `${paceSlider.value}x`;
  volumeValue.textContent = `${volumeSlider.value}%`;
})();
