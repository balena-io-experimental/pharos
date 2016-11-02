import os
import datetime as dt
import time
import requests
from pydash import py_
from colour import Color

import time,signal,sys, datetime
from time import sleep
from Led_Array import Led_Array

HEADERS = { 'Authorization': 'Bearer ' + os.environ['FRONT_TOKEN'] }
INBOX_IDS = os.getenv('INBOX_IDS', 'inb_n62,inb_nla').split(',')
COLORS = os.getenv('COLORS', '#3aff5b,#f44242').split(',')
colorStart = Color(COLORS[0])
colorEnd = Color(COLORS[1])
COLOR_SCALE = list(colorStart.range_to(colorEnd, 60))
INTERVAL = int(os.getenv('INTERVAL', '5'))

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
		return resultArr

def timeElapsed(ts):
	return int((dt.datetime.now() - (dt.datetime.fromtimestamp(int(ts)))).total_seconds())

def getName(tag):
	return tag['name']

def getColor(ts):
	# try apply color scale if fails assume exceeded and return last value
	timeout = timeElapsed(ts)
	if timeout > 60:
		return int(py_.last(COLORS)[1:], 16)
	else:
		return int(COLOR_SCALE[timeElapsed(ts)/60].hex[1:], 16)

def stripSearch(convo):
	return {
		'color' : getColor(convo['last_message']['created_at']),
		'tags'  : py_.map(convo['tags'], getName),
		'timeElapsed': timeElapsed(convo['last_message']['created_at'])
	}

def getLatestComment(convo):
	r = requests.get(convo['_links']['related']['comments'], headers=HEADERS)
	comments = r.json()['_results']
	if not py_.is_empty(comments):
		# get latest
		return py_.pick(comments[0], 'body', 'posted_at')

def isLatestMsg(convo):
	comment = getLatestComment(convo)
	msg = convo['last_message']
	# check if the latest message is newer than latest comment
	try:
		if timeElapsed(msg['created_at']) < timeElapsed(comment['posted_at']):
			return convo
 	except:
		return convo

def run():
	items = py_(INBOX_IDS).map(getConvos) \
						.flatten() \
						.filter(lambda x: \
						  x['last_message']['is_inbound'] == True ) \
						.filter(isLatestMsg) \
						.map(stripSearch) \
						.value()
	print items
	return items

def renderMessages(message_array):
	led_array = Led_Array()
	led_array.empty_array()
	i = 0
	for message in message_array:
		row = i*4
		led_array.fill_rect(row, 3, message['color'])
		# time.sleep(2)
		led_array.render()
		i = i + 1

	led_array.render()
	del led_array

def handleSIGTERM():
	del led_array
	sys.exit()

signal.signal(signal.SIGTERM, handleSIGTERM)


if __name__ == '__main__':
	while (True):
		renderMessages(run())
		time.sleep(INTERVAL)
