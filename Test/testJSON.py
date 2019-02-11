#!/usr/bin/python
import json

dataPath = '../../Data/JsonSample2.json'
with open(dataPath, 'r') as f:
    temp = json.loads(f.read())
    print(temp['messages'][1]['body'])