import sys
import os.path
from os import path

import requests
import numpy as np
import pandas as pd
import json
import time
from datetime import date
import html_maker
import apiInfo

#########################################################################
########################### SUB FUNCTIONS ###############################

# API default setting.
apiDefault = apiInfo.apiDefault


# read csv file and return dataframe with it.
def ReadCSVtoDF(filename):
	df = pd.read_csv(filename)
	df = pd.DataFrame(df)
	return df


def getSummonerName(puuid):
	url = F"{apiDefault['region']}/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={apiDefault['key']}"
	req = requests.get(url)
	summoner_info = json.loads(req.text)
	summoner_info = pd.DataFrame(summoner_info,  index=[0])

	summoner_name = summoner_info['name']
	summoner_name = summoner_name.to_numpy()[0]

	return summoner_name

# get average of a dataframe.(copied from tier_avg_getter.py)
def get_Avg_Match_Data(df_match_data):
	mean_df_match_data = []
	mean_df_match_data = df_match_data.mean(numeric_only = True)
	# print(mean_df_match_data)
	mean_df_match_data = pd.DataFrame(mean_df_match_data)
	print("Mean Data is ready.")

	return mean_df_match_data

# collect recent 10 game data with the puuid.
def get_10_game_data(puuid):

	# 1) get recent match ids from the server API.
	# get match IDs from the puuid list.
	MatchIDs = []
	url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=10&api_key={apiDefault['key']}"
	req = requests.get(url)
	MatchIDs = json.loads(req.text)
	print(MatchIDs)
	#MatchIDs = sum(MatchIDs, [])
	MatchIDs = pd.DataFrame(MatchIDs, columns=['MatchID'])
	#MatchIDs = MatchIDs.drop_duplicates(['MatchID'])

	# 1-1) save the match id list and return.
	filename = "%s\matchIDs.csv" % (puuid)
	MatchIDs.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)
	print("User match Id collected and saved.")

	# 2) get match data of each matches and put them into a dataframe.
	match_data_all = []
	match_data_all = pd.DataFrame(match_data_all)

	player_index_list = []

	for i in range(len(MatchIDs)):
		try:
			url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/{MatchIDs['MatchID'].loc[i]}?api_key={apiDefault['key']}"
			time.sleep(1)
			req = requests.get(url)

			# collect PARTICIPANTS in the match
			match_id = MatchIDs['MatchID'].loc[i]
			match_data = json.loads(req.text)
			match_data = match_data["info"]["participants"]
			df_match_data = pd.DataFrame(match_data)

			filename = "%s\%s_alluser.csv" % (puuid, match_id)
			df_match_data.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

			find_user_in_data = df_match_data['puuid'] == puuid
			player_index_boolean = find_user_in_data

			player_index = 1
			for j in range(len(player_index_boolean)):
				if player_index_boolean[j] == False :
					player_index = player_index + 1
				else: break
			print(player_index)

			player_index_list.append(player_index)

			df_match_data = df_match_data[find_user_in_data]

			# 2-1) save the match data and return.
			filename = "%s\%s.csv" % (puuid, match_id)
			df_match_data.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

			# 2-2 is removed since it returns same value.
			# # 2-2) get mean value of each match and save as csv file.
			# df_match_data_mean = get_Avg_Match_Data(df_match_data)
			# df_match_data_mean = df_match_data_mean.transpose()
			# filename = "%s\%s_mean.csv"%(puuid, match_id)
			# df_match_data_mean.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

		except Exception as e:
			print(e)
			pass

		match_data_all = pd.concat([match_data_all, df_match_data], axis=0)
		print("Match Number ", i + 1, "/", len(MatchIDs))

	# 3) save the match data all and return.
	filename = "%s\match_data_all.csv" % (puuid)
	match_data_all.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)
	print("Match data all is collected.")

	# 3-1) get summoner id from the data
	summoner_id = match_data_all['summonerId'].iloc[0]
	print("summoner id is ", summoner_id)

	# 4) get average of dataframe.
	df_avg_data = get_Avg_Match_Data(match_data_all)
	df_avg_data = df_avg_data.transpose()
	filename = "%s\match_data_all_mean.csv" % (puuid)
	df_avg_data.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

	# 5) return the dataframe.
	return df_avg_data, summoner_id, MatchIDs, player_index_list

# get tier average data from avg_data_v.0.0.1
def get_tier_avg_data(tier_name):
	filename = "avg_data_v.0.0.1/%s_avg_data.csv" % (tier_name)
	df_tier_avg_data = ReadCSVtoDF(filename)
	return df_tier_avg_data

# get tier data from summoner name.
def get_user_tier_data(summoner_id):
	try:
		url = F"{apiDefault['region']}/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={apiDefault['key']}"
		req = requests.get(url)
		summoner_info = json.loads(req.text)
		summoner_info = pd.DataFrame(summoner_info)
		is_solo_queue = summoner_info['queueType'] == 'RANKED_SOLO_5x5'
		summoner_info = summoner_info[is_solo_queue]

		tier = summoner_info['tier']
		tier = tier.to_numpy()[0]

		tier_number = summoner_info['rank']
		tier_number = tier_number.to_numpy()[0]

		leaguePoints = summoner_info['leaguePoints']
		leaguePoints = leaguePoints.to_numpy()[0]

		wins = summoner_info['wins']
		wins = wins.to_numpy()[0]

		losses = summoner_info['losses']
		losses = losses.to_numpy()[0]

	except:
		print("소환사가 존재하지 않거나, 솔로랭크를 진행한 적이 없습니다.\n LOLai 분석을 위해서는 솔로랭크 전적이 필요합니다.")

	# losses 추가하기 나중에
	return tier, tier_number, wins, losses, leaguePoints


# Get Time line data from the server.
def getMatchTimelineInfo(matchId, player_number):
	array_player_gold_timeline = []
	array_team_gold_timeline = []
	array_oppo_gold_timeline = []

	array_player_damage_dealt_timeline = []
	array_team_damage_dealt_timeline = []
	array_oppo_damage_dealt_timeline = []

	array_player_minion_timeline = []
	array_level_timeline = []

	try:
		url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/{matchId}/timeline?api_key={apiDefault['key']}"
		req = requests.get(url)
		match_info_timeline = json.loads(req.text)

		timeline_length = len(match_info_timeline['info']['frames'])

		# player/team/oppo gold total + player level changes.
		for i in range(0, timeline_length):
			team_gold = 0
			oppo_gold = 0

			player_gold = match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['totalGold']
			player_level = match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['level']
			player_damage_dealt = match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['damageStats']['totalDamageDoneToChampions']

			team_damage_dealt = 0
			oppo_damage_dealt = 0
			player_minion = match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['minionsKilled'] + \
			    match_info_timeline['info']['frames'][i]['participantFrames'][str(player_number)]['jungleMinionsKilled']

			for j in range(1, 6):
				team_gold = team_gold + \
				    match_info_timeline['info']['frames'][i]['participantFrames'][str(j)]['totalGold']
				team_damage_dealt = team_damage_dealt + \
				    match_info_timeline['info']['frames'][i]['participantFrames'][str(j)]['damageStats']['totalDamageDoneToChampions']

			for k in range(6, 11):
				oppo_gold = oppo_gold + \
				    match_info_timeline['info']['frames'][i]['participantFrames'][str(k)]['totalGold']
				oppo_damage_dealt = oppo_damage_dealt + \
				    match_info_timeline['info']['frames'][i]['participantFrames'][str(k)]['damageStats']['totalDamageDoneToChampions']


			team_damage_dealt_avg = round(team_damage_dealt / 5)
			oppo_damage_dealt_avg = round(oppo_damage_dealt / 5)

			array_team_gold_timeline.append(team_gold)
			array_oppo_gold_timeline.append(oppo_gold)
			array_player_gold_timeline.append(player_gold)

			array_level_timeline.append(player_level)
			array_player_damage_dealt_timeline.append(player_damage_dealt)
			array_team_damage_dealt_timeline.append(team_damage_dealt_avg)
			array_oppo_damage_dealt_timeline.append(oppo_damage_dealt_avg)
			array_player_minion_timeline.append(player_minion)

		print("1 - " ,array_level_timeline)
		print("2 - " ,array_player_damage_dealt_timeline)
		print("3 - " ,array_team_damage_dealt_timeline)
		print("4 - " ,array_oppo_damage_dealt_timeline)
		print("5 - " ,array_player_minion_timeline)

	except Exception as e:
		print(e)
		pass


	return array_player_gold_timeline, array_team_gold_timeline, array_oppo_gold_timeline, array_player_damage_dealt_timeline, array_team_damage_dealt_timeline, array_oppo_damage_dealt_timeline, array_level_timeline, timeline_length, array_player_minion_timeline


# Load saved history & Save lolai score with its date to text files
def lolaiScoreSaveAndLoad(lolaiScore_score, time_now, puuid):
    # score
	try:
		filename1 = "%s/history_score.csv" % (puuid)
		df_score = ReadCSVtoDF(filename)

		if len(df_score) > 7:
			df_score.drop(0)

		df_score.append(lolaiScore_score)
		df_score.to_csv(filename1, mode='w', encoding="utf-8-sig", index=False)

	except Exception as e:
		filename1 = "%s/history_score.csv" % (puuid)
		df_score = []

		for i in range(0,7) :
			df_score.append(lolaiScore_score)

		df_score = pd.DataFrame(df_score)
		print(df_score)
		df_score.to_csv(filename1, mode='w', encoding="utf-8-sig", index=False)

	# date
	try:
		filename2 = "%s/history_date.csv" % (puuid)
		df_score_date = ReadCSVtoDF(filename)

		if len(df_score_date) > 7:
			df_score_date.drop(0)

		df_score_date.append(time_now)
		df_score_date.to_csv(filename2, mode='w', encoding="utf-8-sig", index=False)

	except Exception as e:
		filename2 = "%s/history_date.csv" % (puuid)
		df_score_date = []

		for i in range(0,7) :
			df_score_date.append(time_now)

		df_score_date = pd.DataFrame(df_score_date)
		df_score_date.to_csv(filename2, mode='w', encoding="utf-8-sig", index=False)

	df_lolaiScore_history_score = df_score
	df_lolaiScore_history_date = df_score_date

	return df_lolaiScore_history_score, df_lolaiScore_history_date

# change the factor title readable for users.


