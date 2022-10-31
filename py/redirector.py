#!Z:\Program Files\Anaconda\python.exe
import cgi
import time
import q_w
import json
import apiInfo

import chardet

import os.path
from os import path

# requests modules for LOL API calls.
import requests

# API default setting.
apiDefault = apiInfo.apiDefault

def redirect(url):
	print("Location: " + url)
	print()


## find puuid from the nickname passed
form = cgi.FieldStorage()
puuid = form["puuid"].value

# user_info = []
# url = F"{apiDefault['region']}/lol/summoner/v4/summoners/by-name/{nickname}?api_key={apiDefault['key']}"
# req = requests.get(url)
# user_info = json.loads(req.text)
#
# try:
# 	puuid = user_info['puuid']
# except KeyError:
# 	redirect("error_888.html")

## wait until the pages get ready.

while True:
	## check the directory if there is a folder with puuid.
	## check_dir is True or False
	filename = puuid+"/user_info.html"
	check_dir = path.isfile(filename)
	time.sleep(1) #wait 1 second to check puuid folder again.
	if check_dir == True:
		break

## redirect to the url
url = puuid + "/user_info.html"
redirect(url)
