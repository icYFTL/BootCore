from python:3.8

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir /opt/app
WORKDIR /opt/app

COPY . .