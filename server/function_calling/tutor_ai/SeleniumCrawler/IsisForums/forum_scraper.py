from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from get_all_forum_id import get_all_forum_id


# Note that this file is preliminary.
# Eventually, we will run all scraper files with one scraper.py

with open('../config.json') as config_file:
    config_data = json.load(config_file)

# Extract username and password from config data
USERNAME_TOKEN = config_data['username']
PASSWORD_TOKEN = config_data['password']

driver = webdriver.Chrome()

driver.get("https://isis.tu-berlin.de/login/index.php")

title = driver.title

driver.implicitly_wait(0.5)

tu_login_button = driver.find_element(by=By.ID, value="shibbolethbutton")
tu_login_button.click()

title_new = driver.title
print(title_new)
username_login = driver.find_element(by=By.ID, value="username")
password_login = driver.find_element(by=By.ID, value="password")

username_login.send_keys(USERNAME_TOKEN)
password_login.send_keys(PASSWORD_TOKEN)

final_login_button = driver.find_element(by=By.ID, value="login-button")
final_login_button.click()

title_second = driver.title

get_all_forum_id(driver)