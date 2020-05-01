import requests
import json
import time
import os

with open('parsed/match_id_list_all.json', 'r', encoding='utf8') as f:
    list_all_target_matches = json.load(f)
base_url = 'https://api.opendota.com/api/matches/{match_id}'

hea = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cache-control': 'max-age=0',
    'cookie': '_ga=GA1.2.1071066128.1581023833; __cfduid=d7eec77236a3415149d11fbc34ddb42eb1587059133',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}

flag_timeout = False
target_match_count = 0
for each_id in list_all_target_matches:
    if not os.path.exists(f'opendota/match/{each_id}.json'):
        target_match_count += 1
i = 0
for each_id in list_all_target_matches:
    # print(f'Get No. {i} / {len(list_all_target_matches)} ({i / len(list_all_target_matches) * 100:.2f}%): match_id = {each_id} -> ', end='')
    if os.path.exists(f'opendota/match/{each_id}.json'):
        # print('exist')
        continue
    i += 1
    print(f'Get No. {i} / {target_match_count} ({i / target_match_count * 100:.2f}%): match_id = {each_id} -> ', end='')
    url = base_url.format(match_id=each_id)
    try:
        res = requests.get(url, headers=hea, timeout=5)
        res.encoding='utf8'
    except:
        print('timeout')
        flag_timeout = True
        continue
    if res.status_code == 200:
        with open(f'opendota/match/{each_id}.json', 'w', encoding='utf8') as f:
            f.write(res.text)
        print('success')
    else:
        print('failed')
        flag_timeout = True
    time.sleep(1.5)

if flag_timeout:
    print('some requests are timeout')