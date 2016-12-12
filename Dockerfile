FROM resin/raspberrypi2-python:2.7

RUN pip install \
	colour \
	pydash \
	requests \
	rpi_ws281x

CMD python -u main.py

WORKDIR /usr/src/app
COPY . .

