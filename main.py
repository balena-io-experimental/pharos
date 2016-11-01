import time,signal,sys, datetime
from time import sleep
from Led_Array import Led_Array, Color

RED = Color(100, 0, 0)
GREEN = Color(0, 100, 0)
BLUE = Color(0,0,100)

led_array = Led_Array()

test_array = [{'is_inbound': True, 'msgId': u'msg_4mhetg', 'time_elapsed': datetime.timedelta(0, 1753, 356637), 'color': 234235}, \
            {'is_inbound': True, 'msgId': u'msg_4mfilb', 'time_elapsed': datetime.timedelta(0, 1436, 356654), 'color': 234235}, \
            {'is_inbound': True, 'msgId': u'msg_4mekrn', 'time_elapsed': datetime.timedelta(0, 11823, 356659), 'color': 234235}, \
            {'is_inbound': True, 'msgId': u'msg_4mekrn', 'time_elapsed': datetime.timedelta(0, 1799, 356659), 'color': 234235}, \
            {'is_inbound': True, 'msgId': u'msg_4m43sm', 'time_elapsed': datetime.timedelta(0, 74521, 356663), 'color': 234235}]

def renderMessages(message_array):
    led_array.empty_array()
    i = 0
    for message in message_array:
        row = i*4 
        led_array.fill_rect(row, 3, message['color'])
        time.sleep(2)
        led_array.render()
        i = i + 1

    # led_array.render()

def handleSIGTERM():
    del led_array
    sys.exit()

signal.signal(signal.SIGTERM, handleSIGTERM)

renderMessages(test_array)

while True:
    print("waiting...")
    time.sleep(30)