def factor_title_changer(factor):

	if factor == "assists":
		readable_factor = "어시스트"
	elif factor == "baronKills":
		readable_factor = "바론 처치 수"
	elif factor == "bountyLevel":
		readable_factor = "현상금 레벨"
	elif factor == "champExperience":
		readable_factor = "챔피언 숙련도"
	elif factor == "consumablesPurchased":
		readable_factor = "소모품 구매 수"
	elif factor == "damageDealtToObjectives":
		readable_factor = "오브젝트에 가한 딜량"
	elif factor == "damageDealtToTurrets":
		readable_factor = "타워에 가한 딜량"
	elif factor == "deaths":
		readable_factor = "데쓰 수"
	elif factor == "dragonKills":
		readable_factor = "드래곤 처치 수"
	elif factor == "firstTowerAssist":
		readable_factor = "첫포탑 파괴 어시스트"
	elif factor == "goldEarned":
		readable_factor = "골드 획득량"
	elif factor == "goldSpent":
		readable_factor = "골드 사용량"
	elif factor == "inhibitorTakedowns":
		readable_factor = "억제기 파괴 수"
	elif factor == "inhibitorsLost":
		readable_factor = "잃은 억제기 수"
	elif factor == "itemsPurchased":
		readable_factor = "아이템 구매 수"
	elif factor == "killingSprees":
		readable_factor = "다중킬 수"
	elif factor == "kills":
		readable_factor = "킬 수"
	elif factor == "largestKillingSpree":
		readable_factor = "최다 다중킬 수"
	elif factor == "largestMultiKill":
		readable_factor = "최다 멀티 킬 수"
	elif factor == "longestTimeSpentLiving":
		readable_factor = "최장 살아있었던 시간"
	elif factor == "magicDamageDealt":
		readable_factor = "가한 마법데미지 수"
	elif factor == "magicDamageDealtToChampions":
		readable_factor = "챔피언에 가한 마법데미지 수"
	elif factor == "physicalDamageDealt":
		readable_factor = "물리데미지 수"
	elif factor == "physicalDamageDealtToChampions":
		readable_factor = "챔피언에 가한 물리데미지 수"
	elif factor == "timeCCingOthers":
		readable_factor = "다른 플레이어를 CC건 시간"
	elif factor == "totalDamageDealt":
		readable_factor = "가한 토탈 데미지 수"
	elif factor == "totalDamageDealtToChampions":
		readable_factor = "챔피언에 가한 토탈 데미지 수"
	elif factor == "totalDamageShieldedOnTeammates":
		readable_factor = "동일팀에게 제공한 쉴드량"
	elif factor == "totalDamageTaken":
		readable_factor = "받은 토탈 데미지"
	elif factor == "totalHeal":
		readable_factor = "토탈 힐량"
	elif factor == "totalMinionsKilled":
		readable_factor = "미니언 처치 수"
	elif factor == "totalTimeSpentDead":
		readable_factor = "데쓰로 있었던 시간 총합"
	elif factor == "totalUnitsHealed":
		readable_factor = "힐을 제공한 유닛 수"
	elif factor == "trueDamageTaken":
		readable_factor = "받은 트루데미지량"
	elif factor == "turretKills":
		readable_factor = "개인 포탑 처치 수"
	elif factor == "turretTakedowns":
		readable_factor = "팀 토탈 포탑 처치 수"
	elif factor == "turretsLost":
		readable_factor = "잃은 포탑 수"
	elif factor == "visionScore":
		readable_factor = "비전 점수"
	elif factor == "visionWardsBoughtInGame":
		readable_factor = "비전 와드 구매 수"
	elif factor == "wardsPlaced":
		readable_factor = "와드 설치 수"
	else:
		readable_factor = "NAN"

	return readable_factor


# 아마도 쓰이지 않을 예정
# # get explanation from the factor. --------------------------------------------- 나머지 추가 필요합니다.
# def getExplanation(factor, ifWin, factor_value, tier_avg):
#
#     if ifWin == True:
#         if factor == "와드 설치 수":
#             explantion = "와드 설치가 어쩌고 저쩌고"
#         else:
#             explantion = "어쩌고 저쩌고"
#     else:
#         explanation = "어쩌고 저쩌고 2"
#
#     explantion = "내용 추가 필요"
#
#     return explantion

# def getExplanation(factor):
#
#     explantion = "현재 test, 추후 내용 추가 필요"
#
#     return explantion


# return grade from user number factors as percentage.
def grade_checker_factors(user_number_percentage):
	if user_number_percentage > 100:
		grade = "SSS"
	elif user_number_percentage > 80:
		grade = "SS"
	elif user_number_percentage > 60:
		grade = "S"
	elif user_number_percentage > 40:
		grade = "A"
	elif user_number_percentage > 0:
		grade = "B"
	elif user_number_percentage > -40:
		grade = "C"
	elif user_number_percentage > -60:
		grade = "D"
	elif user_number_percentage > -80:
		grade = "E"
	else:
		grade = "F"

	return grade


# generate comment for the specific grade.
def LOLai_gradeCommentGenerator(GRADE):

	if GRADE == "SSS":
		comment = "흠...이 플레이는...설마 부캐?? ƪ(˘⌣˘)ʃ"
	elif GRADE == "SS":
		comment = "와우! 왜 아직까지 여기 계신거죠?? 이쪽으로 모시겠습니다, 어서 올라가시죠. ✿˘◡˘✿"
	elif GRADE == "A":
		comment = "대단합니다! 게임을 승리로 이끌고 계시군요! (੭•̀ᴗ•̀)੭"
	elif GRADE == "B":
		comment = "당신의 플레이는 티어 평균과 동일합니다.(~˘▾˘)~"
	elif GRADE == "E":
		comment = "혹시 게임을 던지시고 계신건 아니죠? (๑•﹏•)"
	elif GRADE == "F":
		comment = "혹시 당신은 Bug?! 아 물론 프로그램 버그요! 이 점수는 오류인게 분명..할겁니다. 아무튼 그렇습니다. ｡･ﾟﾟ･(>д<)･ﾟﾟ･｡"

	return comment


# # estimate the player's tier based on the match data
# # 로직 수정 필요 - 낮을수록 좋은게 있고, 높을수록 좋은게 있는데, 반영이 안되어있어서 제대로 된 결과를 얻기 힘듬.
# def tierEstimator(df_val_user):
#
#
# 	tier_name = ["iron", "bronze", "silver", "gold", "platinum",
# 	"diamond", "master", "grandmaster", "challenger"]
#
# 	estimated_tier = 0  # iron as default
#
# 	for i in range(len(tier_name)):
# 		df_avg_val_tier = get_tier_avg_data(tier_name[i])
#
# 		df_avg_val_diff = df_val_user.div(df_avg_val_tier, axis=1)
# 		df_avg_val_diff = df_avg_val_diff.multiply(100)
# 		df_avg_val_diff = df_avg_val_diff.sub(100)
#
# 		mean_value = df_avg_val_diff.iloc[0].mean(axis=0)
#
# 		print(mean_value)
#
# 		if mean_value > 0:
# 			estimated_tier = i
#
# 			tier = tier_name[estimated_tier]
# 			print(tier)
#
# 	return tier

# get match id from the user, and get general data of the match.
def getGeneralMatchData(matchid, summonerName):

	playerNicknameList = []
	playerChampionList = []

	try:
		url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/{matchid}?api_key={apiDefault['key']}"
		req = requests.get(url)
		match_info = json.loads(req.text)
		#match_info = pd.DataFrame(match_info)

		# loop participants lists to find the user's data
		for i in range(len(match_info['info']['participants'])):
			if(match_info['info']['participants'][i]['summonerName'] == summonerName):

				zero_death = False

				m_win = match_info['info']['participants'][i]['win']
				m_duration = match_info['info']['gameDuration']
				m_kills = match_info['info']['participants'][i]['kills']
				m_assists = match_info['info']['participants'][i]['assists']
				m_deaths = match_info['info']['participants'][i]['deaths']
				m_kda = str(m_kills) + "/" + str(m_deaths) + "/" + str(m_assists)

				# prevent logical error division with 0
				if m_deaths == 0:
					m_deaths = 1
					zero_death = True

				m_kda_percentage = (m_kills + m_assists) / m_deaths

				# make it back to normal.
				if zero_death == True:
					zero_death = False
					m_deaths = 0

				m_total_cs = match_info['info']['participants'][i]['totalMinionsKilled'] + match_info['info']['participants'][i]['neutralMinionsKilled']
				m_cs_per_minute = m_total_cs / (m_duration / 60)
				m_level = match_info['info']['participants'][i]['champLevel']
				m_champ = match_info['info']['participants'][i]['championName']
				m_grade = "A"

				playerNicknameList.append(match_info['info']['participants'][i]['summonerName'])
				playerChampionList.append(match_info['info']['participants'][i]['championName'])

			# other players in this game
			else:
				playerNicknameList.append(match_info['info']['participants'][i]['summonerName'])
				playerChampionList.append(match_info['info']['participants'][i]['championName'])

	except:
		print("Match not found.")

	return m_win, m_duration, m_kda, m_kda_percentage, m_total_cs, m_cs_per_minute, m_level, m_grade, m_champ, playerNicknameList, playerChampionList


# use data to get calculated data for chart build
def chartDataCalculator(df_player_data, df_tier_data):

	chart_gold_p_calculated = int(df_player_data['goldEarned'].item())
	chart_alive_p_calculated = int((df_player_data['kills'].item() + df_player_data['assists'].item())/(df_player_data['deaths'].item()+1))
	chart_battle_p_calculated = int(df_player_data['totalDamageDealt'].item())
	chart_growth_p_calculated = df_player_data['champLevel'].item() / int(df_player_data['timePlayed'].item()/60)

	chart_gold_tier_calculated = int(df_tier_data['goldEarned'].item())
	chart_alive_tier_calculated = int((df_tier_data['kills'].item() + df_tier_data['assists'].item())/(df_tier_data['deaths'].item()+1))
	chart_battle_tier_calculated = int(df_tier_data['totalDamageDealt'].item())
	chart_growth_tier_calculated = df_tier_data['champLevel'].item() / int(df_tier_data['timePlayed'].item()/60)

	chart_object_p_calculated = int(df_player_data['damageDealtToObjectives'].item())
	chart_object_tier_calculated = int(df_tier_data['damageDealtToObjectives'].item())

	normalization_list_gold = []
	normalization_list_alive = []
	normalization_list_battle = []
	normalization_list_growth = []
	normalization_list_object = []

	print("CHART GROWTH IS : ", chart_growth_p_calculated, chart_growth_tier_calculated)

	normalization_list_gold.append([chart_gold_p_calculated,chart_gold_tier_calculated, 0, 15000])
	normalization_list_alive.append([chart_alive_p_calculated,chart_alive_tier_calculated, 0, 5])
	normalization_list_battle.append([chart_battle_p_calculated,chart_battle_tier_calculated, 0, 200000])
	normalization_list_growth.append([chart_growth_p_calculated,chart_growth_tier_calculated, 0, 1])
	normalization_list_object.append([chart_object_p_calculated,chart_object_tier_calculated, 0, 20000])

	normalized_list_gold = html_maker.min_max_normalize(normalization_list_gold)
	normalized_list_alive = html_maker.min_max_normalize(normalization_list_alive)
	normalized_list_battle = html_maker.min_max_normalize(normalization_list_battle)
	normalized_list_growth = html_maker.min_max_normalize(normalization_list_growth)
	normalized_list_object = html_maker.min_max_normalize(normalization_list_object)

	# error exception.
	# if chart_gold_p_calculated > 100:
	#     chart_gold_p_calculated = 100
	# if chart_alive_p_calculated > 100:
	#     chart_alive_p_calculated = 100
	# if chart_battle_p_calculated > 100:
	#     chart_battle_p_calculated = 100
	# if chart_growth_p_calculated > 100:
	#     chart_growth_p_calculated = 100
	#
	# if chart_gold_p_calculated < 0:
	#     chart_gold_p_calculated = 0
	# if chart_alive_p_calculated < 0:
	#     chart_alive_p_calculated = 0
	# if chart_battle_p_calculated < 0:
	#     chart_battle_p_calculated = 0
	# if chart_growth_p_calculated < 0:
	#     chart_growth_p_calculated = 0

	return normalized_list_gold, normalized_list_alive, normalized_list_battle, normalized_list_growth, normalized_list_object

# get lolaiscore for all users in a match
def get_lolaiScore_List(matchid, df_avg_val_tier):

	filename = "%s/%s_alluser.csv" % (puuid, matchid)
	df_val_all_user = ReadCSVtoDF(filename)

	filename = "LOLPAGO_data_v.0.0.1/weight_of_values_processed.csv"
	weight_of_values = ReadCSVtoDF(filename)

	df_val_diff_all_weighted = []
	df_val_diff_all_weighted = pd.DataFrame(df_val_diff_all_weighted)

	print(df_val_all_user)

	for z in range(0,10) :
		df_val_line = df_val_all_user.iloc[[z]]
		df_val_line = df_val_line.reset_index(drop = True)

		df_val_diff_line = df_val_line.div(df_avg_val_tier, axis=1)
		df_val_diff_line = df_val_diff_line.multiply(100)

		#df_val_diff_line = df_val_diff_line.sub(100)

		df_val_weight_multiplied = df_val_diff_line.multiply(weight_of_values, axis=1)
		df_val_weight_multiplied = df_val_weight_multiplied.dropna(axis=1)

		df_val_diff_all_weighted = df_val_diff_all_weighted.append(df_val_weight_multiplied)


	df_val_diff_all_weighted = df_val_diff_all_weighted.reset_index(drop = True)
	print(df_val_diff_all_weighted)

	# df_val_weight_multiplied = df_val_diff.multiply(weight_of_values, axis=1)
	# df_val_weight_multiplied = pd.DataFrame(df_val_weight_multiplied)
	# #df_val_weight_multiplied = df_val_weight_multiplied.dropna(axis=1)

	lolaiScore_List_team = []
	lolaiScore_List_all = []

	for i in range(0, 5):
		lolaiScore_score = df_val_diff_all_weighted.iloc[[i]].sum(axis=1)
		lolaiScore_score = lolaiScore_score.to_numpy()[0]
		lolaiScore_List_team.append(lolaiScore_score)
		lolaiScore_List_all.append(lolaiScore_score)

	for j in range(5, 10):
		lolaiScore_score = df_val_diff_all_weighted.iloc[[j]].sum(axis=1)
		lolaiScore_score = lolaiScore_score.to_numpy()[0]
		lolaiScore_List_all.append(lolaiScore_score)


	print("Here : " , lolaiScore_List_team , lolaiScore_List_all)

	return lolaiScore_List_team, lolaiScore_List_all

