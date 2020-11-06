# Use an official Python runtime as a parent image
FROM python:3.8.5

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
WORKDIR /app/WebWhatsapp-Wrapper
RUN pip install -r requirements.txt
RUN pip install ./

WORKDIR /app
