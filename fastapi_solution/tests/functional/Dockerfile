FROM python:3.8-slim-buster

WORKDIR /tests/functional

COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .