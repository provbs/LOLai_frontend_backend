#!Z:\Program Files\Anaconda\python.exe
import time
import cgi
import base64
import apiInfo
import requests
import json

import shutil

import numpy as np
import pandas as pd

import os.path
from os import path

## Check if the filename is existing, if yes, changes its name to name_u
def CheckExistCSV(filename):
	if path.exists(filename+".csv"):
		try:
			os.rename(filename+".csv", filename+"_u.csv")
			return True
		except OSError as e:
			return False


def ReadCSVtoDF(filename):
    df = pd.read_csv(filename)
    df = pd.DataFrame(df)
    return df


if __name__ == "__main__":

	## nickname - received nickname from the user
	form = cgi.FieldStorage()
	nickname = form["nickname"].value

	update = form["update"].value

	## Check if the file is being used by other process.
	while True:
		if CheckExistCSV("nickname_queue") == True:
			break

	## open csv file - nickname_queue.csv
	## save nickname in a dataframe
	df_nickname = ReadCSVtoDF("nickname_queue_u.csv")

	df_new = [nickname]
	column_names = ["nickname"]

	df_new = pd.DataFrame(df_new, columns = column_names)
	df_nickname = pd.concat([df_nickname, df_new], axis = 0)

	apiDefault = apiInfo.apiDefault
	user_info = []
	url = F"{apiDefault['region']}/lol/summoner/v4/summoners/by-name/{nickname}?api_key={apiDefault['key']}"
	req = requests.get(url)
	user_info = json.loads(req.text)

	try:
		puuid = user_info['puuid']
	except KeyError:
		print("error q_w")

	if update == "True":
		shutil.rmtree(puuid)

	## save back to csv in the local folder
	df_nickname.to_csv('nickname_queue_u.csv', mode='w', encoding="utf-8-sig", index=False)
	os.rename("nickname_queue_u.csv", "nickname_queue.csv")

	## increase queue.txt by 1
	queue = open("queue.txt", 'w')
	queue.write("True")
	queue.close()

	#Redirection
	print("Location: redirector.py?puuid="+puuid)
	print()
