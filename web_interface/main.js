 // DOM-Elemente
        const loginContainer = document.getElementById('loginContainer');
        const settingsContainer = document.getElementById('settingsContainer');
        const loginBtn = document.getElementById('loginBtn');
        const paceSlider = document.getElementById('pace');
        const volumeSlider = document.getElementById('volume');
        const paceValue = document.getElementById('paceValue');
        const volumeValue = document.getElementById('volumeValue');
        const saveBtn = document.getElementById('saveBtn');
        const spotifyEnabled = document.getElementById('spotifyEnabled');
        const spotifyUser = document.getElementById('spotifyUser');
        const spotifyPass = document.getElementById('spotifyPass');

        // Anmeldung simulieren
        loginBtn.addEventListener('click', () => {
            loginContainer.classList.add('hidden');
            settingsContainer.classList.remove('hidden');
        });

        // Slider-Werte aktualisieren
        paceSlider.addEventListener('input', () => {
            paceValue.textContent = `${paceSlider.value}x`;
        });

        volumeSlider.addEventListener('input', () => {
            volumeValue.textContent = `${volumeSlider.value}%`;
        });

        // Spotify Integration anzeigen/verstecken
        spotifyEnabled.addEventListener('change', () => {
            if(spotifyEnabled.checked) {
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
            const response = await fetch("http://localhost:8006/save-settings", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
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

        // Alle Einstellungen sammeln
        function collectSettings() {
            const settings = {};
            
            // Alle Eingabeelemente im Einstellungsbereich finden
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

        // Einstellungen als JSON-Datei herunterladen
        function downloadSettings(settings) {
            const json = JSON.stringify(settings, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = 'einstellungen.json';
            document.body.appendChild(a);
            a.click();
            
            // Aufräumen
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);
        }

        // Initiale Werte setzen
        paceValue.textContent = `${paceSlider.value}x`;
        volumeValue.textContent = `${volumeSlider.value}%`;