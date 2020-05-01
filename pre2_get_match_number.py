# -*- coding: utf-8 -*-
import requests
import json
import re

with open('datdota/matches_premium.json', 'r', encoding='utf8') as f:
    data = json.load(f)

with open('datdota/matches_pretty_print.json', 'w', encoding='utf8') as f:
    f.write(json.dumps(data, indent=4, sort_keys=True))
data: list = data["data"]

target_leagues = [
    {"leagueid": 10452, "name": "The Bucharest Minor",  "winner": "EHOME"},
    {"leagueid": 10482, "name": "The Chongqing Major",  "winner": "Team Secret"},

    {"leagueid": 10733, "name": "StarLadder ImbaTV Dota2 Minor",  "winner": "Vici Gaming"},
    {"leagueid": 10681, "name": "DreamLeague Season 11",  "winner": "Vici Gaming"},

    {"leagueid": 10869, "name": "OGA Dota PIT Minor 2019",  "winner": "Ninjas in Pyjamas"},
    {"leagueid": 10810, "name": "MDL Disneyland® Paris Major",  "winner": "Team Secret"},

    {"leagueid": 10979, "name": "StarLadder ImbaTV Dota 2 Minor Season 2",  "winner": "Ninjas in Pyjamas"},
    {"leagueid": 10826, "name": "EPICENTER Major 2019", "winner": "Vici Gaming"},

    {"leagueid": 10749, "name": "The International 2019",  "winner": "OG"},

    {"leagueid": 11371, "name": "Dota Summit 11", "winner": "INVICTUS GAMING"},
    {"leagueid": 11280, "name": "MDL Chengdu Major", "winner": "TNC Predator"},

    {"leagueid": 11490, "name": "WePlay! Bukovel Minor 2020", "winner": "Nigma"},
    {"leagueid": 11517, "name": "Dreamleague Season 13", "winner": "Team Secret"},

    {"leagueid": 11661, "name": "DPC 2019/2020 Qualifier #3", "winner": "None"},
    {"leagueid": 11823, "name": "ESL One LA 2020 Online League", "winner": "None"},
]
order_num = 1
for each in target_leagues:
    each.update({'order': order_num})
    order_num += 1

print(json.dumps(target_leagues, indent=4, sort_keys=True))

with open('parsed/target_leagues.json', 'w', encoding='utf8') as f:
    f.write(json.dumps(target_leagues, indent=4, sort_keys=True))


with open('parsed/target_leagues.json', 'r', encoding='utf8') as f:
    target_leagues = json.load(f)

# get all target league matches
list_all_target_matches = []
for each_league in target_leagues:
    list_target_matches = []
    for each_data in data:
        if each_data['league']['leagueId'] == each_league['leagueid']:
            list_target_matches.append(each_data['matchId'])
            list_all_target_matches.append(each_data['matchId'])
    print(each_league['leagueid'], len(list_target_matches))

print(len(list_all_target_matches))
with open("parsed/match_id_list_all.json", 'w', encoding='utf8') as f:
    f.write(str(list_all_target_matches))
