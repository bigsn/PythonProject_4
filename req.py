# curl -X 'POST' \
#   'http://127.0.0.1:8000/api/sources/' \
#   -H 'accept: */*' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "type": "site",
#   "name": "string",
#   "url": "https://habr.com/ru/",
#   "enabled": true
# }'

import requests

url = "http://127.0.0.1:8000/api/sources/"

response = requests.get(url)

if response.status_code == 200:
    print(response.json())