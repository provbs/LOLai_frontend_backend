# COLLECTIONS OF SUB FUNCTIONS USED IN LOLPAGO.py
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

## get html string from the files and return back.
def html_page(type) :
	if type == 1:
		f = open("../user_info_renewal.html", encoding='UTF8')
		data = f.read()
		f.close()
		html_string = data
	elif type == 2:
		f = open("../match_number_info_renewal.html", encoding='UTF8')
		data = f.read()
		f.close()
		html_string = data
	else :
		print("html type input is wrong.")
		html_string = ""

	return html_string

## Read update_history.txt file and give back update date list
def read_history(instruction) :

	# return recent win/lose data as string
	if instruction_number == "getwinloss" :
		return ws_data

	# return recent win rate data as string
	if instruction_number == "getwinrate" :
		return wr_data

	return 0

## min-max normalization
def min_max_normalize(lst):
	normalized = []
	lst = lst[0]

	for value in lst:
		normalized_num = (value - min(lst)) / (max(lst) - min(lst))
		normalized_num = normalized_num * 100
		normalized.append(normalized_num)

	return normalized
