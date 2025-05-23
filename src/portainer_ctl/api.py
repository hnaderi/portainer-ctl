import json
import logging

import requests
from requests.structures import CaseInsensitiveDict

from . import errors, helpers, models
from .client import Client

logger = logging.getLogger(__name__)


class GlobalStacksAPI:
    def __init__(self, client: Client):
        self.__client = client

    def list(self, **kwargs):
        logger.info("Getting a list of stacks")
        return self.__client.get("/stacks", params=kwargs)

    def get_stack_id_by_name(self, name):
        stacks = self.list(name=name)
        ids = [s["Id"] for s in stacks if s["Name"] == name]
        return ids[0]

    def get_stacks_by_name(self, name):
        stacks = self.list()
        filtered = [s for s in stacks if s["Name"] == name]
        return filtered

    def get(self, id):
        logger.info(f"Getting stack {id}")
        return self.__client.get(f"/stacks/{id}")


class StacksAPI:
    def __init__(self, client, endpoint_id):
        self.__client = client
        self.__endpoint_id = str(endpoint_id)

    def create(self, stack_name: str, compose: str, env_vars):
        stack_name = stack_name.lower().strip()

        stacks = GlobalStacksAPI(self.__client).get_stacks_by_name(stack_name)

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

            self.__client.put(
                f"/stacks/{str(stack_id)}",
                data,
                params={"endpointId": self.__endpoint_id},
            )

        else:
            logger.info("No existing stack with name: " + stack_name)
            info = EndpointAPI(self.__client, self.__endpoint_id).get_docker_info()
            swarm_id = info["Swarm"]["Cluster"]["ID"]

            data = {
                "Env": env_vars,
                "Name": stack_name,
                "SwarmID": swarm_id,
                "StackFileContent": compose,
            }
            self.__client.post(
                f"/stacks/create/swarm/string?endpointId={self.__endpoint_id}",
                data=data,
            )

        return

    def get(self, id):
        pass


class ConfigsAPI:
    def __init__(self, client, endpoint_id, api_version: str):
        self.__client = client
        self.__endpoint_id = str(endpoint_id)
        self.__base = (
            f"/endpoints/{self.__endpoint_id}/docker/"
            + (f"v{api_version}/" if api_version else "")
            + "configs"
        )

    def create(self, name, data):
        name = name.strip()

        logger.info("Creating new config " + name)
        body = {"Data": helpers.to_base64(data), "Name": name, "Labels": {}}
        try:
            return self.__client.post(f"{self.__base}/create", body)
        except Exception as e:
            logger.error(f"cannot create config: {str(e)}")

    def get(self, id: str):
        return self.ls(id=[id])

    def get_by_name(self, name: str):
        return self.ls(name=[name])

    def ls(self, **kwargs):
        return self.__client.get(
            self.__base,
            params={"filters": json.dumps(kwargs)},
        )

    def delete(self, id: str):
        return self.__client.delete(
            f"{self.__base}/{id}",
        )


class SecretsAPI:
    def __init__(self, client, endpoint_id, api_version: str):
        self.__client = client
        self.__endpoint_id = str(endpoint_id)
        self.__base = (
            f"/endpoints/{self.__endpoint_id}/docker/"
            + (f"v{api_version}/" if api_version else "")
            + "secrets"
        )

    def create(self, name, data):
        name = name.strip()

        logger.info("Creating new secret " + name)
        body = {"Data": helpers.to_base64(data), "Name": name, "Labels": {}}
        try:
            return self.__client.post(f"{self.__base}/create", body)
        except Exception as e:
            logger.error(f"cannot create secret: {str(e)}")

    def ls(self, **kwargs):
        return self.__client.get(
            self.__base,
            params={"filters": json.dumps(kwargs)},
        )

    def delete(self, id: str):
        return self.__client.delete(
            f"{self.__base}/{id}",
        )


class EndpointAPI:
    def __init__(self, client, endpoint_id):
        self.__client = client
        self.__endpoint_id = str(endpoint_id)
        logger.info("Getting endpoint info")
        version = self.__client.get(
            "/endpoints/" + self.__endpoint_id + "/docker/version"
        )
        api_version = version["ApiVersion"]
        self.__api_version = api_version
        self.configs = ConfigsAPI(client, endpoint_id, api_version)
        self.secrets = SecretsAPI(client, endpoint_id, api_version)
        self.stacks = StacksAPI(client, endpoint_id)

    def get_docker_info(self):
        logger.info("Getting endpoint info")
        resp = self.__client.get("/endpoints/" + self.__endpoint_id + "/docker/info")
        return resp


class EndpointsAPI:
    def __init__(self, client):
        self.__client = client

    def create(self, request: models.EndpointCreationRequest):
        data = {
            "Name": request.name,
            "EndpointCreationType": request.type,
            "URL": request.url,
            "GroupID": request.groupId,
            "TagIds": request.tagIds,
        }
        return self.__client.post("/endpoints", data)

    def list(self, **kwargs):
        logger.info("Getting a list of endpoints")
        resp = self.__client.get("/endpoints", **kwargs)
        return resp

    def get(self, id):
        logger.info(f"Getting endpoint {id}")
        resp = self.__client.get(f"/endpoints/{id}")
        return resp

    def get_by_name(self, name):
        return self.list(params={"name": name})


class TagsAPI:
    def __init__(self, client):
        self.__client = client

    def list(self):
        logger.info("Getting a list of tags")
        resp = self.__client.get("/tags")
        return resp

    def get_endpoints(self, tag):
        tags = self.list()
        target = [ei for t in tags for ei in t["Endpoints"] if t["Name"] == tag]
        return target


class PublicAPI:
    def __init__(self, client: Client):
        self.__client = client

    def status(self):
        return self.__client.get("/status")

    def init(self, username: str, password: str):
        data = {"password": password, "username": username}
        return self.__client.post("/users/admin/init", data)


class Portainer:
    def __init__(self, client: Client):
        self.__client = client
        self.stacks = GlobalStacksAPI(client)
        self.endpoints = EndpointsAPI(client)
        self.tags = TagsAPI(client)
        self.public = PublicAPI(client)

    def endpoint(self, id) -> EndpointAPI:
        return EndpointAPI(self.__client, id)
