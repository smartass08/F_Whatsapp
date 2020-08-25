# Use an official Python runtime as a parent image
FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

WORKDIR /app/WebWhatsapp-Wrapper

RUN pip install -r requirements.txt

RUN pip install ./

WORKDIR /app

ENV SELENIUM "http://firefox:4444/wd/hub"

CMD ["bash","start.sh"]