#########################################################################
#########################################################################


#########################################################################
########################### MAIN FUNCTIONS ##############################

# MFUNC 1. analyze average 10 game data with LOLPAGO.
def average_analysis(puuid):

	# 1) get average values of categories of the tier.
	df_avg_val_user, summoner_id, matchIDs, player_index_list = get_10_game_data(puuid)

	# 2) get players values of categories of 10 games and get average.
	tier_name, tier_number, wins, losses, leaguePoints = get_user_tier_data(summoner_id)
	df_avg_val_tier = get_tier_avg_data(tier_name)

	# 3) get LOLPAGO weight of values.
	filename = "LOLPAGO_data_v.0.0.1/weight_of_values.csv"
	weight_of_values = ReadCSVtoDF(filename)
	# print(weight_of_values)
	weight_of_values = weight_of_values[['category', 'percentage']]
	weight_of_values = weight_of_values.transpose()
	weight_of_values.columns = weight_of_values.iloc[0]
	weight_of_values = weight_of_values[1:]
	weight_of_values = weight_of_values.reset_index(drop=True)
	# print(weight_of_values)

	filename = "LOLPAGO_data_v.0.0.1/weight_of_values_processed.csv"
	weight_of_values.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

	# 4) df_avg_val_diff : (dataframe) get 2) - 1) values to get the diffrence between player and tier average as percentage.
	# this file shows what percentage of the category value does the user have compared to the tier average values.
	df_avg_val_diff = df_avg_val_user.div(df_avg_val_tier, axis=1)
	df_avg_val_diff = df_avg_val_diff.multiply(100)
	#df_avg_val_diff = df_avg_val_diff.sub(100)
	# print(df_avg_val_diff)
	# save df_avg_val_diff as csv.
	filename = "%s\df_avg_val_diff.csv" % (puuid)
	df_avg_val_diff.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

	# 5) df_avg_val_weight_multiplied : (dataframe) multiply each values of categories with importance values got from LOLPAGO.
	df_avg_val_weight_multiplied = df_avg_val_diff.multiply(weight_of_values, axis=1)
	df_avg_val_weight_multiplied = df_avg_val_weight_multiplied.dropna(axis=1)

	filename = "%s\df_avg_val_weight_multiplied.csv" % (puuid)
	df_avg_val_weight_multiplied.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

	# 5-1) sort 5) values and give out top 3 values with differences.
	return df_avg_val_diff, df_avg_val_weight_multiplied, tier_name, tier_number, wins, losses, leaguePoints, df_avg_val_user, df_avg_val_tier, matchIDs, summoner_id, player_index_list

# MFUNC 2. analyze just one match data with LOLPAGO. --similar to MFUNC1 but modified for single match analysis purpose.
def match_analysis(puuid, df_val_user, summoner_id, matchid):

	# 2) get players values of categories of 10 games and get average.
	tier_name, tier_number, wins, losses, leaguePoints = get_user_tier_data(summoner_id)
	df_avg_val_tier = get_tier_avg_data(tier_name)

	# 3) get LOLPAGO weight of values.
	filename = "LOLPAGO_data_v.0.0.1/weight_of_values.csv"
	weight_of_values = ReadCSVtoDF(filename)
	# print(weight_of_values)
	weight_of_values = weight_of_values[['category', 'percentage']]
	weight_of_values = weight_of_values.transpose()
	weight_of_values.columns = weight_of_values.iloc[0]
	weight_of_values = weight_of_values[1:]
	weight_of_values = weight_of_values.reset_index(drop=True)
	# print(weight_of_values)

	filename = "LOLPAGO_data_v.0.0.1/weight_of_values_processed.csv"
	weight_of_values.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

	# 4) df_val_diff : (dataframe) get 2) - 1) values to get the diffrence between player and tier average as percentage.
	# this file shows what percentage of the category value does the user have compared to the tier average values.
	df_val_diff = df_val_user.div(df_avg_val_tier, axis=1)
	df_val_diff = df_val_diff.multiply(100)
	#df_val_diff = df_val_diff.sub(100)
	# print(df_avg_val_diff)
	# save df_avg_val_diff as csv.
	filename = "%s\df_%s_val_diff.csv" % (puuid, matchid)
	df_val_diff.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

	# 5) df_avg_val_weight_multiplied : (dataframe) multiply each values of categories with importance values got from LOLPAGO.
	df_val_weight_multiplied = df_val_diff.multiply(weight_of_values, axis=1)
	df_val_weight_multiplied = df_val_weight_multiplied.dropna(axis=1)
	print(df_val_weight_multiplied)

	filename = "%s\df_%s_val_weight_multiplied.csv" % (puuid, matchid)
	df_val_weight_multiplied.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)

	# 5-1) sort 5) values and give out top 3 values with differences.
	return df_val_diff, df_val_weight_multiplied, tier_name, tier_number, wins, losses, leaguePoints, df_val_user, df_avg_val_tier, matchid


