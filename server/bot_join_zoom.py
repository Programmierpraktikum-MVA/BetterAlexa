import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



if len(sys.argv) < 2:
    print("Usage: python bot_join_zoom.py <zoom_web_link>")
    sys.exit(1)

zoom_url = sys.argv[1]

# Chrome-Optionen
options = Options()
options.add_argument("--use-fake-ui-for-media-stream")  # Automatischer Audiozugriff
options.add_argument("--start-maximized")

# Browser starten
driver = webdriver.Chrome(options=options)
driver.get(zoom_url)

print("Zoom-Link geöffnet.")
time.sleep(10)

# Versuche auf „Agree“ oder „Accept“ zu klicken, falls vorhanden
try:
    # Beispiel: Button mit Text "Agree"
    agree_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept Cookies')]")
    agree_button.click()
    print("Accept-Cookies-Button geklickt.")
    time.sleep(2)  # kurz warten nach dem Klick
except:
    print("KeinAccept-Cookies-Button gefunden.")


time.sleep(10)

# Versuche auf „Agree“ oder „Accept“ zu klicken, falls vorhanden
try:
    # Beispiel: Button mit Text "Agree"
    agree_button = driver.find_element(By.XPATH, "//button[contains(text(), 'I Agree')]")
    agree_button.click()
    print("Agree-Button geklickt.")
    time.sleep(2)  # kurz warten nach dem Klick
except:
    print("Kein Agree-Button gefunden.")
    
time.sleep(10)

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Warten, bis iframe erscheint, und dann wechseln
try:
    wait = WebDriverWait(driver, 15)
    iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    driver.switch_to.frame(iframe)
    print("In das iframe gewechselt.")
except:
    print("Kein iframe gefunden.")

# Dann wie gewohnt Namensfeld finden und ausfüllen
try:
    name_input = wait.until(EC.element_to_be_clickable((By.ID, "input-for-name")))
    name_input.clear()
    name_input.send_keys("ZoomBot")

    join_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join')]")
    join_button.click()
    print("Name eingegeben und Beitritt geklickt.")
except Exception as e:
    print("Fehler beim Eingeben des Namens oder kein Feld gefunden:", e)


time.sleep(10)

try:
    # „Mit Computer-Audio beitreten“ klicken
    audio_button = driver.find_element(By.CLASS_NAME, "join-audio-container__btn")
    audio_button.click()
    print("Audio beigetreten.")
except:
    print("Audio-Button nicht gefunden oder automatisch aktiviert.")

# Warten, solange Meeting läuft
print("Meeting läuft. Drücke STRG+C zum Beenden.")
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    driver.quit()
    print("Beendet.")

