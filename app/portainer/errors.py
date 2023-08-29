#!/usr/bin/env python3


class NoSuchTagError(Exception):
    def __init__(self, tag):
        self.tag = tag


class AmbiguousTagError(Exception):
    def __init__(self, tag, endpoints):
        self.tag = tag
        self.endpoints = endpoints


class RequestError(Exception):
    def __init__(self, url, status, body):
        self.url = url
        self.status = status
        self.body = body