# MFUNC 3. make a user info html under the puuid folder.
# it uses MFUNC1
def make_user_info_html(puuid, summoner_name):

	# get new summoner_name since argv can't accept spaces in the nickname
	summoner_name = getSummonerName(puuid)
	df_match_val_diff_tier, df_match_val_weight_multiplied, tier_name, tier_number, wins, losses, leaguePoints, df_avg_val_user, df_avg_val_tier, matchIDs, summoner_id, player_index_list = average_analysis(puuid)

	# Get Time now for update history.
	time_now = date.today().strftime("%Y/%m/%d")
	print(time_now)

	# compute the collected data for html input usage.
	match = wins + losses
	wrate = wins / match * 100

	lolaiScore = df_match_val_weight_multiplied.sum(axis=1)
	lolaiScore_score = lolaiScore.to_numpy()[0]

	if lolaiScore_score > 2000:
		GRADE = "SSS"
	elif lolaiScore_score > 1000:
		GRADE = "SS"
	elif lolaiScore_score > 500:
		GRADE = "A"
	elif lolaiScore_score > 0:
		GRADE = "B"
	elif lolaiScore_score > -1000:
		GRADE = "E"
	elif lolaiScore_score > -2000:
		GRADE = "F"

	df_lolaiScore_history_score, df_lolaiScore_history_date = lolaiScoreSaveAndLoad(lolaiScore_score, time_now, puuid)

	# get best 5 parts / worst 5 parts with numbers.
	df_match_val_weight_multiplied_t = df_match_val_weight_multiplied.transpose()
	df_match_val_weight_multiplied_t_s_p = df_match_val_weight_multiplied_t.sort_values(df_match_val_weight_multiplied_t.columns[0], ascending=False)
	df_match_val_weight_multiplied_t_s_n = df_match_val_weight_multiplied_t.sort_values(df_match_val_weight_multiplied_t.columns[0], ascending=True)

	df_match_val_weight_multiplied_t_s_p = df_match_val_weight_multiplied_t_s_p.iloc[:5]
	df_match_val_weight_multiplied_t_s_n = df_match_val_weight_multiplied_t_s_n.iloc[:5]

	df_match_val_weight_multiplied_t_s_p = df_match_val_weight_multiplied_t_s_p.transpose()
	df_match_val_weight_multiplied_t_s_n = df_match_val_weight_multiplied_t_s_n.transpose()

	# print(df_match_val_weight_multiplied_t_s_p.columns[0])
	# match the values with factors in html.

	# title
	p_f_1_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[0])
	p_f_2_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[1])
	p_f_3_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[2])
	p_f_4_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[3])
	p_f_5_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[4])

	n_f_1_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[0])
	n_f_2_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[1])
	n_f_3_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[2])
	n_f_4_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[3])
	n_f_5_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[4])

	# number
	p_f_1_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_p.columns[0]].item()
	p_f_2_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_p.columns[1]].item()
	p_f_3_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_p.columns[2]].item()
	p_f_4_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_p.columns[3]].item()
	p_f_5_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_p.columns[4]].item()

	n_f_1_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_n.columns[0]].item()
	n_f_2_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_n.columns[1]].item()
	n_f_3_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_n.columns[2]].item()
	n_f_4_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_n.columns[3]].item()
	n_f_5_v = df_avg_val_user[df_match_val_weight_multiplied_t_s_n.columns[4]].item()

	# normalization of p_f and n_f
	p_f_list = []
	n_f_list = []

	p_f_list.append([p_f_1_v, p_f_2_v, p_f_3_v, p_f_4_v, p_f_5_v, 0])
	n_f_list.append([n_f_1_v, n_f_2_v, n_f_3_v, n_f_4_v, n_f_5_v, 0])

	normalized_p_f_list = html_maker.min_max_normalize(p_f_list)
	normalized_n_f_list = html_maker.min_max_normalize(n_f_list)

	for num in range(len(normalized_p_f_list)) :
		if normalized_p_f_list[num] < 1 and normalized_p_f_list[num] < 0.05 : normalized_p_f_list[num] = normalized_p_f_list[num] + 20
		if normalized_p_f_list[num] < 1 and normalized_p_f_list[num] > 0.05 : normalized_p_f_list[num] = normalized_p_f_list[num] + 35
		if normalized_n_f_list[num] < 1 and normalized_n_f_list[num] < 0.05: normalized_n_f_list[num] = normalized_n_f_list[num] + 20
		if normalized_n_f_list[num] < 1 and normalized_n_f_list[num] > 0.05: normalized_n_f_list[num] = normalized_n_f_list[num] + 35

	normalized_p_f_1_v = normalized_p_f_list[0]
	normalized_p_f_2_v = normalized_p_f_list[1]
	normalized_p_f_3_v = normalized_p_f_list[2]
	normalized_p_f_4_v = normalized_p_f_list[3]
	normalized_p_f_5_v = normalized_p_f_list[4]

	normalized_n_f_1_v = normalized_n_f_list[0]
	normalized_n_f_2_v = normalized_n_f_list[1]
	normalized_n_f_3_v = normalized_n_f_list[2]
	normalized_n_f_4_v = normalized_n_f_list[3]
	normalized_n_f_5_v = normalized_n_f_list[4]

	# # grade
	# p_f_1_g = grade_checker_factors(df_avg_val_user[df_match_val_weight_multiplied_t_s_p.columns[0]].item())
	# p_f_2_g = grade_checker_factors(df_avg_val_user[df_match_val_weight_multiplied_t_s_p.columns[1]].item())
	# p_f_3_g = grade_checker_factors(df_avg_val_user[df_match_val_weight_multiplied_t_s_p.columns[2]].item())
	#
	# n_f_1_g = grade_checker_factors(df_avg_val_user[df_match_val_weight_multiplied_t_s_n.columns[0]].item())
	# n_f_2_g = grade_checker_factors(df_avg_val_user[df_match_val_weight_multiplied_t_s_n.columns[1]].item())
	# n_f_3_g = grade_checker_factors(df_avg_val_user[df_match_val_weight_multiplied_t_s_n.columns[2]].item())
	#
	# # tier-average
	# p_f_1_a = df_avg_val_tier[df_match_val_weight_multiplied_t_s_p.columns[0]].item()
	# p_f_2_a = df_avg_val_tier[df_match_val_weight_multiplied_t_s_p.columns[1]].item()
	# p_f_3_a = df_avg_val_tier[df_match_val_weight_multiplied_t_s_p.columns[2]].item()
	#
	# n_f_1_a = df_avg_val_tier[df_match_val_weight_multiplied_t_s_n.columns[0]].item()
	# n_f_2_a = df_avg_val_tier[df_match_val_weight_multiplied_t_s_n.columns[1]].item()
	# n_f_3_a = df_avg_val_tier[df_match_val_weight_multiplied_t_s_n.columns[2]].item()

	# get recent 5 match id from the list
	matchIDs = matchIDs[:5]
	print(matchIDs)

	# get match data from the match id list
	m_1_win, m_1_duration, m_1_kda, m_1_kda_percentage, m_1_total_cs, m_1_cs_per_minute, m_1_level, m_1_grade, m_1_champ, m1_playerNicknameList, m1_playerChampionList = getGeneralMatchData(matchIDs.iloc[0].to_numpy()[0], summoner_name)
	m_2_win, m_2_duration, m_2_kda, m_2_kda_percentage, m_2_total_cs, m_2_cs_per_minute, m_2_level, m_2_grade, m_2_champ, m2_playerNicknameList, m2_playerChampionList = getGeneralMatchData(matchIDs.iloc[1].to_numpy()[0], summoner_name)
	m_3_win, m_3_duration, m_3_kda, m_3_kda_percentage, m_3_total_cs, m_3_cs_per_minute, m_3_level, m_3_grade, m_3_champ, m3_playerNicknameList, m3_playerChampionList = getGeneralMatchData(matchIDs.iloc[2].to_numpy()[0], summoner_name)
	m_4_win, m_4_duration, m_4_kda, m_4_kda_percentage, m_4_total_cs, m_4_cs_per_minute, m_4_level, m_4_grade, m_4_champ, m4_playerNicknameList, m4_playerChampionList = getGeneralMatchData(matchIDs.iloc[3].to_numpy()[0], summoner_name)
	m_5_win, m_5_duration, m_5_kda, m_5_kda_percentage, m_5_total_cs, m_5_cs_per_minute, m_5_level, m_5_grade, m_5_champ, m5_playerNicknameList, m5_playerChampionList = getGeneralMatchData(matchIDs.iloc[4].to_numpy()[0], summoner_name)

	playerNicknameList_total = []
	playerNicknameList_total.extend([m1_playerNicknameList, m2_playerNicknameList, m3_playerNicknameList, m4_playerNicknameList, m5_playerNicknameList])
	playerChampionList_total = []
	playerChampionList_total.extend([m1_playerChampionList, m2_playerChampionList, m3_playerChampionList, m4_playerChampionList, m5_playerChampionList])

	###############################
	# create match_info.html here.

	grades, recent_match_history_data, recent_win_rate_data = make_match_info_html(matchIDs, puuid, summoner_id, match, wins, losses, playerNicknameList_total, playerChampionList_total, player_index_list)  # matchid list is passed here.

	###############################

	# make a list that contains analysis page for individual match id. (total 5)
	match_page_list = [1, 2, 3, 4, 5]
	for i in range(0, 5):
		filename = "match_" + matchIDs.iloc[i].to_numpy()[0] + "_info.html"
		match_page_list[i] = filename


	# chart data calculator
	normalized_list_gold, normalized_list_alive, normalized_list_battle, normalized_list_growth, normalized_list_object = chartDataCalculator(df_avg_val_user, df_avg_val_tier)

	normalized_list_gold, normalized_list_alive, normalized_list_battle, normalized_list_growth, normalized_list_object

	chart_gold_p_calculated = normalized_list_gold[0]
	chart_gold_tier_calculated= normalized_list_gold[1]

	chart_alive_p_calculated= normalized_list_alive[0]
	chart_alive_tier_calculated= normalized_list_alive[1]

	chart_battle_p_calculated= normalized_list_battle[0]
	chart_battle_tier_calculated= normalized_list_battle[1]

	chart_growth_p_calculated= normalized_list_growth[0]
	chart_growth_tier_calculated= normalized_list_growth[1]

	chart_object_p_calculated= normalized_list_object[0]
	chart_object_tier_calculated= normalized_list_object[1]


	# expectation calculation
	expected_line_w_r = round((chart_gold_p_calculated + chart_growth_p_calculated) / 2, 1)
	expected_promo_r = round((chart_gold_p_calculated + chart_alive_p_calculated + chart_battle_p_calculated + chart_growth_p_calculated) / 4, 1)


	# recent match history
	win_history_list = [m_1_win, m_2_win, m_3_win, m_4_win, m_5_win]
	match_color_list = ["#FFCCCC", "#FFCCCC","#FFCCCC","#FFCCCC","#FFCCCC","#FFCCCC"] #last one is the analyzed match.
	str1 = ""
	rwr_win = 0
	rwr_lose = 0
	for i in range(len(win_history_list)) :
		if win_history_list[i] == True :
			rwr_win = rwr_win + 1
			str1 = str1 + "승"
			win_history_list[i] = "승리"
			match_color_list[i] = "#add0f7"
		else :
			rwr_lose = rwr_lose + 1
			str1 = str1 + "패"
			win_history_list[i] = "패배"

	recent_match_history_data = str1
	recent_win_rate_data = round(rwr_win/5 * 100, 1)

	###########################################################################
	###########################################################################
	# string to make a html file.
	html_str = str(html_maker.html_page(1))
	html_str = html_str.format(

	    #####################
	    # BASIC INFORMATION #
	    #####################
	    nickname=summoner_name, update_date=time_now,
	    tier=tier_name,
	    tier_num=tier_number,
	    LP=leaguePoints,
	    total_match_number=match,
	    wins=wins,
	    losses=losses,
	    win_rate=round(wrate, 1),
	    lolai_score_letter=GRADE,
	    lolai_score_number=round(lolaiScore_score, 2),
	    lolai_score_comment=LOLai_gradeCommentGenerator(GRADE),
	    recent_match_history=recent_match_history_data,
	    recent_win_rate=recent_win_rate_data,

	    expected_win_rate=expected_line_w_r, expected_promo= expected_promo_r,

	    ##################################
	    # MATCH PARTICIPANTS INFORMATION #
	    ##################################


	    # match 1 information
	    match_1_bool_win= win_history_list[0],
	    match_1_length=str(int(m_1_duration / 60 % 60)) + "분 " + str(m_1_duration % 60) + "초",
	    match_1_kda=m_1_kda,
	    match_1_kda_percentage=round(m_1_kda_percentage, 1),
	    match_1_cs=m_1_total_cs,
	    match_1_cs_per_minuite=round(m_1_cs_per_minute, 2),
	    match_1_level=m_1_level,
	    match_1_player_1=m1_playerNicknameList[0],
	    match_1_player_2=m1_playerNicknameList[1],
	    match_1_player_3=m1_playerNicknameList[2],
	    match_1_player_4=m1_playerNicknameList[3],
	    match_1_player_5=m1_playerNicknameList[4],
	    match_1_player_6=m1_playerNicknameList[5],
	    match_1_player_7=m1_playerNicknameList[6],
	    match_1_player_8=m1_playerNicknameList[7],
	    match_1_player_9=m1_playerNicknameList[8],
	    match_1_player_10=m1_playerNicknameList[9],

	    match_1_player_1_champ=m1_playerChampionList[0],
	    match_1_player_2_champ=m1_playerChampionList[1],
	    match_1_player_3_champ=m1_playerChampionList[2],
	    match_1_player_4_champ=m1_playerChampionList[3],
	    match_1_player_5_champ=m1_playerChampionList[4],
	    match_1_player_6_champ=m1_playerChampionList[5],
	    match_1_player_7_champ=m1_playerChampionList[6],
	    match_1_player_8_champ=m1_playerChampionList[7],
	    match_1_player_9_champ=m1_playerChampionList[8],
	    match_1_player_10_champ=m1_playerChampionList[9],

	    match_1_lolai_score_letter= m_1_grade,
	    match_1_champ= m_1_champ,

	    # match 2 information
	    match_2_bool_win= win_history_list[1],
	    match_2_length=str(int(m_2_duration / 60 % 60)) + "분 " + str(m_2_duration % 60) + "초",
	    match_2_kda=m_2_kda,
	    match_2_kda_percentage=round(m_2_kda_percentage, 1),
	    match_2_cs=m_2_total_cs,
	    match_2_cs_per_minuite=round(m_2_cs_per_minute, 2),
	    match_2_level=m_2_level,
	    match_2_player_1=m2_playerNicknameList[0],
	    match_2_player_2=m2_playerNicknameList[1],
	    match_2_player_3=m2_playerNicknameList[2],
	    match_2_player_4=m2_playerNicknameList[3],
	    match_2_player_5=m2_playerNicknameList[4],
	    match_2_player_6=m2_playerNicknameList[5],
	    match_2_player_7=m2_playerNicknameList[6],
	    match_2_player_8=m2_playerNicknameList[7],
	    match_2_player_9=m2_playerNicknameList[8],
	    match_2_player_10=m2_playerNicknameList[9],

	    match_2_player_1_champ=m2_playerChampionList[0],
	    match_2_player_2_champ=m2_playerChampionList[1],
	    match_2_player_3_champ=m2_playerChampionList[2],
	    match_2_player_4_champ=m2_playerChampionList[3],
	    match_2_player_5_champ=m2_playerChampionList[4],
	    match_2_player_6_champ=m2_playerChampionList[5],
	    match_2_player_7_champ=m2_playerChampionList[6],
	    match_2_player_8_champ=m2_playerChampionList[7],
	    match_2_player_9_champ=m2_playerChampionList[8],
	    match_2_player_10_champ=m2_playerChampionList[9],

	    match_2_lolai_score_letter=m_2_grade,
	    match_2_champ=m_2_champ,

	    # match 3 information
	    match_3_bool_win=win_history_list[2],
	    match_3_length=str(int(m_3_duration / 60 % 60)) + "분 " + str(m_3_duration % 60) + "초",
	    match_3_kda=m_3_kda,
	    match_3_kda_percentage=round(m_3_kda_percentage, 1),
	    match_3_cs=m_3_total_cs,
	    match_3_cs_per_minuite=round(m_3_cs_per_minute, 2),
	    match_3_level=m_3_level,
	    match_3_player_1=m3_playerNicknameList[0],
	    match_3_player_2=m3_playerNicknameList[1],
	    match_3_player_3=m3_playerNicknameList[2],
	    match_3_player_4=m3_playerNicknameList[3],
	    match_3_player_5=m3_playerNicknameList[4],
	    match_3_player_6=m3_playerNicknameList[5],
	    match_3_player_7=m3_playerNicknameList[6],
	    match_3_player_8=m3_playerNicknameList[7],
	    match_3_player_9=m3_playerNicknameList[8],
	    match_3_player_10=m3_playerNicknameList[9],

	    match_3_player_1_champ=m3_playerChampionList[0],
	    match_3_player_2_champ=m3_playerChampionList[1],
	    match_3_player_3_champ=m3_playerChampionList[2],
	    match_3_player_4_champ=m3_playerChampionList[3],
	    match_3_player_5_champ=m3_playerChampionList[4],
	    match_3_player_6_champ=m3_playerChampionList[5],
	    match_3_player_7_champ=m3_playerChampionList[6],
	    match_3_player_8_champ=m3_playerChampionList[7],
	    match_3_player_9_champ=m3_playerChampionList[8],
	    match_3_player_10_champ=m3_playerChampionList[9],

	    match_3_lolai_score_letter=m_3_grade,
	    match_3_champ=m_3_champ,

	    # match 4 information
	    match_4_bool_win=win_history_list[3],
	    match_4_length=str(int(m_4_duration / 60 % 60)) + "분 " + str(m_4_duration % 60) + "초",
	    match_4_kda=m_4_kda,
	    match_4_kda_percentage=round(m_4_kda_percentage, 1),
	    match_4_cs=m_4_total_cs,
	    match_4_cs_per_minuite=round(m_4_cs_per_minute, 2),
	    match_4_level=m_4_level,
	    match_4_player_1=m4_playerNicknameList[0],
	    match_4_player_2=m4_playerNicknameList[1],
	    match_4_player_3=m4_playerNicknameList[2],
	    match_4_player_4=m4_playerNicknameList[3],
	    match_4_player_5=m4_playerNicknameList[4],
	    match_4_player_6=m4_playerNicknameList[5],
	    match_4_player_7=m4_playerNicknameList[6],
	    match_4_player_8=m4_playerNicknameList[7],
	    match_4_player_9=m4_playerNicknameList[8],
	    match_4_player_10=m4_playerNicknameList[9],

	    match_4_player_1_champ=m4_playerChampionList[0],
	    match_4_player_2_champ=m4_playerChampionList[1],
	    match_4_player_3_champ=m4_playerChampionList[2],
	    match_4_player_4_champ=m4_playerChampionList[3],
	    match_4_player_5_champ=m4_playerChampionList[4],
	    match_4_player_6_champ=m4_playerChampionList[5],
	    match_4_player_7_champ=m4_playerChampionList[6],
	    match_4_player_8_champ=m4_playerChampionList[7],
	    match_4_player_9_champ=m4_playerChampionList[8],
	    match_4_player_10_champ=m4_playerChampionList[9],

	    match_4_lolai_score_letter=m_4_grade,
	    match_4_champ=m_4_champ,

	    # match 5 information
	    match_5_bool_win=win_history_list[4],
	    match_5_length=str(int(m_5_duration / 60 % 60)) + "분 " + str(m_5_duration % 60) + "초",
	    match_5_kda=m_5_kda,
	    match_5_kda_percentage=round(m_5_kda_percentage, 1),
	    match_5_cs=m_5_total_cs,
	    match_5_cs_per_minuite=round(m_5_cs_per_minute, 2),
	    match_5_level=m_5_level,
	    match_5_player_1=m5_playerNicknameList[0],
	    match_5_player_2=m5_playerNicknameList[1],
	    match_5_player_3=m5_playerNicknameList[2],
	    match_5_player_4=m5_playerNicknameList[3],
	    match_5_player_5=m5_playerNicknameList[4],
	    match_5_player_6=m5_playerNicknameList[5],
	    match_5_player_7=m5_playerNicknameList[6],
	    match_5_player_8=m5_playerNicknameList[7],
	    match_5_player_9=m5_playerNicknameList[8],
	    match_5_player_10=m5_playerNicknameList[9],

	    match_5_player_1_champ=m5_playerChampionList[0],
	    match_5_player_2_champ=m5_playerChampionList[1],
	    match_5_player_3_champ=m5_playerChampionList[2],
	    match_5_player_4_champ=m5_playerChampionList[3],
	    match_5_player_5_champ=m5_playerChampionList[4],
	    match_5_player_6_champ=m5_playerChampionList[5],
	    match_5_player_7_champ=m5_playerChampionList[6],
	    match_5_player_8_champ=m5_playerChampionList[7],
	    match_5_player_9_champ=m5_playerChampionList[8],
	    match_5_player_10_champ=m5_playerChampionList[9],

	    match_5_lolai_score_letter=m_5_grade,
	    match_5_champ=m_5_champ,

	    #####################
	    # CHART INFORMATION #
	    #####################

	    radar_player_data_2=chart_gold_p_calculated,
	    radar_player_data_3=chart_alive_p_calculated,
	    radar_player_data_4=chart_battle_p_calculated,
	    radar_player_data_1=chart_growth_p_calculated,
	    radar_player_data_5=chart_object_p_calculated,

	    radar_tier_avg_data_2=chart_gold_tier_calculated,
	    radar_tier_avg_data_3=chart_alive_tier_calculated,
	    radar_tier_avg_data_4=chart_battle_tier_calculated,
	    radar_tier_avg_data_1=chart_growth_tier_calculated,
	    radar_tier_avg_data_5=chart_object_tier_calculated,

		# polar chart
		positive_factor_label_1=p_f_1_t,
		positive_factor_label_2=p_f_2_t,
		positive_factor_label_3=p_f_3_t,
		positive_factor_label_4=p_f_4_t,
		positive_factor_label_5=p_f_5_t,

		positive_factor_data_1=normalized_p_f_1_v,
		positive_factor_data_2=normalized_p_f_2_v,
		positive_factor_data_3=normalized_p_f_3_v,
		positive_factor_data_4=normalized_p_f_4_v,
		positive_factor_data_5=normalized_p_f_5_v,

		negative_factor_label_1=n_f_1_t,
		negative_factor_label_2=n_f_2_t,
		negative_factor_label_3=n_f_3_t,
		negative_factor_label_4=n_f_4_t,
		negative_factor_label_5=n_f_5_t,

		negative_factor_data_1=normalized_n_f_1_v,
		negative_factor_data_2=normalized_n_f_2_v,
		negative_factor_data_3=normalized_n_f_3_v,
		negative_factor_data_4=normalized_n_f_4_v,
		negative_factor_data_5=normalized_n_f_5_v,

	    iron_lolai_score="10",
	    my_league_lolai_score="100",
	    challenger_lolai_score="200",

	    lolai_score_history_1_date=df_lolaiScore_history_date.iloc[0].to_numpy()[0],
	    lolai_score_history_2_date=df_lolaiScore_history_date.iloc[1].to_numpy()[0],
	    lolai_score_history_3_date=df_lolaiScore_history_date.iloc[2].to_numpy()[0],
	    lolai_score_history_4_date=df_lolaiScore_history_date.iloc[3].to_numpy()[0],
	    lolai_score_history_5_date=df_lolaiScore_history_date.iloc[4].to_numpy()[0],
	    lolai_score_history_6_date=df_lolaiScore_history_date.iloc[5].to_numpy()[0],
	    lolai_score_history_7_date=df_lolaiScore_history_date.iloc[6].to_numpy()[0],

	    lolai_score_history_1=df_lolaiScore_history_score.iloc[0].to_numpy()[0],
	    lolai_score_history_2=df_lolaiScore_history_score.iloc[1].to_numpy()[0],
	    lolai_score_history_3=df_lolaiScore_history_score.iloc[2].to_numpy()[0],
	    lolai_score_history_4=df_lolaiScore_history_score.iloc[3].to_numpy()[0],
	    lolai_score_history_5=df_lolaiScore_history_score.iloc[4].to_numpy()[0],
	    lolai_score_history_6=df_lolaiScore_history_score.iloc[5].to_numpy()[0],
	    lolai_score_history_7=df_lolaiScore_history_score.iloc[6].to_numpy()[0],

		match_1_box_color = match_color_list[0],
		match_2_box_color = match_color_list[1],
		match_3_box_color = match_color_list[2],
		match_4_box_color = match_color_list[3],
		match_5_box_color = match_color_list[4],

	    match1_page_link=match_page_list[0],
	    match2_page_link=match_page_list[1],
	    match3_page_link=match_page_list[2],
	    match4_page_link=match_page_list[3],
	    match5_page_link=match_page_list[4],

	    ###################
	    # ADs INFORMATION #
	    ###################
	    AD1_h="1", AD2_h="2"

	)

	# create the html file under the puuid folder.
	filename = r"%s\user_info.html" % (puuid)
	Html_file = open(filename, "w", encoding='utf8')
	Html_file.write(html_str)
	Html_file.close()

	return 0

