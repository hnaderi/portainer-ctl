#!/usr/bin/env python

import argparse
import sys
from os import getenv
import json
import logging

from .client import Client
from .api import Portainer
from .errors import RequestError


def configure_logging(args):
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)


def parse_mount(conf: str):
    try:
        path, name = conf.split(":")
        return (path, name)
    except Exception:
        print("invalid mount argument: " + conf)


def read_string(path):
    with open(path, "r") as f:
        return "".join(f.readlines())


def deploy_app(args):
    try:
        deploy(args)
    except RequestError as err:
        print(err.url, err.status, err.body, file=sys.stderr)
        sys.exit("Failed to deploy!")


def get_authenticated_client(args):
    HOST = getenv("PORTAINER_HOST", args.host)
    PASSWORD = getenv("PORTAINER_PASSWORD", args.password)
    USERNAME = getenv("PORTAINER_USERNAME", args.username)
    API_TOKEN = getenv("PORTAINER_TOKEN", args.api_token)

    client = Client(HOST)
    if API_TOKEN:
        client.authorize(API_TOKEN)
    else:
        client.login(USERNAME, PASSWORD)

    return client


def connect(args):
    client = get_authenticated_client(args)
    return Portainer(client)


def deploy(args):
    api = connect(args)

    endpoints = api.tags.get_endpoints(args.environment)
    if len(endpoints) == 0:
        raise errors.NoSuchTagError(tag)
    elif len(endpoints) > 1:
        raise errors.AmbiguousTagError(tag, target)

    ep = api.endpoint(endpoints[0])

    compose = ""
    with open(args.compose_file, "r") as f:
        compose = "".join(f.readlines())

    env_lines = args.variable
    if args.env_file != None:
        with open(args.env_file, "r") as f:
            lines = f.readlines()
            env_lines = env_lines + lines

    env_vars = []
    for line in env_lines:
        striped = line.strip()
        idx = striped.find("=")
        env_vars.append({"name": striped[:idx], "value": striped[idx + 1 :]})

    for conf in args.config:
        path, name = parse_mount(conf)
        data = read_string(path)
        ep.configs.create(name=name, data=data)

    for conf in args.secret:
        path, name = parse_mount(conf)
        data = read_string(path)
        ep.secrets.create(name=name, data=data)

    stack_name = (
        args.stack_name
        if args.stack_name != None
        else args.environment + "-" + args.name
    )

    ep.stacks.create(stack_name=stack_name, compose=compose, env_vars=env_vars)


def destroy(args):
    print(args)


def _build_deploy_cmd(subparsers):
    deploy_cmd = subparsers.add_parser("deploy")
    deploy_cmd.add_argument(
        "-f",
        "--compose-file",
        help="compose manifest file",
        default="docker-compose.yaml",
        required=True,
    )
    deploy_cmd.add_argument("-n", "--name", help="deployment name", required=True)
    deploy_cmd.add_argument(
        "-E",
        "--environment",
        help="environment to deploy on",
        required=True,
    )
    deploy_cmd.add_argument(
        "-S", "--stack-name", help="use this to override stack name"
    )
    deploy_cmd.add_argument(
        "--env-file",
        help="dot env file used for deployment, it will be used as stack environment in portainer",
    )
    deploy_cmd.add_argument(
        "-e",
        "--variable",
        action="append",
        help="environment variable `SOME_ENV=some-value`",
        default=[],
    )
    deploy_cmd.add_argument(
        "-c",
        "--config",
        help="""create config; args must be like `local-path-to-file:conf-name`;
  NOTE that as configs are immutable and might be already in use, your config name must not exist!
  use versioning or date in names to always get a new name
  """,
        action="append",
        default=[],
    )
    deploy_cmd.add_argument(
        "-s",
        "--secret",
        help="create a new secret; see --config.",
        action="append",
        default=[],
    )
    deploy_cmd.set_defaults(func=deploy_app)


def _build_get_cmd(subparsers):
    get_cmd = subparsers.add_parser("get")
    get_cmd.set_defaults(func=lambda args: get_cmd.print_help())

    subcmd = get_cmd.add_subparsers(
        title="supported resources", help="resource to get info"
    )

    def build_get_endpoints_cmd():
        def get(args):
            client = connect(args)
            if args.name:
                print(json.dumps(client.endpoints.get_by_name(args.name)))
            elif args.id:
                print(json.dumps(client.endpoints.get(args.id)))
            else:
                print(json.dumps(client.endpoints.list()))

        endpoints = subcmd.add_parser("endpoints")
        args = endpoints.add_mutually_exclusive_group()
        args.add_argument("-n", "--name")
        args.add_argument("--id")

        endpoints.set_defaults(func=get)

    def build_get_stacks_cmd():
        stacks = subcmd.add_parser("stacks")
        stacks.set_defaults(func=destroy)

    build_get_endpoints_cmd()
    build_get_stacks_cmd()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Portainer deployment client",
        epilog="Use it to automate workflows for less mouse clicks!",
    )
    ### HACK: this is due to a known issue in argparse in python3
    parser.set_defaults(func=lambda args: parser.print_help())

    parser.add_argument(
        "-T",
        "--api-token",
        help="api token for user, overrides PORTAINER_TOKEN variable",
    )
    parser.add_argument(
        "-H",
        "--host",
        help="portainer host, overrides PORTAINER_HOST variable; defaults to `http://127.0.0.1:9000/api`",
        default="http://127.0.0.1:9000/api",
    )
    parser.add_argument(
        "-U",
        "--username",
        help="username to login, overrides PORTAINER_USERNAME variable; defaults to `admin`",
        default="admin",
    )
    parser.add_argument(
        "-P",
        "--password",
        help="password for user, overrides PORTAINER_PASSWORD variable; defaults to admin",
        default="admin",
    )

    parser.add_argument(
        "--debug", help="Whether or not print debugging logs", action="store_true"
    )

    subparsers = parser.add_subparsers(
        title="subcommands", description="valid subcommands", help="additional help"
    )

    _build_deploy_cmd(subparsers)
    _build_get_cmd(subparsers)

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()
    configure_logging(args)
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
