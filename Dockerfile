FROM resin/raspberrypi3-alpine-python:3.3.6

RUN mkdir -p /usr/src/appd
WORKDIR /usr/src/appd

ONBUILD COPY requirements.txt /usr/src/appd/
ONBUILD RUN pip install --no-cache-dir -r requirements.txt

ONBUILD COPY . /usr/src/appd