#!/usr/bin/env python3


class InvalidCommand(Exception):
    def __init__(self, msg):
        self.msg = msg


class RequestError(Exception):
    def __init__(self, url, status, body):
        self.url = url
        self.status = status
        self.body = body
