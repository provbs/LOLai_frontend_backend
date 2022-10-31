## this py file will be run on anaconda prompt.

import numpy as np
import pandas as pd
import json

# requests modules for LOL API calls.
import requests

# q_w for file lock function use.
import q_w
import apiInfo

# API default setting.
apiDefault = apiInfo.apiDefault

# file location exist check module.
import os.path
from os import path


### LOLPAGO SERVER...
while True:
## Check if the nickname has been put into the nickname_queue.csv.
	try:
		while True:
			queue = open("queue.txt", 'r')
			queue_bool = queue.readline()
			queue.close()

			if queue_bool == "True":
				queue = open("queue.txt", 'w')
				queue.write("False")
				queue.close()
				break

		## Check if the file is being used by other process.
		while True:
			if q_w.CheckExistCSV("nickname_queue") == True:
				break

		## Delete the nickname from the csv.
		df_nickname = q_w.ReadCSVtoDF("nickname_queue_u.csv")

		nickname = df_nickname["nickname"][0]
		print("nickname is : ", nickname)
		df_nickname.drop(index=df_nickname.index[0],axis=0,inplace=True)

		## save back to csv in the local folder
		df_nickname.to_csv('nickname_queue_u.csv', mode='w', encoding="utf-8-sig", index=False)
		os.rename("nickname_queue_u.csv", "nickname_queue.csv")

		## Find puuid from the nickname.
		user_info = []
		url = F"{apiDefault['region']}/lol/summoner/v4/summoners/by-name/{nickname}?api_key={apiDefault['key']}"
		req = requests.get(url)
		user_info = json.loads(req.text)
		try:
			puuid = user_info['puuid']
		except KeyError:
			print("No summoner exists with nickname ", nickname)


		## check the directory if there is a folder with puuid.
		## check_dir is True or False
		check_dir = path.isdir(puuid)

		## if yes, do nothing and ends, the redirector.py will find the existing html and proceed.
		if check_dir == True:
			print("dir already exists..")

		## if no, going with "refresh" route
		if check_dir == False:
			## run LOLPAGO.py and pass puuid to it
			print("executing LOLPAGO.py with puuid :", puuid)
			print("nickname : ", nickname)
			task = "python LOLPAGO.py " + puuid + " " + nickname
			os.system(task)
	except :
		print("Error occured, please try again.")
