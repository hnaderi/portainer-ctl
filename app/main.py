#!/usr/bin/env python

from portainer.bot import Portainer
from os import environ
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("echo")
args = parser.parse_args()

print(args.echo)

HOST=environ['PORTAINER_HOST']
PASSWORD=environ['PORTAINER_PASSWORD']
USERNAME=environ['PORTAINER_USERNAME']

bot = Portainer(HOST, USERNAME, PASSWORD)

token = bot.login()
# target = bot.get_stack_id('production-trading')
# print(target)

# ep_id = bot.get_endpoint_id('production')
# info = bot.get_docker_info(ep_id)
# print(info)

# print(info['Swarm']['Cluster']['ID'])

# bot.create_config(5, 'havij', 'Some Havij!')

bot.deploy('staging', 'trading', '', '')
