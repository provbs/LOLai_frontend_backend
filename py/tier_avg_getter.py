################################################################################
############################## tier_avg_getter.py ##############################
####################### Runs one times for one new patch #######################
######################### Get average tier match data ##########################
################################################################################

import requests
import numpy as np
import pandas as pd
import json

# for time delay (only use on beta version, will be removed after riot API usage approved.)
import time

apiDefault = {
    'region': 'https://kr.api.riotgames.com',  # kr server.
    'key': 'RGAPI-393cbd2e-ba9f-4105-85c8-18a64972160d',  # API KEY - from riot developers portal.
    'summonerName': 'PROvbs',  # default with my nickname.
}


## get match ids for the tier players.(100 people for high ranks, 100 total for low ranks)
def get_Match_IDs(tier_name):
	############################### CHALLENGER ###############################
	##########################################################################
	if tier_name == "CHALLENGER":
		# get all user list of challenger.
		url = F"{apiDefault['region']}/lol/league/v4/challengerleagues/by-queue/{'RANKED_SOLO_5x5'}?api_key={apiDefault['key']}"
		req = requests.get(url)
		Challenger_League_Users_List = json.loads(req.text)
		Challenger_League_Users_List_entries = Challenger_League_Users_List["entries"]
		Challenger_League_Users_List_entries = pd.DataFrame(Challenger_League_Users_List_entries)
		tier_list = Challenger_League_Users_List["tier"]

		Challenger_League_Users_List_tiers =[]
		for i in range(len(Challenger_League_Users_List_entries)):
		    Challenger_League_Users_List_tiers.append(tier_list)
		Challenger_League_Users_List_tiers = pd.DataFrame(Challenger_League_Users_List_tiers, columns=['tier'])
		Challenger_League_Users_List = pd.concat([Challenger_League_Users_List_entries,Challenger_League_Users_List_tiers],axis=1)
		# save user list to dataframe
		Challenger_League_Users_List_DF = pd.DataFrame(Challenger_League_Users_List)
		Challenger_League_Users_List_DF = Challenger_League_Users_List_DF.sort_values(by='leaguePoints' ,ascending=False)
		Challenger_League_Users_List_DF = Challenger_League_Users_List_DF.reset_index()


		# Cut only 100 users from the user list.
		Challenger_League_Users_List_DF = Challenger_League_Users_List_DF[:100]
		print("Challenger User list Dataframe ready, length : ", len(Challenger_League_Users_List_DF), " users.")

		## save as .csv file for LOLPAGO learning.

		# get puuids from the user list. (summoner name)
		Challenger_League_Users_List_DF_summonerName = pd.DataFrame(Challenger_League_Users_List_DF['summonerName'])
		Challenger_League_Users_Puuids = []
		for i in range(len(Challenger_League_Users_List_DF_summonerName)):
		    while True:
		        try:
		            url = F"{apiDefault['region']}/lol/summoner/v4/summoners/by-name/{Challenger_League_Users_List_DF_summonerName.loc[i].to_numpy()[0]}?api_key={apiDefault['key']}"
		            req = requests.get(url)
		            Challenger_League_Users_Puuids_temp = json.loads(req.text)
		            Challenger_League_Users_Puuids.append(Challenger_League_Users_Puuids_temp['puuid'])
		            break
		        except KeyError:
		            break
		    time.sleep(1)
		print(tier_name,  " User PUUID list Dataframe ready, length : ", len(Challenger_League_Users_Puuids), " users.")

		# get match IDs from the puuid list.
		Challenger_League_Users_MatchID = []
		for n in range(len(Challenger_League_Users_Puuids)):
		    url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/by-puuid/{Challenger_League_Users_Puuids[n]}/ids?type=ranked&start=0&count=10&api_key={apiDefault['key']}"
		    req = requests.get(url)
		    Challenger_League_Users_MatchID_temp = json.loads(req.text)
		    Challenger_League_Users_MatchID.append(Challenger_League_Users_MatchID_temp)
		    time.sleep(1)

		Challenger_League_Users_MatchID = sum(Challenger_League_Users_MatchID, [])
		print("Challenger User MatchID list Dataframe ready, length : ", len(Challenger_League_Users_MatchID), " match ids.")
		# final result return as "MatchIDs".
		MatchIDs = Challenger_League_Users_MatchID


	############################## GRAND MASTER ##############################
	##########################################################################
	elif tier_name == "GRANDMASTER":

		url = F"{apiDefault['region']}/lol/league/v4/grandmasterleagues/by-queue/{'RANKED_SOLO_5x5'}?api_key={apiDefault['key']}"
		req = requests.get(url)
		Grand_Master_League_Users_List = json.loads(req.text)
		Grand_Master_League_Users_List_entries = Grand_Master_League_Users_List["entries"]
		Grand_Master_League_Users_List_entries = pd.DataFrame(Grand_Master_League_Users_List_entries)
		tier_list = Grand_Master_League_Users_List["tier"]

		Grand_Master_League_Users_List_tiers =[]
		for i in range(len(Grand_Master_League_Users_List_entries)):
		    Grand_Master_League_Users_List_tiers.append(tier_list)
		Grand_Master_League_Users_List_tiers = pd.DataFrame(Grand_Master_League_Users_List_tiers, columns=['tier'])

		Grand_Master_League_Users_List = pd.concat([Grand_Master_League_Users_List_entries,Grand_Master_League_Users_List_tiers],axis=1)

		Grand_Master_League_Users_List_DF = pd.DataFrame(Grand_Master_League_Users_List)
		Grand_Master_League_Users_List_DF = Grand_Master_League_Users_List_DF.sort_values(by='leaguePoints' ,ascending=False)
		Grand_Master_League_Users_List_DF = Grand_Master_League_Users_List_DF.reset_index()



		# Cut only 100 users from the user list.
		Grand_Master_League_Users_List_DF = Grand_Master_League_Users_List_DF[:100]
		print("Grand Master User list Dataframe ready, length : ", len(Grand_Master_League_Users_List_DF), " users.")
		## save as .csv file for LOLPAGO learning.

		# get puuids from the user list. (summoner name)
		Grand_Master_League_Users_List_DF_summonerName = pd.DataFrame(Grand_Master_League_Users_List_DF['summonerName'])

		Grand_Master_League_Users_Puuids = []

		for i in range(len(Grand_Master_League_Users_List_DF_summonerName)):
			while True:
				try:
					url = F"{apiDefault['region']}/lol/summoner/v4/summoners/by-name/{Grand_Master_League_Users_List_DF_summonerName.loc[i].to_numpy()[0]}?api_key={apiDefault['key']}"
					req = requests.get(url)
					Grand_Master_League_Users_Puuids_temp = json.loads(req.text)
					Grand_Master_League_Users_Puuids.append(Grand_Master_League_Users_Puuids_temp['puuid'])
					break
				except:
					break

				time.sleep(1)

		# get match IDs from the puuid list.
		Grand_Master_League_Users_MatchID = []
		for n in range(len(Grand_Master_League_Users_Puuids)):
		    url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/by-puuid/{Grand_Master_League_Users_Puuids[n]}/ids?type=ranked&start=0&count=10&api_key={apiDefault['key']}"
		    req = requests.get(url)
		    Grand_Master_League_Users_MatchID_temp = json.loads(req.text)
		    Grand_Master_League_Users_MatchID.append(Grand_Master_League_Users_MatchID_temp)
		    time.sleep(1)

		Grand_Master_League_Users_MatchID = sum(Grand_Master_League_Users_MatchID, [])
		print("Grand Master User MatchID list Dataframe ready, length : ", len(Grand_Master_League_Users_MatchID), " match ids.")
		# final result return as "MatchIDs".
		MatchIDs = Grand_Master_League_Users_MatchID

	################################# MASTER #################################
	##########################################################################
	elif tier_name == "MASTER":

		url = F"{apiDefault['region']}/lol/league/v4/masterleagues/by-queue/{'RANKED_SOLO_5x5'}?api_key={apiDefault['key']}"
		req = requests.get(url)
		Master_League_Users_List = json.loads(req.text)
		Master_League_Users_List_entries = Master_League_Users_List["entries"]
		Master_League_Users_List_entries = pd.DataFrame(Master_League_Users_List_entries)
		tier_list = Master_League_Users_List["tier"]
		Master_League_Users_List_tiers =[]
		for i in range(len(Master_League_Users_List_entries)):
		    Master_League_Users_List_tiers.append(tier_list)
		Master_League_Users_List_tiers = pd.DataFrame(Master_League_Users_List_tiers, columns=['tier'])

		Master_League_Users_List = pd.concat([Master_League_Users_List_entries, Master_League_Users_List_tiers],axis=1)
		Master_League_Users_List_DF = pd.DataFrame(Master_League_Users_List)
		Master_League_Users_List_DF = Master_League_Users_List_DF.sort_values(by='leaguePoints' ,ascending=False)

		Master_League_Users_List_DF = Master_League_Users_List_DF.reset_index()



		# Cut only 100 users from the user list.
		Master_League_Users_List_DF = Master_League_Users_List_DF[:100]
		print("Master User list Dataframe ready, length : ", len(Master_League_Users_List_DF), " users.")

		## save as .csv file for LOLPAGO learning.

		# get puuids from the user list. (summoner name)
		Master_League_Users_List_DF_summonerName = pd.DataFrame(Master_League_Users_List_DF['summonerName'])

		Master_League_Users_Puuids = []

		for i in range((len(Master_League_Users_List_DF_summonerName))):
		    while True:
		        try:
		            url = F"{apiDefault['region']}/lol/summoner/v4/summoners/by-name/{Master_League_Users_List_DF_summonerName.loc[i].to_numpy()[0]}?api_key={apiDefault['key']}"
		            req = requests.get(url)
		            Master_League_Users_Puuids_temp = json.loads(req.text)
		            Master_League_Users_Puuids.append(Master_League_Users_Puuids_temp['puuid'])
		            break
		        except KeyError:
		            break
		    time.sleep(1)

		# get match IDs from the puuid list.
		Master_League_Users_MatchID = []
		for n in range(len(Master_League_Users_Puuids)):
		    url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/by-puuid/{Master_League_Users_Puuids[n]}/ids?type=ranked&start=0&count=10&api_key={apiDefault['key']}"
		    req = requests.get(url)
		    Master_League_Users_MatchID_temp = json.loads(req.text)
		    Master_League_Users_MatchID.append(Master_League_Users_MatchID_temp)
		    time.sleep(1)

		Master_League_Users_MatchID = sum(Master_League_Users_MatchID, [])
		print("Master User MatchID list Dataframe ready, length : ", len(Master_League_Users_MatchID), " match ids.")
		# final result return as "MatchIDs".
		MatchIDs = Master_League_Users_MatchID

	############################ DIAMOND ~ IRON ##############################
	##########################################################################
	else:
		# repeat for I ~ IV tiers.
		Users_MatchID = []
		Users_MatchID = sum(Users_MatchID, [])
		for i in range(1,5):

			if i == 1: tier_num = "I"
			elif i == 2: tier_num = "II"
			elif i == 3: tier_num = "III"
			elif i == 4: tier_num = "IV"

			url = F"{apiDefault['region']}/lol/league/v4/entries/{'RANKED_SOLO_5x5'}/{tier_name}/{tier_num}?page=1&api_key={apiDefault['key']}"
			req = requests.get(url)
			Users_List = json.loads(req.text)
			Users_List_DF = pd.DataFrame(Users_List)
			#Users_List_DF = Users_List_DF.sort_values(by='leaguePoints' ,ascending=False)
			Users_List_DF = Users_List_DF.reset_index()



			# Cut only 100 users from the user list.
			Users_List_DF = Users_List_DF[:25]
			print(tier_name, " ", tier_num, " User list Dataframe ready, length : ", len(Users_List_DF), " users.")
			## save as .csv file for LOLPAGO learning.

			# get puuids from the user list. (summoner name)
			Users_List_DF_summonerName = pd.DataFrame(Users_List_DF['summonerName'])
			Users_Puuids = []

			for i in range((len(Users_List_DF_summonerName))):
				while True:
					try:
						url = F"{apiDefault['region']}/lol/summoner/v4/summoners/by-name/{Users_List_DF_summonerName.loc[i].to_numpy()[0]}?api_key={apiDefault['key']}"
						req = requests.get(url)
						Users_Puuids_temp = json.loads(req.text)
						Users_Puuids.append(Users_Puuids_temp['puuid'])
						break
					except:
						break
					time.sleep(1)

			# get match IDs from the puuid list.

			for n in range(len(Users_Puuids)):
				url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/by-puuid/{Users_Puuids[n]}/ids?type=ranked&start=0&count=10&api_key={apiDefault['key']}"
				req = requests.get(url)
				Users_MatchID_temp = json.loads(req.text)
				Users_MatchID.append(Users_MatchID_temp)
				time.sleep(1)

		# final result return as "MatchIDs".
		Users_MatchID = sum(Users_MatchID, [])
		print(tier_name,  "User MatchID list Dataframe ready, length : ", len(Users_MatchID), " match ids.")
		MatchIDs = Users_MatchID
	##########################################################################
	##########################################################################
	MatchIDs = pd.DataFrame(MatchIDs , columns=['MatchID'])
	MatchIDs = MatchIDs.drop_duplicates(['MatchID'])
	return MatchIDs, tier_name


