import requests
import sys
from pprint import pprint

if len(sys.argv) > 1:
    jwt = sys.argv[1]
else:
    jwt = input("Enter JWT token: ")

if len(sys.argv) > 2:
    delivery_id = sys.argv[2]
else:
    delivery_id = input("Enter delivery id: ")

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {jwt}',
    'X-GitHub-Api-Version': '2022-11-28',
}

response = requests.post(f'https://api.github.com/app/hook/deliveries/{delivery_id}/attempts', headers=headers)
print(pprint(response.json()))