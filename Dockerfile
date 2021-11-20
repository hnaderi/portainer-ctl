FROM python:alpine
MAINTAINER Hossein Naderi <hossein-naderi@hotmail.com>

RUN addgroup -g 1001 -S bot
RUN adduser -S bot -u 1001

ENV PYTHONUNBUFFERED 1

# Install pythonic requirements
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt && \
  rm -r /requirements.txt

USER bot
COPY ./app /app
WORKDIR /app
