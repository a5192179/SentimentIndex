#!/usr/bin/python
import json
import urllib.request

response = urllib.request.urlopen('https://api.stocktwits.com/api/2/streams/symbol/BTC.X.json')
# html = response.read()
temp = json.loads(response.read())
print(len(temp['messages']))
for body in temp['messages']:
    print(body['body'])
