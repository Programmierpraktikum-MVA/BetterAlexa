from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  
import requests
import subprocess
import os
import json 

def extract_audio(local_video_path, output_file):
    try:
        ffmpeg_command = f'ffmpeg -i "{local_video_path}" -vn -acodec libmp3lame -y "{output_file}"'
        subprocess.call(ffmpeg_command, shell=True)
        os.remove(local_video_path)  # Delete the .mp4 file after conversion
    except Exception as e:
        print(f"Error during audio extraction: {e}")

def setup_session_with_cookies(driver):
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    return session

def sanitize_filename(name):
    import re
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_and_extract_audio(session, video_url, lecture_name, output_index, page_link, processed_urls):
    if video_url in processed_urls:
        print(f"Skipping duplicate video URL: {video_url}")
        return
    processed_urls.add(video_url)
    safe_lecture_name = sanitize_filename(lecture_name)
    local_video_path = f'{safe_lecture_name}_{output_index}.mp4'
    output_file = f'{safe_lecture_name}_{output_index}.mp3'
    response = session.get(video_url, stream=True)
    if response.status_code == 200:
        with open(local_video_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        extract_audio(local_video_path, output_file)
        log_entry(output_file, page_link)
        print(f'Audio extracted and saved as {output_file}')
    else:
        print(f"Failed to download video from {video_url}, Response Code = {response.status_code}")

def log_entry(title, link):
    entry = {"Title": title, "Link": link}
    try:
        with open('download_log.json', 'r+') as log_file:
            log_data = json.load(log_file)
            log_data.append(entry)
            log_file.seek(0)
            json.dump(log_data, log_file, indent=4)
    except FileNotFoundError:
        with open('download_log.json', 'w') as log_file:
            json.dump([entry], log_file, indent=4)

def scrape_and_extract_audio(start_url):
    chrome_options = Options()
    chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    chrome_options.add_argument("webdriver.chrome.driver=C:\\Users\\user\\Desktop\\ChromiumDriver\\chromedriver.exe")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(start_url)
    input("Press Enter to continue...")
    processed_urls = set()

    try:
        session = setup_session_with_cookies(driver)
        links = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='mod/videoservice/view.php/cm']")))
        hrefs = [link.get_attribute('href') for link in links]

        for href in hrefs:
            driver.get(href)
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3[data-v-f62d1a84]")))
                lecture_title_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h3[data-v-f62d1a84]")))
                lecture_name = lecture_title_element.text.strip().replace(' - ', '_').replace(' ', '_')
                video_elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "video")))
                for i, video_element in enumerate(video_elements):
                    video_source_url = video_element.get_attribute('src')
                    if video_source_url:
                        download_and_extract_audio(session, video_source_url, lecture_name, i+1, href, processed_urls)
            except TimeoutException:
                print(f"Timeout or element not found on page {href}.")
    finally:
        driver.quit()

scrape_and_extract_audio("https://isis.tu-berlin.de/mod/videoservice/view.php/course/38479/browse")