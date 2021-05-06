import requests
import json
from pprint import pprint

url = 'https://api.github.com'
user = 'DimOv148'

r = requests.get(f'{url}/users/{user}/repos')
with open('repos.json', 'w') as f:
    json.dump(r.json(), f)

for i in r.json():
    print(i['name'])


