import os
import signal
import sys
import time

import audioop
import pyaudio
from pubnub import Pubnub

from Led_Array import Led_Array, Color

AUDIO_VOLUME = float(os.getenv('AUDIO_VOLUME', 1.0))
PROGRESS_SENSITIVITY = float(os.getenv('SENSITIVITY', 10.0))
RESIN_DEVICE_UUID = os.getenv("RESIN_DEVICE_UUID")

PUBNUB_ENABLE = os.getenv("PUBNUB_ENABLE", "off")
PUBLISH_KEY = os.getenv("PUBLISH_KEY")
SUBSCRIBE_KEY = os.getenv("SUBSCRIBE_KEY")

RATE = 44100
FORMAT = pyaudio.paInt16
AUDIO_MAX = 2 ** 15
CHANNELS = 2

MAX_ROWS = 32

RED = Color(100, 0, 0)
GREEN = Color(0, 100, 0)
BLUE = Color(0, 0, 100)

READY_FLAG = False

pubnub = Pubnub(publish_key=PUBLISH_KEY,
                subscribe_key=SUBSCRIBE_KEY, ssl_on=True)

p = pyaudio.PyAudio()
led_array = Led_Array()

current_max = 0
current_level = 0
current_progress = 0

count = 0

def audio_callback(in_data, frame_count, time_info, status):
    global current_max
    global current_level
    global current_progress
    global count
    count += 1

    # slowly drop the max
    current_max = max(current_max - 1, 0)

    current_level = audioop.max(in_data, 2) * AUDIO_VOLUME
    # current_level is 0-32 value shown on LEDs
    current_level = min(int(current_level * MAX_ROWS / AUDIO_MAX), MAX_ROWS)

    current_max = min(max(current_level, current_max), MAX_ROWS)

    current_progress = min(current_progress + current_level / PROGRESS_SENSITIVITY, MAX_ROWS)

    led_array.empty_array()
    led_array.fill_up_to(int(current_progress) + current_level, BLUE)
    led_array.setRowColor(int(current_progress) + current_max, RED)
    led_array.fill_up_to(int(current_progress), GREEN)
    led_array.render()

    return (None, pyaudio.paContinue)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                frames_per_buffer=RATE / 10,
                rate=RATE,
                input=True,
                output=False,
                start=False,
                stream_callback=audio_callback)


def clean_up():
    print 'Clean up streams and pyaudio'
    stream.stop_stream()
    stream.close()
    p.terminate()


def handler(signal, frame):
    clean_up()
    print 'exiting python process'
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

# Asynchronous usage
def callback(message, channel):
    global READY_FLAG
    print('message received: ',str(message))
    if (str(message) == "ready") & (READY_FLAG == False):
        READY_FLAG = True
        main()


def error_callback(message):
    print("ERROR : " + str(message))


def connect(message):
    print("CONNECTED to dockercon channel")


def reconnect(message):
    print("RECONNECTED")


def disconnect(message):
    print("DISCONNECTED")

pubnub.subscribe(channels="events", callback=callback, error=error_callback,
                 connect=connect, reconnect=reconnect, disconnect=disconnect)

def main():
    global count
    print('Starting Applause-o-meter!!')
    stream.start_stream()
    while stream.is_active():
        if PUBNUB_ENABLE == "on":
            current_progress_percent = (current_progress/32.0)*100
            current_level_percent = (current_level/32.0)*100
            message = {'current_progress': current_progress_percent, 'current_level': current_level_percent}
            print 'pubnub: ', message
            pubnub.publish(RESIN_DEVICE_UUID, message)

        print "audio callback rate: %dHz" % count
        count = 0

        time.sleep(1)

while True:
    time.sleep(10)
clean_up()