# MFUNC 4. make a match analysis html under puuid folder
# it uses MFUNC2
def make_match_info_html(matchIDs, puuid, summoner_id, match, wins, losses, playerNicknameList_total, playerChampionList_total, player_index_list):

	# Get Time now for update history.
	time_now = date.today().strftime("%Y/%m/%d")

	# compute the collected data for html input usage.
	match = wins + losses
	wrate = wins / match * 100

	# get list of nickname and chamipons of each matches.
	match_1_player_name_list = playerNicknameList_total[0]
	match_2_player_name_list = playerNicknameList_total[1]
	match_3_player_name_list = playerNicknameList_total[2]
	match_4_player_name_list = playerNicknameList_total[3]
	match_5_player_name_list = playerNicknameList_total[4]

	match_1_player_champ_list = playerChampionList_total[0]
	match_2_player_champ_list = playerChampionList_total[1]
	match_3_player_champ_list = playerChampionList_total[2]
	match_4_player_champ_list = playerChampionList_total[3]
	match_5_player_champ_list = playerChampionList_total[4]


	# 1) loop 10 times to make 10 match info htmls.
	for i in range(0, 5):

	    # Initialize
		grades = ["A", "A", "A", "A", "A"]

		# get general infos for the match.
		matchid = matchIDs.iloc[i].to_numpy()[0]
		summoner_name = getSummonerName(puuid)
		m_win, m_duration, m_kda, m_kda_p, m_cs, m_cs_pm, m_level, m_grade, m_champion_name, playerNicknameList, playerChampionList = getGeneralMatchData(matchIDs.iloc[i].to_numpy()[0], summoner_name)

		filename = "%s/%s.csv" % (puuid, matchid)
		df_val_user = ReadCSVtoDF(filename)

		df_val_diff, df_val_weight_multiplied, tier_name, tier_number, wins, losses, leaguePoints, df_val_user, df_val_tier, matchID = match_analysis(puuid, df_val_user, summoner_id, matchid)

		# lolaiScore for one match.
		lolaiScore_score = df_val_weight_multiplied.sum(axis=1)
		lolaiScore_score = lolaiScore_score.to_numpy()[0]

		# match radar chart data
		# chart data calculator

		# lolaiScore grouped as team, and all players.
		lolaiScore_List_team, lolaiScore_List_all = get_lolaiScore_List(matchid, df_val_tier)

		df_playerNicknameList = pd.DataFrame(playerNicknameList)
		df_playerNicknameList_team = pd.DataFrame(playerNicknameList[:5])

		df_lolaiScore_List_team = pd.DataFrame(lolaiScore_List_team)
		df_lolaiScore_List_all = pd.DataFrame(lolaiScore_List_all)

		df_lolaiScore_List_all_with_nickname = pd.concat([df_playerNicknameList, df_lolaiScore_List_all], axis=1)
		df_lolaiScore_List_team_with_nickname = pd.concat([df_playerNicknameList_team, df_lolaiScore_List_team], axis=1)

		# lolaiScore comparison
		# 1. 플레이어 인덱스 찾기  -> player_index_list
		# 2. 해당 인덱스와 숫자들 비교해서 몇번째로 큰지 알아내기
		player_index_inlist = player_index_list[i] - 1
		print("player_index_inlist : ", player_index_inlist)

		player_lolaiScore_place_in_all = 10
		for j in range(len(df_lolaiScore_List_all)):
			if j == player_index_inlist: pass
			else:
				if lolaiScore_List_all[j] < lolaiScore_List_all[player_index_inlist]:
					player_lolaiScore_place_in_all = player_lolaiScore_place_in_all - 1
					print(lolaiScore_List_all[j], " is smaller than ", lolaiScore_List_all[player_index_inlist], " so place is now : ", player_lolaiScore_place_in_all)

		player_lolaiScore_place_in_team = 5
		for p in range(len(df_lolaiScore_List_team)):
			if p == player_index_inlist: pass
			else:
				if player_index_inlist < 5 :
					if lolaiScore_List_team[p] < lolaiScore_List_all[player_index_inlist]:
						player_lolaiScore_place_in_team = player_lolaiScore_place_in_team - 1
						print(lolaiScore_List_team[p], " is smaller than ", lolaiScore_List_all[player_index_inlist], " so place is now : ", player_lolaiScore_place_in_team)

				else :
					if lolaiScore_List_all[p + 5] < lolaiScore_List_all[player_index_inlist]:
						player_lolaiScore_place_in_team = player_lolaiScore_place_in_team - 1
						print(lolaiScore_List_team[p], " is smaller than ", lolaiScore_List_all[player_index_inlist], " so place is now : ", player_lolaiScore_place_in_team)

		print("place in all : ")
		print(player_lolaiScore_place_in_all)
		print("place in team : ")
		print(player_lolaiScore_place_in_team)

		# lolaiScore to GRADE
		if lolaiScore_score > 5000:
			GRADE = "SSS"
		elif lolaiScore_score > 3000:
			GRADE = "SS"
		elif lolaiScore_score > 1000:
			GRADE = "A"
		elif lolaiScore_score > 0:
			GRADE = "B"
		elif lolaiScore_score > -1000:
			GRADE = "E"
		else:
			GRADE = "F"

		grades[i] = GRADE

		# comment for the GRADE calculated.
		grade_comment = LOLai_gradeCommentGenerator(GRADE)

		# # estimate tier based on the data.
		# tier_esti_name = tierEstimator(df_val_user)


		# Positive factors & Negative facotrs about the game

		# get best 5 parts / worst 5 parts with numbers.
		df_match_val_weight_multiplied_t = df_val_weight_multiplied.transpose()
		df_match_val_weight_multiplied_t = df_match_val_weight_multiplied_t.loc[(df_match_val_weight_multiplied_t!=0).any(axis=1)]
		print(df_match_val_weight_multiplied_t)

		df_match_val_weight_multiplied_t_s_p = df_match_val_weight_multiplied_t.sort_values(df_match_val_weight_multiplied_t.columns[0], ascending=False)
		df_match_val_weight_multiplied_t_s_n = df_match_val_weight_multiplied_t.sort_values(df_match_val_weight_multiplied_t.columns[0], ascending=True)

		df_match_val_weight_multiplied_t_s_p = df_match_val_weight_multiplied_t_s_p.iloc[:5]
		df_match_val_weight_multiplied_t_s_n = df_match_val_weight_multiplied_t_s_n.iloc[:5]

		df_match_val_weight_multiplied_t_s_p_copy = df_match_val_weight_multiplied_t_s_p
		df_match_val_weight_multiplied_t_s_n_copy = df_match_val_weight_multiplied_t_s_n

		df_match_val_weight_multiplied_t_s_p = df_match_val_weight_multiplied_t_s_p.transpose()
		df_match_val_weight_multiplied_t_s_n = df_match_val_weight_multiplied_t_s_n.transpose()

		# print(df_match_val_weight_multiplied_t_s_p.columns[0])

		# match the values with factors in html.

		# title
		p_f_1_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[0])
		p_f_2_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[1])
		p_f_3_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[2])
		p_f_4_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[3])
		p_f_5_t = factor_title_changer(df_match_val_weight_multiplied_t_s_p.columns[4])

		n_f_1_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[0])
		n_f_2_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[1])
		n_f_3_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[2])
		n_f_4_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[3])
		n_f_5_t = factor_title_changer(df_match_val_weight_multiplied_t_s_n.columns[4])

		print("pf1t : ", p_f_1_t)
		print("pf2t : ", p_f_2_t)
		print("pf3t : ", p_f_3_t)
		print("pf4t : ", p_f_4_t)
		print("pf5t : ", p_f_5_t)


		# value
		p_f_1_v = df_val_user[df_match_val_weight_multiplied_t_s_p.columns[0]].item()
		p_f_2_v = df_val_user[df_match_val_weight_multiplied_t_s_p.columns[1]].item()
		p_f_3_v = df_val_user[df_match_val_weight_multiplied_t_s_p.columns[2]].item()
		p_f_4_v = df_val_user[df_match_val_weight_multiplied_t_s_p.columns[3]].item()
		p_f_5_v = df_val_user[df_match_val_weight_multiplied_t_s_p.columns[4]].item()

		n_f_1_v = df_val_user[df_match_val_weight_multiplied_t_s_n.columns[0]].item()
		n_f_2_v = df_val_user[df_match_val_weight_multiplied_t_s_n.columns[1]].item()
		n_f_3_v = df_val_user[df_match_val_weight_multiplied_t_s_n.columns[2]].item()
		n_f_4_v = df_val_user[df_match_val_weight_multiplied_t_s_n.columns[3]].item()
		n_f_5_v = df_val_user[df_match_val_weight_multiplied_t_s_n.columns[4]].item()

		print("POSITIVE VALUES : ", p_f_1_v, p_f_2_v, p_f_3_v, p_f_4_v, p_f_5_v)
		print("NEGATIVE VALUES : ", n_f_1_v, n_f_2_v, n_f_3_v, n_f_4_v, n_f_5_v)


		# normalization of p_f and n_f
		p_f_list = []
		n_f_list = []

		p_f_list.append([p_f_1_v, p_f_2_v, p_f_3_v, p_f_4_v, p_f_5_v, 0])
		n_f_list.append([n_f_1_v, n_f_2_v, n_f_3_v, n_f_4_v, n_f_5_v, 0])

		normalized_p_f_list = html_maker.min_max_normalize(p_f_list)
		normalized_n_f_list = html_maker.min_max_normalize(n_f_list)

		for num in range(len(normalized_p_f_list)) :
			if normalized_p_f_list[num] < 1 and normalized_p_f_list[num] < 0.05 : normalized_p_f_list[num] = normalized_p_f_list[num] + 20
			if normalized_p_f_list[num] < 1 and normalized_p_f_list[num] > 0.05 : normalized_p_f_list[num] = normalized_p_f_list[num] + 35
			if normalized_n_f_list[num] < 1 and normalized_n_f_list[num] < 0.05: normalized_n_f_list[num] = normalized_n_f_list[num] + 20
			if normalized_n_f_list[num] < 1 and normalized_n_f_list[num] > 0.05: normalized_n_f_list[num] = normalized_n_f_list[num] + 35

		normalized_p_f_1_v = normalized_p_f_list[0]
		normalized_p_f_2_v = normalized_p_f_list[1]
		normalized_p_f_3_v = normalized_p_f_list[2]
		normalized_p_f_4_v = normalized_p_f_list[3]
		normalized_p_f_5_v = normalized_p_f_list[4]

		normalized_n_f_1_v = normalized_n_f_list[0]
		normalized_n_f_2_v = normalized_n_f_list[1]
		normalized_n_f_3_v = normalized_n_f_list[2]
		normalized_n_f_4_v = normalized_n_f_list[3]
		normalized_n_f_5_v = normalized_n_f_list[4]

		print("2 POSITIVE VALUES : ", normalized_p_f_1_v, normalized_p_f_2_v, normalized_p_f_3_v, normalized_p_f_4_v, normalized_p_f_5_v)
		print("2 NEGATIVE VALUES : ", normalized_n_f_1_v, normalized_n_f_2_v, normalized_n_f_3_v, normalized_n_f_4_v, normalized_n_f_5_v)


		# # grade
		# p_f_1_g = grade_checker_factors(df_val_user[df_match_val_weight_multiplied_t_s_p.columns[0]].item())
		# p_f_2_g = grade_checker_factors(df_val_user[df_match_val_weight_multiplied_t_s_p.columns[1]].item())
		# p_f_3_g = grade_checker_factors(df_val_user[df_match_val_weight_multiplied_t_s_p.columns[2]].item())
		#
		# n_f_1_g = grade_checker_factors(df_val_user[df_match_val_weight_multiplied_t_s_n.columns[0]].item())
		# n_f_2_g = grade_checker_factors(df_val_user[df_match_val_weight_multiplied_t_s_n.columns[1]].item())
		# n_f_3_g = grade_checker_factors(df_val_user[df_match_val_weight_multiplied_t_s_n.columns[2]].item())
		#
		# # tier-average
		# p_f_1_a = df_val_tier[df_match_val_weight_multiplied_t_s_p.columns[0]].item()
		# p_f_2_a = df_val_tier[df_match_val_weight_multiplied_t_s_p.columns[1]].item()
		# p_f_3_a = df_val_tier[df_match_val_weight_multiplied_t_s_p.columns[2]].item()
		#
		# n_f_1_a = df_val_tier[df_match_val_weight_multiplied_t_s_n.columns[0]].item()
		# n_f_2_a = df_val_tier[df_match_val_weight_multiplied_t_s_n.columns[1]].item()
		# n_f_3_a = df_val_tier[df_match_val_weight_multiplied_t_s_n.columns[2]].item()
		#
		#
		# # ## victory contribution value getter
		p_f_1_v_c = df_match_val_weight_multiplied_t_s_p_copy.iloc[0].item()
		p_f_2_v_c = df_match_val_weight_multiplied_t_s_p_copy.iloc[1].item()
		p_f_3_v_c = df_match_val_weight_multiplied_t_s_p_copy.iloc[2].item()
		p_f_4_v_c = df_match_val_weight_multiplied_t_s_p_copy.iloc[2].item()
		p_f_5_v_c = df_match_val_weight_multiplied_t_s_p_copy.iloc[2].item()

		n_f_1_v_c = df_match_val_weight_multiplied_t_s_n_copy.iloc[0].item()
		n_f_2_v_c = df_match_val_weight_multiplied_t_s_n_copy.iloc[1].item()
		n_f_3_v_c = df_match_val_weight_multiplied_t_s_n_copy.iloc[2].item()
		n_f_4_v_c = df_match_val_weight_multiplied_t_s_n_copy.iloc[2].item()
		n_f_5_v_c = df_match_val_weight_multiplied_t_s_n_copy.iloc[2].item()

		p_factor_impact = (p_f_1_v_c + p_f_2_v_c + p_f_3_v_c + p_f_4_v_c + p_f_5_v_c) / 5
		n_factor_impact = (n_f_1_v_c + n_f_2_v_c + n_f_3_v_c + n_f_4_v_c + n_f_5_v_c) / 5

		normalization_factor_list = []
		normalization_factor_list.append([p_factor_impact, n_factor_impact, 0, 5000])
		normalization_factor_list = html_maker.min_max_normalize(normalization_factor_list)

		normalized_p_factor = normalization_factor_list[0]
		normalized_n_factor = normalization_factor_list[1]
		normalized_n_factor = normalized_n_factor*1000

		if normalized_p_factor > 100 :
			normalized_p_factor = 100
		elif normalized_p_factor < 0 :
			normalized_p_factor = 0

		if normalized_n_factor > 100 :
			normalized_n_factor = 100
		elif normalized_n_factor < 0 :
			normalized_n_factor = 0

		# get timeline data
		array_player_gold_timeline, array_team_gold_timeline, array_oppo_gold_timeline, array_player_damage_dealt_timeline, array_team_damage_dealt_timeline, array_oppo_damage_dealt_timeline, array_level_timeline, timeline_length, array_player_minion_timeline = getMatchTimelineInfo(matchid, player_index_list[i])

		print("array player gold timeline : ", array_player_gold_timeline)

		# match infos
		# get match data from the match id list
		m_1_win, m_1_duration, m_1_kda, m_1_kda_percentage, m_1_total_cs, m_1_cs_per_minute, m_1_level, m_1_grade, m_1_champ, m1_playerNicknameList, m1_playerChampionList = getGeneralMatchData(matchIDs.iloc[0].to_numpy()[0], summoner_name)
		m_2_win, m_2_duration, m_2_kda, m_2_kda_percentage, m_2_total_cs, m_2_cs_per_minute, m_2_level, m_2_grade, m_2_champ, m2_playerNicknameList, m2_playerChampionList = getGeneralMatchData(matchIDs.iloc[1].to_numpy()[0], summoner_name)
		m_3_win, m_3_duration, m_3_kda, m_3_kda_percentage, m_3_total_cs, m_3_cs_per_minute, m_3_level, m_3_grade, m_3_champ, m3_playerNicknameList, m3_playerChampionList = getGeneralMatchData(matchIDs.iloc[2].to_numpy()[0], summoner_name)
		m_4_win, m_4_duration, m_4_kda, m_4_kda_percentage, m_4_total_cs, m_4_cs_per_minute, m_4_level, m_4_grade, m_4_champ, m4_playerNicknameList, m4_playerChampionList = getGeneralMatchData(matchIDs.iloc[3].to_numpy()[0], summoner_name)
		m_5_win, m_5_duration, m_5_kda, m_5_kda_percentage, m_5_total_cs, m_5_cs_per_minute, m_5_level, m_5_grade, m_5_champ, m5_playerNicknameList, m5_playerChampionList = getGeneralMatchData(matchIDs.iloc[4].to_numpy()[0], summoner_name)


		# chart data calculator
		normalized_list_gold, normalized_list_alive, normalized_list_battle, normalized_list_growth, normalized_list_object = chartDataCalculator(df_val_user, df_val_tier)

		chart_gold_p_calculated = normalized_list_gold[0]
		chart_gold_tier_calculated= normalized_list_gold[1]

		chart_alive_p_calculated= normalized_list_alive[0]
		chart_alive_tier_calculated= normalized_list_alive[1]

		chart_battle_p_calculated= normalized_list_battle[0]
		chart_battle_tier_calculated= normalized_list_battle[1]

		chart_growth_p_calculated= normalized_list_growth[0]
		chart_growth_tier_calculated= normalized_list_growth[1]

		chart_object_p_calculated= normalized_list_object[0]
		chart_object_tier_calculated= normalized_list_object[1]

		# recent match history
		win_history_list = [m_1_win, m_2_win, m_3_win, m_4_win, m_5_win]
		match_color_list = ["#FFCCCC", "#FFCCCC","#FFCCCC","#FFCCCC","#FFCCCC","#FFCCCC"] #last one is the analyzed match.
		str1 = ""
		rwr_win = 0
		rwr_lose = 0
		for i in range(len(win_history_list)) :
			if win_history_list[i] == True :
				rwr_win = rwr_win + 1
				str1 = str1 + "승"
				win_history_list[i] = "승리"
				match_color_list[i] = "#add0f7"
			else :
				rwr_lose = rwr_lose + 1
				str1 = str1 + "패"
				win_history_list[i] = "패배"

		recent_match_history_data = str1
		recent_win_rate_data = round(rwr_win/5 * 100, 1)

		if m_win == True :
			m_win = "승리"
			match_color_list[5] = "#add0f7"
		else :
			m_win = "패배"



		###########################################################################
		###########################################################################
		# string to make a html file.
		html_str = str(html_maker.html_page(2))
		html_str = html_str.format(

		    #####################
		    # BASIC INFORMATION #
		    #####################
		    nickname=summoner_name,
		    update_date=time_now,
		    tier_name=tier_name,
		    tier_num=tier_number,
		    lp=leaguePoints,
		    total_match_number=match,
		    wins=wins,
		    losses=losses,
		    win_rate=round(wrate, 1),
		    lolai_score_letter=GRADE,
		    lolai_score_number=round(lolaiScore_score),
		    lolai_score_comment=LOLai_gradeCommentGenerator(GRADE),

			## 임시 - 나중에 수정 필요
		    # recent_match_history=html_maker.read_history("getwinloss"),
		    # recent_win_rate=html_maker.read_history("getwinrate"),
			recent_match_history=recent_match_history_data,
		    recent_win_rate= recent_win_rate_data,

		    ##############################
		    # SELECTED MATCH INFORMATION #
		    ##############################
		    match_bool_win=m_win,
		    match_length=str(int(m_duration / 60 % 60)) + "분 " + str(m_duration % 60) + "초",
		    match_champ=m_champion_name,
			match_level=m_level,
		    match_kda=m_kda,
		    match_kda_percentage=round(m_kda_p, 1),
		    match_cs=m_cs,
		    match_cs_per_minuite=round(m_cs_pm, 2),
		    match_player_1_champ=playerChampionList[0],
		    match_player_1_nickname=playerNicknameList[0],
		    match_player_2_champ=playerChampionList[1],
		    match_player_2_nickname=playerNicknameList[1],
		    match_player_3_champ=playerChampionList[2],
		    match_player_3_nickname=playerNicknameList[2],
		    match_player_4_champ=playerChampionList[3],
		    match_player_4_nickname=playerNicknameList[3],
		    match_player_5_champ=playerChampionList[4],
		    match_player_5_nickname=playerNicknameList[4],
		    match_player_6_champ=playerChampionList[5],
		    match_player_6_nickname=playerNicknameList[5],
		    match_player_7_champ=playerChampionList[6],
		    match_player_7_nickname=playerNicknameList[6],
		    match_player_8_champ=playerChampionList[7],
		    match_player_8_nickname=playerNicknameList[7],
		    match_player_9_champ=playerChampionList[8],
		    match_player_9_nickname=playerNicknameList[8],
		    match_player_10_champ=playerChampionList[9],
		    match_player_10_nickname=playerNicknameList[9],
		    match_lolai_score_letter=GRADE,

		    ##############################
		    # MATCH ANALYSIS INFORMATION #
		    ##############################
		    match_lolai_score_number=round(lolaiScore_score),
		    match_lolai_score_comment=grade_comment,

		    # bar chart
		    match_lolai_score_place_in_team=player_lolaiScore_place_in_team,
		    match_lolai_score_place_in_all=player_lolaiScore_place_in_all,

		    # # time flow chart
		    # gamelength_onefive=m_duration / 5 * 1,
		    # gamelength_twofive=m_duration / 5 * 2,
		    # gamelength_threefive=m_duration / 5 * 3,
		    # gamelength_fourfive=m_duration / 5 * 4,
		    # gamelength_fivefive=m_duration,
		    # goldchart_comment = "",
		    # kdachart_comment = "",

		    # bottom box conclusion
		    positive_factor_impact_percentage= round(normalized_p_factor, 1),
		    negative_factor_impact_percentage= round(normalized_n_factor, 1),

		    ##################################
		    # MATCH PARTICIPANTS INFORMATION #
		    ##################################

		    # match 1 information
		    match_1_bool_win=win_history_list[0],
		    match_1_length=str(int(m_1_duration / 60 % 60)) + "분 " + str(m_1_duration % 60) + "초",
		    match_1_kda=m_1_kda,
		    match_1_kda_percentage=round(m_1_kda_percentage, 1),
		    match_1_cs=m_1_total_cs,
		    match_1_cs_per_minuite=round(m_1_cs_per_minute, 2),
		    match_1_level=m_1_level,
		    match_1_player_1=match_1_player_name_list[0],
		    match_1_player_2=match_1_player_name_list[1],
		    match_1_player_3=match_1_player_name_list[2],
		    match_1_player_4=match_1_player_name_list[3],
		    match_1_player_5=match_1_player_name_list[4],
		    match_1_player_6=match_1_player_name_list[5],
		    match_1_player_7=match_1_player_name_list[6],
		    match_1_player_8=match_1_player_name_list[7],
		    match_1_player_9=match_1_player_name_list[8],
		    match_1_player_10=match_1_player_name_list[9],

		    match_1_player_1_champ=match_1_player_champ_list[0],
		    match_1_player_2_champ=match_1_player_champ_list[1],
		    match_1_player_3_champ=match_1_player_champ_list[2],
		    match_1_player_4_champ=match_1_player_champ_list[3],
		    match_1_player_5_champ=match_1_player_champ_list[4],
		    match_1_player_6_champ=match_1_player_champ_list[5],
		    match_1_player_7_champ=match_1_player_champ_list[6],
		    match_1_player_8_champ=match_1_player_champ_list[7],
		    match_1_player_9_champ=match_1_player_champ_list[8],
		    match_1_player_10_champ=match_1_player_champ_list[9],

		    match_1_lolai_score_letter=grades[0],
		    match_1_champ=m_1_champ,
			match_1_match_number = matchIDs.iloc[0].to_numpy()[0],

		    # match 2 information
		    match_2_bool_win=win_history_list[1],
		    match_2_length=str(int(m_2_duration / 60 % 60)) + "분 " + str(m_2_duration % 60) + "초",
		    match_2_kda=m_2_kda,
		    match_2_kda_percentage=round(m_2_kda_percentage, 1),
		    match_2_cs=m_2_total_cs,
		    match_2_cs_per_minuite=round(m_2_cs_per_minute, 2),
		    match_2_level=m_2_level,
		    match_2_player_1=match_2_player_name_list[0],
		    match_2_player_2=match_2_player_name_list[1],
		    match_2_player_3=match_2_player_name_list[2],
		    match_2_player_4=match_2_player_name_list[3],
		    match_2_player_5=match_2_player_name_list[4],
		    match_2_player_6=match_2_player_name_list[5],
		    match_2_player_7=match_2_player_name_list[6],
		    match_2_player_8=match_2_player_name_list[7],
		    match_2_player_9=match_2_player_name_list[8],
		    match_2_player_10=match_2_player_name_list[9],

		    match_2_player_1_champ=match_2_player_champ_list[0],
		    match_2_player_2_champ=match_2_player_champ_list[1],
		    match_2_player_3_champ=match_2_player_champ_list[2],
		    match_2_player_4_champ=match_2_player_champ_list[3],
		    match_2_player_5_champ=match_2_player_champ_list[4],
		    match_2_player_6_champ=match_2_player_champ_list[5],
		    match_2_player_7_champ=match_2_player_champ_list[6],
		    match_2_player_8_champ=match_2_player_champ_list[7],
		    match_2_player_9_champ=match_2_player_champ_list[8],
		    match_2_player_10_champ=match_2_player_champ_list[9],

		    match_2_lolai_score_letter=grades[1],
		    match_2_champ=m_2_champ,
			match_2_match_number = matchIDs.iloc[1].to_numpy()[0],

		    # match 3 information
		    match_3_bool_win=win_history_list[2],
		    match_3_length=str(int(m_3_duration / 60 % 60)) + "분 " + str(m_3_duration % 60) + "초",
		    match_3_kda=m_3_kda,
		    match_3_kda_percentage=round(m_3_kda_percentage, 1),
		    match_3_cs=m_3_total_cs,
		    match_3_cs_per_minuite=round(m_3_cs_per_minute, 2),
		    match_3_level=m_3_level,
		    match_3_player_1=match_3_player_name_list[0],
		    match_3_player_2=match_3_player_name_list[1],
		    match_3_player_3=match_3_player_name_list[2],
		    match_3_player_4=match_3_player_name_list[3],
		    match_3_player_5=match_3_player_name_list[4],
		    match_3_player_6=match_3_player_name_list[5],
		    match_3_player_7=match_3_player_name_list[6],
		    match_3_player_8=match_3_player_name_list[7],
		    match_3_player_9=match_3_player_name_list[8],
		    match_3_player_10=match_3_player_name_list[9],

		    match_3_player_1_champ=match_3_player_champ_list[0],
		    match_3_player_2_champ=match_3_player_champ_list[1],
		    match_3_player_3_champ=match_3_player_champ_list[2],
		    match_3_player_4_champ=match_3_player_champ_list[3],
		    match_3_player_5_champ=match_3_player_champ_list[4],
		    match_3_player_6_champ=match_3_player_champ_list[5],
		    match_3_player_7_champ=match_3_player_champ_list[6],
		    match_3_player_8_champ=match_3_player_champ_list[7],
		    match_3_player_9_champ=match_3_player_champ_list[8],
		    match_3_player_10_champ=match_3_player_champ_list[9],

		    match_3_lolai_score_letter=grades[2],
		    match_3_champ=m_3_champ,
			match_3_match_number = matchIDs.iloc[2].to_numpy()[0],

		    # match 4 information
		    match_4_bool_win=win_history_list[3],
		    match_4_length=str(int(m_4_duration / 60 % 60)) + "분 " + str(m_4_duration % 60) + "초",
		    match_4_kda=m_4_kda,
		    match_4_kda_percentage=round(m_4_kda_percentage, 1),
		    match_4_cs=m_4_total_cs,
		    match_4_cs_per_minuite=round(m_4_cs_per_minute, 2),
		    match_4_level=m_4_level,
		    match_4_player_1=match_4_player_name_list[0],
		    match_4_player_2=match_4_player_name_list[1],
		    match_4_player_3=match_4_player_name_list[2],
		    match_4_player_4=match_4_player_name_list[3],
		    match_4_player_5=match_4_player_name_list[4],
		    match_4_player_6=match_4_player_name_list[5],
		    match_4_player_7=match_4_player_name_list[6],
		    match_4_player_8=match_4_player_name_list[7],
		    match_4_player_9=match_4_player_name_list[8],
		    match_4_player_10=match_4_player_name_list[9],

		    match_4_player_1_champ=match_4_player_champ_list[0],
		    match_4_player_2_champ=match_4_player_champ_list[1],
		    match_4_player_3_champ=match_4_player_champ_list[2],
		    match_4_player_4_champ=match_4_player_champ_list[3],
		    match_4_player_5_champ=match_4_player_champ_list[4],
		    match_4_player_6_champ=match_4_player_champ_list[5],
		    match_4_player_7_champ=match_4_player_champ_list[6],
		    match_4_player_8_champ=match_4_player_champ_list[7],
		    match_4_player_9_champ=match_4_player_champ_list[8],
		    match_4_player_10_champ=match_4_player_champ_list[9],

		    match_4_lolai_score_letter=grades[3],
		    match_4_champ=m_4_champ,
			match_4_match_number = matchIDs.iloc[3].to_numpy()[0],

		    # match 5 information
		    match_5_bool_win=win_history_list[4],
		    match_5_length=str(int(m_5_duration / 60 % 60)) + "분 " + str(m_5_duration % 60) + "초",
		    match_5_kda=m_5_kda,
		    match_5_kda_percentage=round(m_5_kda_percentage, 1),
		    match_5_cs=m_5_total_cs,
		    match_5_cs_per_minuite=round(m_5_cs_per_minute, 2),
		    match_5_level=m_5_level,
		    match_5_player_1=match_5_player_name_list[0],
		    match_5_player_2=match_5_player_name_list[1],
		    match_5_player_3=match_5_player_name_list[2],
		    match_5_player_4=match_5_player_name_list[3],
		    match_5_player_5=match_5_player_name_list[4],
		    match_5_player_6=match_5_player_name_list[5],
		    match_5_player_7=match_5_player_name_list[6],
		    match_5_player_8=match_5_player_name_list[7],
		    match_5_player_9=match_5_player_name_list[8],
		    match_5_player_10=match_5_player_name_list[9],

		    match_5_player_1_champ=match_5_player_champ_list[0],
		    match_5_player_2_champ=match_5_player_champ_list[1],
		    match_5_player_3_champ=match_5_player_champ_list[2],
		    match_5_player_4_champ=match_5_player_champ_list[3],
		    match_5_player_5_champ=match_5_player_champ_list[4],
		    match_5_player_6_champ=match_5_player_champ_list[5],
		    match_5_player_7_champ=match_5_player_champ_list[6],
		    match_5_player_8_champ=match_5_player_champ_list[7],
		    match_5_player_9_champ=match_5_player_champ_list[8],
		    match_5_player_10_champ=match_5_player_champ_list[9],

		    match_5_lolai_score_letter=grades[4],
		    match_5_champ=m_5_champ,
			match_5_match_number = matchIDs.iloc[4].to_numpy()[0],

			match_box_color = match_color_list[5],
			match_1_box_color = match_color_list[0],
			match_2_box_color = match_color_list[1],
			match_3_box_color = match_color_list[2],
			match_4_box_color = match_color_list[3],
			match_5_box_color = match_color_list[4],

		    #####################
		    # CHART INFORMATION #
		    #####################

			# radar chart
			player_growth_stat = chart_growth_p_calculated,
			player_gold_stat = chart_gold_p_calculated,
			player_alive_stat = chart_alive_p_calculated,
			player_battle_stat = chart_battle_p_calculated,
			player_object_stat = chart_object_p_calculated,

			avg_growth_stat = chart_growth_tier_calculated,
			avg_gold_stat = chart_gold_tier_calculated,
			avg_alive_stat = chart_alive_tier_calculated,
			avg_battle_stat = chart_battle_tier_calculated,
			avg_object_stat = chart_object_tier_calculated,

		    # bar chart
		    team_p1_nickname=playerNicknameList[0],
		    team_p2_nickname=playerNicknameList[1],
		    team_p3_nickname=playerNicknameList[2],
		    team_p4_nickname=playerNicknameList[3],
		    team_p5_nickname=playerNicknameList[4],
		    oppo_p1_nickname=playerNicknameList[5],
		    oppo_p2_nickname=playerNicknameList[6],
		    oppo_p3_nickname=playerNicknameList[7],
		    oppo_p4_nickname=playerNicknameList[8],
		    oppo_p5_nickname=playerNicknameList[9],

		    player_lolai=round(lolaiScore_List_all[0]),
		    team_p2_lolai=round(lolaiScore_List_all[1]),
		    team_p3_lolai=round(lolaiScore_List_all[2]),
		    team_p4_lolai=round(lolaiScore_List_all[3]),
		    team_p5_lolai=round(lolaiScore_List_all[4]),
		    oppo_p1_lolai=round(lolaiScore_List_all[5]),
		    oppo_p2_lolai=round(lolaiScore_List_all[6]),
		    oppo_p3_lolai=round(lolaiScore_List_all[7]),
		    oppo_p4_lolai=round(lolaiScore_List_all[8]),
		    oppo_p5_lolai=round(lolaiScore_List_all[9]),


		    # line chart - gold
		    player_gold_at_onefive=array_player_gold_timeline[0],
		    player_gold_at_twofive=array_player_gold_timeline[round(timeline_length / 5 * 2)],
		    player_gold_at_threefive=array_player_gold_timeline[round(timeline_length / 5 * 3)],
		    player_gold_at_fourfive=array_player_gold_timeline[round( timeline_length / 5 * 4)],
		    player_gold_at_fivefive=array_player_gold_timeline[timeline_length-1],

		    team_gold_at_onefive=array_team_gold_timeline[0],
		    team_gold_at_twofive=array_team_gold_timeline[round(timeline_length / 5 * 2)],
		    team_gold_at_threefive=array_team_gold_timeline[round(timeline_length / 5 * 3)],
		    team_gold_at_fourfive=array_team_gold_timeline[round(timeline_length / 5 * 4)],
		    team_gold_at_fivefive=array_team_gold_timeline[timeline_length-1],

		    oppo_gold_at_onefive=array_oppo_gold_timeline[0],
		    oppo_gold_at_twofive=array_oppo_gold_timeline[round(timeline_length / 5 * 2)],
		    oppo_gold_at_threefive=array_oppo_gold_timeline[round(timeline_length / 5 * 3)],
		    oppo_gold_at_fourfive=array_oppo_gold_timeline[round(timeline_length / 5 * 4)],
		    oppo_gold_at_fivefive=array_oppo_gold_timeline[timeline_length-1],

		    # line chart - level/damage dealt
		    player_damage_dealt_at_onefive=array_player_damage_dealt_timeline[0],
		    player_damage_dealt_at_twofive=array_player_damage_dealt_timeline[round(timeline_length / 5 * 2)],
		    player_damage_dealt_at_threefive=array_player_damage_dealt_timeline[round(timeline_length / 5 * 3)],
		    player_damage_dealt_at_fourfive=array_player_damage_dealt_timeline[round(timeline_length / 5 * 4)],
		    player_damage_dealt_at_fivefive=array_player_damage_dealt_timeline[timeline_length-1],

		    team_damage_dealt_at_onefive=array_team_damage_dealt_timeline[0],
		    team_damage_dealt_at_twofive=array_team_damage_dealt_timeline[round(timeline_length / 5 * 2)],
		    team_damage_dealt_at_threefive=array_team_damage_dealt_timeline[round(timeline_length / 5 * 3)],
		    team_damage_dealt_at_fourfive=array_team_damage_dealt_timeline[round(timeline_length / 5 * 4)],
		    team_damage_dealt_at_fivefive=array_team_damage_dealt_timeline[timeline_length-1],

		    oppo_damage_dealt_at_onefive=array_oppo_damage_dealt_timeline[0],
		    oppo_damage_dealt_at_twofive=array_oppo_damage_dealt_timeline[round(timeline_length / 5 * 2)],
		    oppo_damage_dealt_at_threefive=array_oppo_damage_dealt_timeline[round(timeline_length / 5 * 3)],
		    oppo_damage_dealt_at_fourfive=array_oppo_damage_dealt_timeline[round(timeline_length / 5 * 4)],
		    oppo_damage_dealt_at_fivefive=array_oppo_damage_dealt_timeline[timeline_length-1],

		    level_at_onefive=array_level_timeline[0],
		    level_at_twofive=array_level_timeline[round(timeline_length / 5 * 2)],
		    level_at_threefive=array_level_timeline[round(timeline_length / 5 * 3)],
		    level_at_fourfive=array_level_timeline[round(timeline_length / 5 * 4)],
		    level_at_fivefive=array_level_timeline[timeline_length-1],

			cs_at_onefive=array_player_minion_timeline[0],
		    cs_at_twofive=array_player_minion_timeline[round(timeline_length / 5 * 2)],
		    cs_at_threefive=array_player_minion_timeline[round(timeline_length / 5 * 3)],
		    cs_at_fourfive=array_player_minion_timeline[round(timeline_length / 5 * 4)],
		    cs_at_fivefive=array_player_minion_timeline[timeline_length-1],

		    gamelength_onefive="0",
		    gamelength_twofive=round(timeline_length / 5 * 2),
		    gamelength_threefive=round(timeline_length / 5 * 3),
		    gamelength_fourfive=round(timeline_length / 5 * 4),
		    gamelength_fivefive=timeline_length-1,

		    # polar chart
		    positive_factor_label_1=p_f_1_t,
		    positive_factor_label_2=p_f_2_t,
		    positive_factor_label_3=p_f_3_t,
		    positive_factor_label_4=p_f_4_t,
		    positive_factor_label_5=p_f_5_t,

		    positive_factor_data_1=normalized_p_f_1_v,
		    positive_factor_data_2=normalized_p_f_2_v,
		    positive_factor_data_3=normalized_p_f_3_v,
		    positive_factor_data_4=normalized_p_f_4_v,
		    positive_factor_data_5=normalized_p_f_5_v,

		    negative_factor_label_1=n_f_1_t,
		    negative_factor_label_2=n_f_2_t,
		    negative_factor_label_3=n_f_3_t,
		    negative_factor_label_4=n_f_4_t,
		    negative_factor_label_5=n_f_5_t,

		    negative_factor_data_1=normalized_n_f_1_v,
		    negative_factor_data_2=normalized_n_f_2_v,
		    negative_factor_data_3=normalized_n_f_3_v,
		    negative_factor_data_4=normalized_n_f_4_v,
		    negative_factor_data_5=normalized_n_f_5_v,

		    ###################
		    # ADs INFORMATION #
		    ###################
		    AD1_h="1", AD2_h="2"
		)

		filename = r"%s\match_%s_info.html" % (puuid, matchID)
		Html_file = open(filename, "w", encoding='utf8')
		Html_file.write(html_str)
		Html_file.close()

		print(i, "- match info html completed.")

	return grades, recent_match_history_data,recent_win_rate_data

#########################################################################
#########################################################################


if __name__ == "__main__":

	# argv 1: puuid
	#puuid = "HnhJr6GllSp6ia70JHqNaaOiWIbaeRg8w0BLRe14vIoTq28UtrsFVkvsYe8QZFNAA6Oqcq7Gdf8z0A"
	#summoner_name = "테스트nickname"
	puuid = sys.argv[1]
	summoner_name = sys.argv[2]

	try:
		os.mkdir(puuid)
	except:
		print("dir already exists.")

	make_user_info_html(puuid, summoner_name)
