#!/usr/bin/env python

import argparse
import json
import logging
import sys
from os import getenv

from rich import print
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich_argparse import ArgumentDefaultsRichHelpFormatter

from . import errors, models, printer
from .api import Portainer
from .client import Client


def configure_logging(args):
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )


def subcommand(parser: argparse._SubParsersAction, name: str, **kwargs):
    return parser.add_parser(
        name, formatter_class=ArgumentDefaultsRichHelpFormatter, **kwargs
    )


def parse_mount(conf: str):
    try:
        path, name = conf.split(":")
        return (path, name)
    except Exception:
        raise errors.InvalidCommand("invalid mount argument: " + conf)


def name_or_id_group(parser: argparse.ArgumentParser):
    args = parser.add_mutually_exclusive_group(required=True)
    args.add_argument("-n", "--name")
    args.add_argument("--id")


def docker_filter_group(parser: argparse.ArgumentParser):
    args = parser.add_argument_group()
    args.add_argument(
        "-n",
        "--name",
        action="append",
        default=[],
    )
    args.add_argument(
        "-l",
        "--label",
        action="append",
        default=[],
    )
    args.add_argument(
        "--id",
        action="append",
        default=[],
    )


def file_or_inline(parser: argparse.ArgumentParser):
    args = parser.add_mutually_exclusive_group(required=True)
    args.add_argument("-f", "--file")
    args.add_argument("--value")


def requires_endpoint(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-E",
        "--endpoint",
        help="id of the endpoint to deploy on",
        required=True,
    )


def read_string(path):
    with open(path, "r") as f:
        return "".join(f.readlines())


def get_unauthenticated_api(args):
    client = Client(args.host)
    return Portainer(client)


def get_authenticated_api(args):
    HOST = getenv("PORTAINER_HOST", args.host)
    PASSWORD = getenv("PORTAINER_PASSWORD", args.password)
    USERNAME = getenv("PORTAINER_USERNAME", args.username)
    API_TOKEN = getenv("PORTAINER_TOKEN", args.api_token)

    client = Client(HOST)
    if API_TOKEN:
        client.authorize(API_TOKEN)
    else:
        client.login(USERNAME, PASSWORD)
    return Portainer(client)


def deploy(args):
    request = models.DeploymentRequest()
    api = get_authenticated_api(args)

    request.name = args.stack_name

    with open(args.compose_file, "r") as f:
        request.compose = "".join(f.readlines())

    env_lines = args.variable
    if args.env_file != None:
        with open(args.env_file, "r") as f:
            lines = f.readlines()
            env_lines = env_lines + lines

    request.variables = dict()
    for line in env_lines:
        striped = line.strip()
        idx = striped.find("=")
        request.variables[striped[:idx]] = striped[idx + 1 :]

    request.configs = dict(
        [
            (name, read_string(path))
            for (path, name) in [parse_mount(conf) for conf in args.config]
        ]
    )

    request.secrets = dict(
        [
            (name, read_string(path))
            for (path, name) in [parse_mount(conf) for conf in args.secret]
        ]
    )

    return api.endpoint(args.endpoint).deploy(request, args.no_error)


