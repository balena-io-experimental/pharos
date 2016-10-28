#!/usr/bin/env python
import os
import datetime as dt
import json
import requests
import spectra
from pydash import py_

HEADERS = { 'Authorization': 'Bearer ' + os.environ['FRONT_TOKEN'] }
INBOX_IDS = os.environ['INBOX_IDS'].split(',') or ['inb_n62', 'inb_nla']
COLORS = os.environ['COLORS'].split(',') or ["#3aff5b", "#f44242"]
COLOR_SCALE = spectra.scale(COLORS).domain([0, 60])

def getConvos(inboxId):
	print 'ID ' + inboxId
	url = 'https://api2.frontapp.com/inboxes/' + inboxId + '/conversations?q[statuses][]=unassigned'
	r = requests.get(url, headers=HEADERS)
	return r.json()['_results']

def timeElapsed(ts):
	return (dt.datetime.now() - (dt.datetime.fromtimestamp(int(ts)))).total_seconds()/60

def getName(tag):
	return tag['name']

def getColor(ts):
	try:
		return COLOR_SCALE(timeElapsed(ts)).hexcode
	except:
		return py_.last(COLORS)

def stripSearch(convo):
	newObj = {
		'color': getColor(convo['last_message']['created_at']),
		'tags': py_.map(convo['tags'], getName)
	}
	return newObj

def run():
	return py_(INBOX_IDS).map(getConvos) \
				  .flatten() \
				  .filter(lambda x:
				  	x['last_message']['is_inbound'] == True ) \
				  .map(stripSearch) \
				  .value()

if __name__ == "__main__":
    print run()
