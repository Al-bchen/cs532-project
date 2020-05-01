import json
import os
from pymongo import MongoClient

# connect MongoDB as client
client = MongoClient('localhost', 27017)

# use database
db = client['project']

# Need to create collections before insert

collection = db['heroes']

with open('opendota/heroes.json') as f:
    data = json.load(f)

for each in data:
    each['hero_id'] = each['id']
    del each['id']

try:
    collection.delete_many({})
    collection.insert_many(data)
except:
    pass

# import leagues
collection = db['leagues']

with open('parsed/target_leagues.json') as f:
    data = json.load(f)

try:
    collection.delete_many({})
    collection.insert_many(data)
except:
    pass

# exit(0)

# import matches
collection = db['matches']
try:
    collection.delete_many({})
    for i, filename in enumerate(os.listdir('opendota/match')):
        with open(f'opendota/match/{filename}', encoding='utf8') as f:
            data = json.load(f)
        collection.insert_one(data)
        if i % 100 == 0:
            print(f'match {i}')
except:
    pass
client.close()