FROM python:alpine
MAINTAINER Hossein Naderi <hossein-naderi@hotmail.com>

RUN addgroup -g 1001 -S bot
RUN adduser -S bot -u 1001
USER bot

ENV PYTHONUNBUFFERED 1

# Install pythonic requirements
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app /usr/bin
WORKDIR /home/bot
