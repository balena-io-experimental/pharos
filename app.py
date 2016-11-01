#!/usr/bin/env python
import os
import datetime as dt
import time
import requests
import spectra
from pydash import py_

HEADERS = { 'Authorization': 'Bearer ' + os.environ['FRONT_TOKEN'] }
INBOX_IDS = os.getenv('INBOX_IDS', 'inb_n62,inb_nla').split(',')
COLORS = os.getenv('COLORS', '#3aff5b,#f44242').split(',')
COLOR_SCALE = spectra.scale(COLORS).domain([0, 60])

def getConvos(inboxId, pageIndex):
	resultArr = list()
	i = str(pageIndex) or '1'
	url = 'https://api2.frontapp.com/inboxes/' + inboxId + '/conversations?q[statuses][]=unassigned&q[statuses][]=assigned&page=' + i
	r = requests.get(url, headers=HEADERS)
	rjson = r.json()

	# Append items to results array
	resultArr.extend(rjson['_results'])
	# If there are more results from front run the getter again
	if rjson['_pagination']['next'] is not None:
		getConvos(inboxId, pageIndex + 1)
	else:
		print resultArr[0]['status']
		# print resultArr
		return resultArr

def timeElapsed(ts):
	return (dt.datetime.now() - (dt.datetime.fromtimestamp(int(ts)))).total_seconds()/60

def getName(tag):
	return tag['name']

def getColor(ts):
	# try apply color scale if fails assume exceeded and return last value
	try:
		return int(COLOR_SCALE(timeElapsed(ts)).hexcode[1:], 16)
	except:
		return int(py_.last(COLORS)[1:], 16)

def stripSearch(convo):
	newObj = {
		'color' : getColor(convo['last_message']['created_at']),
		'tags'  : py_.map(convo['tags'], getName),
	}
	return newObj

def run():
	return py_(INBOX_IDS).map(getConvos) \
						 .flatten() \
						 .filter(lambda x: \
						  x['last_message']['is_inbound'] == True ) \
						 .map(stripSearch) \
				  		 .value()

if __name__ == '__main__':
	while (True):
		print run()
		time.sleep(10)