## get match data with match ids and return dataframe.
def get_Match_Data(df_matchids, tier_name):

	match_data_all = []
	match_data_all = pd.DataFrame(match_data_all)

	for i in range(len(df_matchids)):
		try:
			url = F"{'https://asia.api.riotgames.com'}/lol/match/v5/matches/{df_matchids['MatchID'].loc[i]}?api_key={apiDefault['key']}"
			time.sleep(1)
			req = requests.get(url)

	        # collect PARTICIPANTS in the match
			match_data = json.loads(req.text)
			match_data = match_data["info"]["participants"]
			df_match_data = pd.DataFrame(match_data)
		except:
			pass

		match_data_all = pd.concat([match_data_all,df_match_data],axis=0)
		if i%20 == 0:
			print("Match Number ", i+1,"/", len(df_matchids))

	print("Match-Data dataframe is ready, length : ", len(match_data_all), " player match data.")
	filename = "raw_data_v.0.0.1\%s_raw_data.csv"%(tier_name)
	match_data_all.to_csv(filename, mode='w', encoding="utf-8-sig", index=False)
	print("Saved to raw_data_v.0.0.1 local folder.")
	return match_data_all


## get avg match data. (add up all datas and divide them by the number of users)
def get_Avg_Match_Data(df_match_data):

	mean_df_match_data = []
	mean_df_match_data = df_match_data.mean()
	#print(mean_df_match_data)
	mean_df_match_data = pd.DataFrame(mean_df_match_data)
	print("Mean Data is ready.")

	return mean_df_match_data


