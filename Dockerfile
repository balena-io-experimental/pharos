FROM resin/raspberrypi3-python:2.7

# RUN apt-get update \
# 	&& apt-get install -yq \
#     	python-pyaudio \
# 	&& apt-get clean \
# 	&& rm -rf /var/lib/apt/lists/*

RUN pip install rpi_ws281x

WORKDIR /usr/src/app

COPY . .

CMD python -u main.py


