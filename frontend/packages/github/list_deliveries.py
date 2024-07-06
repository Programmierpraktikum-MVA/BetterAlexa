import requests
import sys
from pprint import pprint

if len(sys.argv) > 1:
    jwt = sys.argv[1]
else:
    jwt = input("Enter JWT token: ")

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {jwt}',
    'X-GitHub-Api-Version': '2022-11-28',
}

response = requests.get('https://api.github.com/app/hook/deliveries', headers=headers)
print(pprint(response.json()))