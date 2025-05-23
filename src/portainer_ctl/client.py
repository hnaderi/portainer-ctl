#!/usr/bin/env python

import json
import logging

import requests
from requests.structures import CaseInsensitiveDict

from . import errors, helpers

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, host: str):
        self.host = host
        self.token: CaseInsensitiveDict = CaseInsensitiveDict()

    def __extract(self, resp):
        if resp.ok:
            return resp.json()
        else:
            raise errors.RequestError(resp.url, resp.status_code, resp.text)

    def get(self, url: str, **kwargs):
        resp = requests.get(self.host + url, headers=self.token, **kwargs)
        return self.__extract(resp)

    def post(self, url: str, json=None, data=None, **kwargs):
        resp = requests.post(
            self.host + url, headers=self.token, json=json, data=data, **kwargs
        )
        return self.__extract(resp)

    def put(self, url: str, data, **kwargs):
        resp = requests.put(
            self.host + url, headers=self.token, data=json.dumps(data), **kwargs
        )
        return self.__extract(resp)

    def delete(self, url: str, **kwargs):
        resp = requests.delete(self.host + url, headers=self.token, **kwargs)
        if resp.ok:
            return
        else:
            raise errors.RequestError(resp.url, resp.status_code, resp.text)

    def authorize(self, api_token: str):
        logger.info("Authorized for " + self.host + " using api token")
        self.token["Accept"] = "application/json"
        self.token["x-api-key"] = api_token
        return

    def login(self, username: str, password: str):
        logger.info("Trying to login to " + self.host + "...")
        body = {"username": username, "password": password}
        resp = self.post("/auth", body)
        token = resp["jwt"]
        self.token["Accept"] = "application/json"
        self.token["Authorization"] = "Bearer " + token
        return

    def logout(self):
        self.token.clear()