## merge upper functions together.
def get_tier_data(tier_name):
	MatchIDs, tier_name_passed = get_Match_IDs(tier_name)
	df_match_data = get_Match_Data(MatchIDs, tier_name_passed)
	mean_df_match_data = get_Avg_Match_Data(df_match_data)
	mean_df_match_data = mean_df_match_data.transpose()

	return mean_df_match_data

if __name__ == "__main__":

	print("######################")
	print("Tier Average Getter On")


	# Get tier data from the server and save it to the local folder.
	print("######################")
	print("Challenger Tier avg data getting ON")
	df_c = get_tier_data("CHALLENGER")
	#print(df_c)
	df_c.to_csv('avg_data_v.0.0.1\challenger_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("Challenger Tier avg data getting OFF")
	print("######################")


	print("######################")
	print("GRANDMASTER Tier avg data getting ON")
	df_gm = get_tier_data("GRANDMASTER")
	df_gm.to_csv('avg_data_v.0.0.1\grandmaster_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("GRANDMASTER Tier avg data getting OFF")
	print("######################")

	print("######################")
	print("MASTER Tier avg data getting ON")
	df_m = get_tier_data("MASTER")
	df_m.to_csv('avg_data_v.0.0.1\master_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("MASTER Tier avg data getting OFF")
	print("######################")

	print("######################")
	print("DIAMOND Tier avg data getting ON")
	df_d = get_tier_data("DIAMOND")
	df_d.to_csv('avg_data_v.0.0.1\diamond_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("DIAMOND Tier avg data getting OFF")
	print("######################")

	print("######################")
	print("PLATINUM Tier avg data getting ON")
	df_p = get_tier_data("PLATINUM")
	df_p.to_csv('avg_data_v.0.0.1\platinum_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("PLATINUM Tier avg data getting OFF")
	print("######################")

	print("######################")
	print("GOLD Tier avg data getting ON")
	df_g = get_tier_data("GOLD")
	df_g.to_csv('avg_data_v.0.0.1\gold_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("GOLD Tier avg data getting OFF")
	print("######################")

	print("######################")
	print("SILVER Tier avg data getting ON")
	df_s = get_tier_data("SILVER")
	df_s.to_csv('avg_data_v.0.0.1\silver_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("SILVER Tier avg data getting OFF")
	print("######################")

	print("######################")
	print("BRONZE Tier avg data getting ON")
	df_b = get_tier_data("BRONZE")
	df_b.to_csv('avg_data_v.0.0.1/bronze_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("BRONZE Tier avg data getting OFF")
	print("######################")

	print("######################")
	print("IRON Tier avg data getting ON")
	df_i = get_tier_data("IRON")
	df_i.to_csv('avg_data_v.0.0.1\iron_avg_data.csv', mode='w', encoding="utf-8-sig", index=False)
	print("IRON Tier avg data getting OFF")
	print("######################")

	print("Tier Average Getter Off")
	print("Thank you for using.")
	print("######################")
