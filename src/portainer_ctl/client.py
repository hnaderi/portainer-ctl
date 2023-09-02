#!/usr/bin/env python

import json
import logging

import requests
from requests.structures import CaseInsensitiveDict

from . import errors, helpers

logging.basicConfig()
logger = logging.getLogger("portainer")
logger.setLevel(logging.DEBUG)


class Portainer:
    def __init__(self, host: str):
        self.host = host
        self.token: CaseInsensitiveDict = CaseInsensitiveDict()

    def __extract(self, resp):
        if resp.ok:
            return resp.json()
        else:
            raise errors.RequestError(resp.url, resp.status_code, resp.text)

    def get(self, url: str):
        resp = requests.get(self.host + url, headers=self.token)
        return self.__extract(resp)

    def post(self, url: str, data):
        resp = requests.post(self.host + url, headers=self.token, data=json.dumps(data))
        return self.__extract(resp)

    def put(self, url: str, data):
        resp = requests.put(self.host + url, headers=self.token, data=json.dumps(data))
        return self.__extract(resp)

    def delete(self, url: str):
        resp = requests.post(self.host + url, headers=self.token)
        return self.__extract(resp)

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

    def list_stacks(self):
        logger.info("Getting a list of stacks")
        resp = self.get("/stacks")
        return resp

    def get_stack_id(self, name):
        stacks = self.list_stacks()
        ids = [s["Id"] for s in stacks if s["Name"] == name]
        return ids[0]

    def get_stack(self, name):
        stacks = self.list_stacks()
        filtered = [s for s in stacks if s["Name"] == name]
        return filtered

    def list_endpoints(self):
        logger.info("Getting a list of endpoints")
        resp = self.get("/endpoints")
        return resp

    def list_tags(self):
        logger.info("Getting a list of tags")
        resp = self.get("/tags")
        return resp

    def get_endpoint_id(self, name):
        endpoints = self.list_endpoints()
        ids = [e["Id"] for e in endpoints if e["Name"] == name]
        return ids[0]

    def get_endpoint_by_id(self, e_id):
        return Endpoint(client=self, endpoint_id=e_id)

    def get_endpoint_by_tag(self, tag):
        tags = self.list_tags()
        target = [ei for t in tags for ei in t["Endpoints"] if t["Name"] == tag]
        if len(target) == 1:
            return self.get_endpoint_by_id(target[0])
        elif len(target) == 0:
            raise errors.NoSuchTagError(tag)
        else:
            raise errors.AmbiguousTagError(tag, target)


class Endpoint:
    def __init__(self, client, endpoint_id):
        self.client = client
        self.endpoint_id = str(endpoint_id)

    def get_docker_info(self):
        logger.info("Getting endpoint info")
        resp = self.client.get("/endpoints/" + self.endpoint_id + "/docker/info")
        return resp

    def create_config(self, name, data):
        name = name.strip()

        logger.info("Creating new config " + name)
        body = {"Data": helpers.to_base64(data), "Name": name, "Labels": {}}
        try:
            self.client.post(
                "/endpoints/" + self.endpoint_id + "/docker/configs/create", body
            )
        except Exception as e:
            logger.error(f"cannot create config: {str(e)}")

    def create_secret(self, name, data):
        name = name.strip()

        logger.info("Creating new secret " + name)
        body = {"Data": helpers.to_base64(data), "Name": name, "Labels": {}}
        try:
            self.client.post(
                "/endpoints/" + self.endpoint_id + "/docker/secrets/create", body
            )
        except Exception as e:
            logger.error(f"cannot create secret: {str(e)}")

    def deploy(self, stack_name: str, compose: str, env_vars):
        stack_name = stack_name.lower().strip()

        stacks = self.client.get_stack(stack_name)

        if len(stacks) == 1:
            logger.info("Updating existing stack name: " + stack_name)
            existing_stack = stacks[0]
            stack_id = existing_stack["Id"]

            data = {
                "Prune": True,
                "StackFileContent": compose,
                "Env": env_vars,
                "id": stack_id,
            }

            self.client.put(
                "/stacks/" + str(stack_id) + "?endpointId=" + self.endpoint_id, data
            )

        else:
            logger.info("No existing stack with name: " + stack_name)
            info = self.get_docker_info()
            swarm_id = info["Swarm"]["Cluster"]["ID"]

            data = {
                "Env": env_vars,
                "Name": stack_name,
                "SwarmID": swarm_id,
                "StackFileContent": compose,
            }
            self.client.post(
                "/stacks?endpointId=" + self.endpoint_id + "&method=string&type=1",
                data=data,
            )

        return
