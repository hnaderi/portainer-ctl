FROM python:alpine
MAINTAINER Hossein Naderi <hossein-naderi@hotmail.com>

ENV PYTHONUNBUFFERED 1

# Install pythonic requirements
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && rm -f /app/requirements.txt

COPY ./app /usr/bin
WORKDIR /app
