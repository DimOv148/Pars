import requests
import json
from pprint import pprint


url = 'https://api.vk.com/method/groups.get'
params = {'user_id': '473582868',
         'extended': '1',
         'access_token': '50a78a9f080d9dafdd83b3227b3c6713a5a576162ffde207f2a4b60ac0609201836b75650d61d0145fb69',
         'v': '5.130'}

response = requests.get(url, params=params)

print(response.json())

for i in response.json()['response']['items']:
    print(i['name'])

with open('groups.json', 'w') as f:
    json.dump(response.json(), f)




