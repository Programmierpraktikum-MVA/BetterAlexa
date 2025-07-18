// BetterAlexa – main.js (drop-in replacement, rich alert details)
// ------------------------------------------------------------------
// Shows *all* error information directly inside the browser alert
// dialog (HTTP status, response body, network/CORS details).
// ------------------------------------------------------------------

(() => {
  /* ──────────────── DOM references ──────────────── */
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

  /* ───────────── Helper: backend base URL ───────────── */
  const API_BASE = (() => {
    const { protocol, hostname } = window.location;
    if (["localhost", "127.0.0.1"].includes(hostname)) {
      return `${protocol}//${hostname}:8006`;          // dev
    }
    return `${protocol}//${hostname}`;                 // prod
  })();

  /* ──────────────── UI behaviour ──────────────── */
  loginBtn.addEventListener("click", () => {
    loginContainer.classList.add("hidden");
    settingsContainer.classList.remove("hidden");
  });

  paceSlider.addEventListener("input", () => {
    paceValue.textContent   = `${paceSlider.value}x`;
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

  /* ───────────── Persist settings to API ───────────── */
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

      /* ───── Handle HTTP-level errors ───── */
      if (!res.ok) {
        const copy = res.clone();            // we might need body twice
        let body;
        try { body = await copy.json(); }    // attempt JSON first
        catch { body = await copy.text(); }

        const bodyText = typeof body === "string" ? body
                         : JSON.stringify(body, null, 2);

        console.error(
          `API error: ${res.status} ${res.statusText}`,
          "Response body:", body,
          "Payload sent:", payload,
        );

        alert(`HTTP-Fehler ${res.status} ${res.statusText}\n` +
              `Antwort-Body:\n${bodyText}`);
        return;
      }

      /* ───── Success ───── */
      console.info("Einstellungen gespeichert:", payload);
      alert("Einstellungen erfolgreich gespeichert.");

    } catch (err) {
      /* ───── Network / CORS / unexpected errors ───── */
      console.error("Network/CORS error while sending:", err);
      if (err.stack) console.error(err.stack);

      alert(`Verbindung zum Server fehlgeschlagen:\n` +
            `${err.name}: ${err.message}` +
            (err.stack ? `\nStack-Trace:\n${err.stack}` : ""));
    }
  });

  /* ───────────── Misc. helpers ───────────── */
  function collectSettings() {
    const data = {};
    settingsContainer.querySelectorAll("input, select, textarea")
      .forEach((el) => {
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

  /* ───── Download settings to a file (optional) ───── */
  function downloadSettings(settings) {
    const blob = new Blob([JSON.stringify(settings, null, 2)], { type: "application/json" });
    const url  = URL.createObjectURL(blob);
    const a    = Object.assign(document.createElement("a"), {
      href: url,
      download: "einstellungen.json",
    });
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      URL.revokeObjectURL(url);
      a.remove();
    }, 100);
  }

  // initial slider labels
  paceValue.textContent   = `${paceSlider.value}x`;
  volumeValue.textContent = `${volumeSlider.value}%`;
})();