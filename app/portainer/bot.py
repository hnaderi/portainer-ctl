#!/usr/bin/env python

import json
import requests
from requests.structures import CaseInsensitiveDict
import logging
from . import helpers

logging.basicConfig()
logger = logging.getLogger("portainer-bot")
logger.setLevel(logging.DEBUG)

class Portainer:
  def __init__(self, host: str, username : str, password : str):
    self.host = host
    self.username = username
    self.password = password

  def __get(self, url:str):
    resp = requests.get(self.host + url, headers = self.token)
    return resp.json()

  def __post(self, url:str, data):
    resp = requests.post(self.host + url, headers = self.token, data=json.dumps(data))
    return resp.json()


  def login(self):
    logger.info("Trying to login...")
    body = {'username': self.username, 'password' : self.password}
    resp = requests.post(self.host + '/auth', data=json.dumps(body))
    token = resp.json()["jwt"]
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    self.token = headers
    return


  def list_stacks(self):
     logger.info("Getting a list of stacks")
     resp = self.__get('/stacks')
     return resp

  def get_stack_id(self, name):
     stacks = self.list_stacks()
     ids = [s['Id'] for s in stacks if s['Name']==name]
     return ids[0]


  def get_stack(self, name):
     stacks = self.list_stacks()
     filtered = [s for s in stacks if s['Name']==name]
     return filtered

  def list_endpoints(self):
     logger.info("Getting a list of endpoints")
     resp = self.__get('/endpoints')
     return resp

  def get_docker_info(self, endpoint_id):
    logger.info("Getting endpoint info")
    resp = self.__get('/endpoints/'+ str(endpoint_id) + '/docker/info')
    return resp

  def get_endpoint_id(self, name):
    endpoints = self.list_endpoints()
    ids = [e['Id'] for e in endpoints if e['Name']==name]
    return ids[0]


  def create_config(self, endpoint_id, name, data):
    logger.info('Creating new config ' + name)
    body = { 'Data': helpers.to_base64(data), 'Name': name, 'Labels': {} }
    resp = self.__post('/endpoints/' + str(endpoint_id) + '/docker/configs/create', body)
    return resp

  def create_secret(self, endpoint_id, name, data):
    logger.info('Creating new secret ' + name)
    body = { 'Data': helpers.to_base64(data), 'Name': name, 'Labels': {} }
    resp = self.__post('/endpoints/' + str(endpoint_id) + '/docker/secrets/create', body)
    return resp


  def deploy(self, envname, name, manifest, envfile):
    stack_name = str(envname) + '-' + str(name)
    stacks = self.get_stack(stack_name)
    if len(stacks) == 1:
      logger.info('Updating existing stack name: ' + stack_name)
      existing_stack = stacks[0]
    else:
      logger.info('No existing stack with name: ' + stack_name)

    return
