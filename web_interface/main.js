document.addEventListener('DOMContentLoaded', () => {
  // Server-URL
const SERVER_URL = "https://betteralexa.adastruct.com";

// DOM-Elemente Allgemein
const loginContainer = document.getElementById('loginContainer');
const registerContainer = document.getElementById('registerContainer');
const settingsContainer = document.getElementById('settingsContainer');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const showRegisterLink = document.getElementById('showRegister');
const showLoginLink = document.getElementById('showLogin');

// Settings-Elemente
const paceSlider = document.getElementById('pace');
const paceValue = document.getElementById('paceValue');
const saveBtn = document.getElementById('saveBtn');
const spotifyEnabled = document.getElementById('spotifyEnabled');
const spotifyUser = document.getElementById('spotifyUser');
const spotifyPass = document.getElementById('spotifyPass');

// Anzeigewechsel Login / Registrierung
showRegisterLink.addEventListener('click', () => {
    loginContainer.classList.add('hidden');
    registerContainer.classList.remove('hidden');
});

showLoginLink.addEventListener('click', () => {
    registerContainer.classList.add('hidden');
    loginContainer.classList.remove('hidden');
});

// Login-Funktion
loginBtn.addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showError("Bitte Benutzername und Passwort eingeben");
        return;
    }

    try {
        const response = await fetch(`${SERVER_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: username, password: password })
        });

        if (response.ok) {
            loginContainer.classList.add('hidden');
            settingsContainer.classList.remove('hidden');
        } else {
            const errorData = await response.json();
            showError(errorData.detail || "Anmeldung fehlgeschlagen");
        }
    } catch (err) {
        console.error("Fehler bei der Anmeldung:", err);
        showError("Verbindung zum Server fehlgeschlagen");
    }
});

// Registrierung
registerBtn.addEventListener('click', async () => {
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    const passwordConfirm = document.getElementById('regPasswordConfirm').value;

    if (!username || !password || !passwordConfirm) {
        showError("Bitte alle Felder ausfüllen", registerContainer);
        return;
    }

    if (password !== passwordConfirm) {
        showError("Passwörter stimmen nicht überein", registerContainer);
        return;
    }

    if (password.length < 6) {
        showError("Passwort muss mindestens 6 Zeichen haben", registerContainer);
        return;
    }

    try {
        const response = await fetch(`${SERVER_URL}/create-user`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: username, password: password })
        });

        if (response.ok) {
            alert("Registrierung erfolgreich! Bitte anmelden.");
            registerContainer.classList.add('hidden');
            loginContainer.classList.remove('hidden');
        } else {
            const errorData = await response.json();
            showError(errorData.detail || "Registrierung fehlgeschlagen", registerContainer);
        }
    } catch (err) {
        console.error("Fehler bei der Registrierung:", err);
        showError("Verbindung zum Server fehlgeschlagen", registerContainer);
    }
});

// Einstellungen Slider-Werte aktualisieren
paceSlider.addEventListener('input', () => {
    paceValue.textContent = `${paceSlider.value}x`;
});

// Spotify Integration anzeigen/verstecken
spotifyEnabled.addEventListener('change', () => {
    console.log("Spotify Checkbox changed:", spotifyEnabled.checked);

    if (spotifyEnabled.checked) {
        spotifyUser.classList.remove('hidden');
        spotifyPass.classList.remove('hidden');
    } else {
        spotifyUser.classList.add('hidden');
        spotifyPass.classList.add('hidden');
    }
});

// Einstellungen speichern
saveBtn.addEventListener('click', async () => {
    const settings = collectSettings();

    const user_id = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!user_id || !password) {
        alert("Bitte Benutzername und Passwort eingeben.");
        return;
    }

    const payload = {
        user_id: user_id,
        password: password,
        settings: settings
    };

    try {
        const response = await fetch(`${SERVER_URL}/save-settings`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Einstellungen erfolgreich gespeichert.");
        } else {
            const error = await response.json();
            alert("Fehler: " + error.detail);
        }
    } catch (err) {
        console.error("Fehler beim Senden:", err);
        alert("Verbindung zum Server fehlgeschlagen.");
    }
});

// Hilfsfunktion zum Einsammeln der Settings
function collectSettings() {
    const settings = {};
    const inputs = settingsContainer.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        const key = input.name;
        if (!key) return;

        if (input.type === 'checkbox' || input.type === 'radio') {
            settings[key] = input.checked ? input.value : 'false';
        } else if (input.type === 'range') {
            settings[key] = parseFloat(input.value);
        } else {
            settings[key] = input.value;
        }
    });

    return settings;
}

// Fehlermeldung anzeigen
function showError(message, container = null) {
    const oldErrors = container
        ? container.querySelectorAll('.error-message')
        : document.querySelectorAll('.error-message');

    oldErrors.forEach(error => error.remove());

    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    errorElement.style.display = 'block';

    if (container) {
        container.querySelector('.card').appendChild(errorElement);
    } else {
        document.querySelector('.card').appendChild(errorElement);
    }

    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}

// Initiale Werte setzen
paceValue.textContent = `${paceSlider.value}x`;
});