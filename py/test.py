import os.path
from os import path

import requests
import numpy as np
import pandas as pd
import json
import time
import math


# API default setting.
apiDefault = {
    'region': 'https://kr.api.riotgames.com',  # kr server.
    # API KEY - from riot developers portal.
    'key': 'RGAPI-eb942e87-72c2-4af4-b289-8125e318da98',
    'summonerName': 'PROvbs',  # default with my nickname.
}


array_player_gold_timeline = []
array_team_gold_timeline = []
array_oppo_gold_timeline = []

array_player_damage_dealth_timeline = []
array_team_damage_dealth_timeline = []
array_oppo_damage_dealth_timeline = []

array_player_minion_timeline = []
array_level_timeline = []

try:
    url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/{'KR_5583104229'}/timeline?api_key={apiDefault['key']}"
    req = requests.get(url)
    match_info_timeline = json.loads(req.text)

    timeline_length = len(match_info_timeline['info']['frames'])
    player_number = 1

    # player/team/oppo gold total + player level changes.
    for i in range(0, timeline_length):
        team_gold = 0
        oppo_gold = 0
        player_gold = match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['totalGold']
        player_level = match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['level']
        player_damage_dealth = match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['damageStats']['totalDamageDoneToChampions']

        team_damage_dealth = 0
        oppo_damage_dealth = 0
        player_minion = match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['minionsKilled'] + \
            match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['jungleMinionsKilled']

        for j in range(1, 6):
            team_gold = team_gold + \
                match_info_timeline['info']['frames'][i]['participantFrames'][str(j)]['totalGold']
            team_damage_dealth = team_damage_dealth + \
                match_info_timeline['info']['frames'][i]['participantFrames'][str(j)]['damageStats']['totalDamageDoneToChampions']

        for k in range(6, 11):
            oppo_gold = oppo_gold + \
                match_info_timeline['info']['frames'][i]['participantFrames'][str(k)]['totalGold']
            oppo_damage_dealth = oppo_damage_dealth + \
                match_info_timeline['info']['frames'][i]['participantFrames'][str(k)]['damageStats']['totalDamageDoneToChampions']

        team_damage_dealth_avg = round(team_damage_dealth / 5)
        oppo_damage_dealth_avg = round(oppo_damage_dealth / 5)

        array_team_gold_timeline.append(team_gold)
        array_oppo_gold_timeline.append(oppo_gold)
        array_player_gold_timeline.append(player_gold)
        array_level_timeline.append(player_level)

        array_player_damage_dealth_timeline.append(player_damage_dealth)
        array_team_damage_dealth_timeline.append(team_damage_dealth_avg)
        array_oppo_damage_dealth_timeline.append(oppo_damage_dealth_avg)

        array_player_minion_timeline.append(player_minion)

    print(array_player_gold_timeline)
    print(array_player_damage_dealth_timeline)

except Exception as e:
    print("error")
    print(e)
    pass
