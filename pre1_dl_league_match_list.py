# -*- coding: utf-8 -*-
import requests

res = requests.get('https://www.datdota.com/api/matches?tier=premium')

with open('datdota/matches_premium.json', 'w', encoding='utf8') as f:
    f.write(res.text)

res = requests.get('https://www.datdota.com/api/matches?tier=all')

with open('datdota/matches_all.json', 'w', encoding='utf8') as f:
    f.write(res.text)
