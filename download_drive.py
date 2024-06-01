import requests
from bs4 import BeautifulSoup
import os

def download_file_from_google_drive(file_id, file_name, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()
    
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    if is_html_response(response):
        download_link = get_download_link_from_html(response)
        if download_link:
            response = session.get(download_link, stream = True)

    save_response_content(response, destination, file_name)    

def get_confirm_token(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    token = None
    for input_tag in soup.find_all('input'):
        if input_tag.get('name') == 'confirm':
            token = input_tag.get('value')
            break
    return token


def is_html_response(response):
    return 'html' in response.headers.get('Content-Type', '')

def get_download_link_from_html(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', {'id': 'download-form'})
    if form:
        action = form['action']
        params = {input_tag['name']: input_tag['value'] for input_tag in form.find_all('input') if input_tag.get('name')}
        download_link = requests.Request('GET', action, params=params).prepare().url
        return download_link
    return None

def save_response_content(response, destination, file_name):
    CHUNK_SIZE = 32768
    file_path = os.path.join(destination, file_name)
    
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

def get_files_from_folder(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    files = []
    # Find all divs with the attribute 'data-id'
    for div in soup.find_all('div', attrs={'data-id': True}):
        file_id = div['data-id']
        # Extract file name from the div with class 'KL4NAf' and attribute 'aria-label'
        name_tag = div.find('div', {'class': 'KL4NAf'})
        file_name = name_tag['aria-label'] if name_tag and 'aria-label' in name_tag.attrs else f"{file_id}.file"
        file_name = file_name.split(": ", 1)[1]
        files.append((file_id, file_name))
    
    return files

def download_google_drive_folder(folder_url, local_path='downloads'):
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    files = get_files_from_folder(folder_url)
    
    for file_id, file_name in files:
        download_file_from_google_drive(file_id, file_name, local_path)
        print(f"Downloaded: {file_name}")