def _build_deploy_cmd(subparsers):
    deploy_cmd = subcommand(subparsers, "deploy")
    deploy_cmd.add_argument(
        "-f",
        "--compose-file",
        help="compose manifest file",
        default="docker-compose.yaml",
        required=True,
    )
    requires_endpoint(deploy_cmd)
    deploy_cmd.add_argument(
        "-S",
        "--stack-name",
        help="Name of the stack to create or update",
        required=True,
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

    deploy_cmd.add_argument(
        "-K",
        "--no-error",
        help="Don't raise error if there are existing configs or secrets",
        action="store_true",
    )
    deploy_cmd.set_defaults(func=deploy)


def _build_endpoints_cmd(subparsers):
    endpoints_cmd = subcommand(subparsers, "endpoints")
    endpoints_cmd.set_defaults(func=lambda args: endpoints_cmd.print_help())

    subcmd = endpoints_cmd.add_subparsers(
        title="supported resources", help="resource to get info"
    )

    def get(args):
        client = get_authenticated_api(args)
        if args.name:
            printer.print(args, data=client.endpoints.get_by_name(args.name))
        elif args.id:
            printer.print(args, data=client.endpoints.get(args.id))

    def ls(args):
        client = get_authenticated_api(args)

        printer.print(
            args,
            data=client.endpoints.list(),
            columns=["Id", "Name", "Type", "URL", "ContainerEngine"],
        )

    def info(args):
        client = get_authenticated_api(args)
        printer.print(args, data=client.endpoint(args.endpoint).get_docker_info())

    def version(args):
        client = get_authenticated_api(args)
        printer.print(args, data=client.endpoint(args.endpoint).get_docker_version())

    def create(args):
        client = get_authenticated_api(args)
        request = models.EndpointCreationRequest()
        request.name = args.name
        request.tagIds = args.tag
        request.groupId = args.group
        request.url = args.url
        request.type = args.type

        printer.print(args, data=client.endpoints.create(request))

    get_cmd = subcommand(subcmd, "get")
    name_or_id_group(get_cmd)
    get_cmd.set_defaults(func=get)

    ls_cmd = subcommand(subcmd, "ls")
    ls_cmd.set_defaults(func=ls)

    create_cmd = subcommand(subcmd, "create")
    create_cmd.add_argument("name", help="Endpoint name")
    create_cmd.add_argument(
        "--type",
        choices=list(models.EndpointCreationType),
        type=models.EndpointCreationType.from_string,
    )
    create_cmd.add_argument("-u", "--url")
    create_cmd.add_argument(
        "-t",
        "--tag",
        action="append",
        default=[],
    )
    create_cmd.add_argument("-g", "--group")
    create_cmd.set_defaults(func=create)

    info_cmd = subcommand(subcmd, "info")
    requires_endpoint(info_cmd)
    info_cmd.set_defaults(func=info)

    version_cmd = subcommand(subcmd, "version")
    requires_endpoint(version_cmd)
    version_cmd.set_defaults(func=version)


def _build_stacks_cmd(subparsers):
    stacks_cmd = subcommand(subparsers, "stacks")
    stacks_cmd.set_defaults(func=lambda args: stacks_cmd.print_help())

    subcmd = stacks_cmd.add_subparsers(
        title="supported resources", help="resource to get info"
    )

    def get(args):
        client = get_authenticated_api(args)
        if args.name:
            printer.print(args, data=client.stacks.get_stacks_by_name(args.name))
        elif args.id:
            printer.print(args, data=client.stacks.get(args.id))

    def get_file(args):
        client = get_authenticated_api(args)
        printer.raw(client.stacks.get_file(args.id))

    def ls(args):
        client = get_authenticated_api(args)
        printer.print(
            args,
            data=client.stacks.list(),
            columns=["Id", "Name", "Type", "Status", "EndpointId", "SwarmId"],
        )

    def delete(args):
        client = get_authenticated_api(args)
        if args.id:
            printer.print(
                args,
                client.endpoint(args.endpoint).stacks.delete(args.id, args.external),
            )
        elif args.name:
            printer.print(
                args,
                client.endpoint(args.endpoint).stacks.delete_by_name(
                    args.name, args.external
                ),
            )

    def start(args):
        client = get_authenticated_api(args)
        printer.print(args, data=client.endpoint(args.endpoint).stacks.start(args.id))

    def stop(args):
        client = get_authenticated_api(args)
        printer.print(args, data=client.endpoint(args.endpoint).stacks.stop(args.id))

    _build_deploy_cmd(subcmd)

    ls_cmd = subcommand(subcmd, "ls")
    ls_cmd.set_defaults(func=ls)

    get_cmd = subcommand(subcmd, "get")
    name_or_id_group(get_cmd)
    get_cmd.set_defaults(func=get)

    get_file_cmd = subcmd.add_parser("get-file")
    get_file_cmd.add_argument("id")
    get_file_cmd.set_defaults(func=get_file)

    start_cmd = subcommand(subcmd, "start")
    start_cmd.add_argument("id")
    requires_endpoint(start_cmd)
    start_cmd.set_defaults(func=start)

    stop_cmd = subcommand(subcmd, "stop")
    stop_cmd.add_argument("id")
    requires_endpoint(stop_cmd)
    stop_cmd.set_defaults(func=stop)

    delete_cmd = subcommand(subcmd, "delete")
    name_or_id_group(delete_cmd)
    requires_endpoint(delete_cmd)
    delete_cmd.add_argument(
        "--external",
        help="Whether or not delete if it is an external stack",
        action="store_true",
    )
    delete_cmd.set_defaults(func=delete)


def _build_tags_cmd(subparsers):
    tags_cmd = subcommand(subparsers, "tags")
    tags_cmd.set_defaults(func=lambda args: tags_cmd.print_help())

    subcmd = tags_cmd.add_subparsers(
        title="supported resources", help="resource to get info"
    )

    def create(args):
        client = get_authenticated_api(args)
        printer.print(args, data=client.tags.create(args.name))

    def ls(args):
        client = get_authenticated_api(args)
        printer.print(args, data=client.tags.list())

    def delete(args):
        client = get_authenticated_api(args)
        client.tags.delete(args.id)

    create_cmd = subcommand(subcmd, "create")
    create_cmd.add_argument("name")
    create_cmd.set_defaults(func=create)

    ls_cmd = subcommand(subcmd, "ls")
    ls_cmd.set_defaults(func=ls)

    delete_cmd = subcommand(subcmd, "delete")
    delete_cmd.add_argument("id")
    delete_cmd.set_defaults(func=delete)


def _build_secrets_cmd(subparsers):
    secrets_cmd = subcommand(subparsers, "secrets")
    secrets_cmd.set_defaults(func=lambda args: secrets_cmd.print_help())

    subcmd = secrets_cmd.add_subparsers(
        title="supported resources", help="resource to get info"
    )

    requires_endpoint(secrets_cmd)

    def create(args):
        client = get_authenticated_api(args)
        data = args.value if args.value else read_string(args.file)
        printer.print(
            args, client.endpoint(args.endpoint).secrets.create(args.name, data)
        )

    def ls(args):
        client = get_authenticated_api(args)
        printer.print(
            args,
            client.endpoint(args.endpoint).secrets.ls(
                id=args.id, name=args.name, label=args.label
            ),
        )

    def delete(args):
        client = get_authenticated_api(args)
        client.endpoint(args.endpoint).secrets.delete(args.id)

    create_cmd = subcommand(subcmd, "create")
    create_cmd.add_argument("name")
    file_or_inline(create_cmd)
    create_cmd.set_defaults(func=create)

    ls_cmd = subcommand(subcmd, "ls")
    docker_filter_group(ls_cmd)
    ls_cmd.set_defaults(func=ls)

    delete_cmd = subcommand(subcmd, "delete")
    delete_cmd.add_argument("id")
    delete_cmd.set_defaults(func=delete)


def _build_configs_cmd(subparsers):
    configs_cmd = subcommand(subparsers, "configs")
    configs_cmd.set_defaults(func=lambda args: configs_cmd.print_help())

    subcmd = configs_cmd.add_subparsers(
        title="supported resources", help="resource to get info"
    )

    requires_endpoint(configs_cmd)

    def create(args):
        client = get_authenticated_api(args)
        data = args.value if args.value else read_string(args.file)
        printer.print(
            args, client.endpoint(args.endpoint).configs.create(args.name, data)
        )

    def ls(args):
        client = get_authenticated_api(args)
        printer.print(
            args,
            client.endpoint(args.endpoint).configs.ls(
                id=args.id, name=args.name, label=args.label
            ),
        )

    def delete(args):
        client = get_authenticated_api(args)
        client.endpoint(args.endpoint).configs.delete(args.id)

    create_cmd = subcommand(subcmd, "create")
    create_cmd.add_argument("name")
    file_or_inline(create_cmd)
    create_cmd.set_defaults(func=create)

    ls_cmd = subcommand(subcmd, "ls")
    docker_filter_group(ls_cmd)
    ls_cmd.set_defaults(func=ls)

    delete_cmd = subcommand(subcmd, "delete")
    delete_cmd.add_argument("id")
    delete_cmd.set_defaults(func=delete)


def _build_system_cmd(subparsers):
    cmd = subcommand(subparsers, "system")
    cmd.set_defaults(func=lambda args: cmd.print_help())

    subcmd = cmd.add_subparsers(
        title="supported resources", help="resource to get info"
    )

    def build_init_cmd():
        def init(args):
            PASSWORD = getenv("PORTAINER_PASSWORD", args.password)
            USERNAME = getenv("PORTAINER_USERNAME", args.username)
            if not (USERNAME and PASSWORD):
                raise errors.InvalidCommand(
                    "Both username and password are required for admin initiation."
                )
            portainer = get_unauthenticated_api(args)

            printer.print(
                args, portainer.public.init(username=USERNAME, password=PASSWORD)
            )

        init_cmd = subcommand(subcmd, "init")
        init_cmd.set_defaults(func=init)

    def build_status_cmd():
        def get(args):
            client = get_unauthenticated_api(args)
            printer.print(args, data=client.public.status())

        status = subcommand(subcmd, "status")
        status.set_defaults(func=get)

    build_init_cmd()
    build_status_cmd()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Poorman's kubectl, CLI for portainer on docker swarm",
        epilog=Markdown("""No budget. No vendors. No fleet of ops.
        Just you, a blinking cursor, and the will to script what others buy.
        The rich scale with dollars. You scale with shell.
        Excuses cost, Automation pays!
        """, style="italic sky_blue1"),
        formatter_class=ArgumentDefaultsRichHelpFormatter,
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
        help="portainer host, overrides PORTAINER_HOST variable",
        default="http://127.0.0.1:9000/api",
    )
    parser.add_argument(
        "-U",
        "--username",
        help="username to login, overrides PORTAINER_USERNAME variable",
        default="admin",
    )
    parser.add_argument(
        "-P",
        "--password",
        help="password for user, overrides PORTAINER_PASSWORD variable",
        default="admin",
    )

    parser.add_argument(
        "--debug", help="Whether or not print debugging logs", action="store_true"
    )

    parser.add_argument("-j", "--json", help="Print json output", action="store_true")

    subparsers = parser.add_subparsers(title="commands")

    _build_deploy_cmd(subparsers)
    _build_stacks_cmd(subparsers)
    _build_configs_cmd(subparsers)
    _build_secrets_cmd(subparsers)
    _build_endpoints_cmd(subparsers)
    _build_tags_cmd(subparsers)
    _build_system_cmd(subparsers)

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()
    configure_logging(args)
    try:
        args.func(args)
    except errors.InvalidCommand as err:
        print(err.msg, file=sys.stderr)
        sys.exit(1)
    except errors.RequestError as err:
        print(err.url, err.status, err.body, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
