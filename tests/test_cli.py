from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from portainer_ctl import errors
from portainer_ctl.cli import (
    _DEFAULT_HOST,
    _resolve_host,
    parse_mount,
)


# ---------------------------------------------------------------------------
# parse_mount
# ---------------------------------------------------------------------------

def test_parse_mount_valid():
    assert parse_mount("/tmp/conf.txt:my-conf") == ("/tmp/conf.txt", "my-conf")


def test_parse_mount_no_colon_raises():
    with pytest.raises(errors.InvalidCommand):
        parse_mount("no-colon-here")


def test_parse_mount_multiple_colons_uses_first():
    # only the first colon splits; extra colons end up in the name
    path, name = parse_mount("/a/b:name:extra")
    assert path == "/a/b"
    assert name == "name:extra"


# ---------------------------------------------------------------------------
# _resolve_host priority: CLI flag > env var > built-in default
# ---------------------------------------------------------------------------

def _args(host=None):
    ns = argparse.Namespace()
    ns.host = host
    return ns


def test_resolve_host_cli_wins_over_env():
    with patch.dict("os.environ", {"PORTAINER_HOST": "http://from-env:9000/api"}):
        assert _resolve_host(_args(host="http://from-cli:9000/api")) == "http://from-cli:9000/api"


def test_resolve_host_env_used_when_no_cli():
    with patch.dict("os.environ", {"PORTAINER_HOST": "http://from-env:9000/api"}):
        assert _resolve_host(_args()) == "http://from-env:9000/api"


def test_resolve_host_default_when_nothing_set():
    with patch.dict("os.environ", {}, clear=True):
        # ensure the variable is absent even if set in the outer environment
        import os
        os.environ.pop("PORTAINER_HOST", None)
        assert _resolve_host(_args()) == _DEFAULT_HOST


# ---------------------------------------------------------------------------
# env file / variable parsing (tested via the deploy logic extracted inline)
# ---------------------------------------------------------------------------

def _parse_env_lines(lines: list[str]) -> dict:
    """Mirror the parsing loop from cli.deploy so we can unit-test it."""
    variables = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        idx = stripped.find("=")
        if idx < 0:
            continue
        variables[stripped[:idx]] = stripped[idx + 1:]
    return variables


def test_env_parsing_basic():
    assert _parse_env_lines(["FOO=bar\n"]) == {"FOO": "bar"}


def test_env_parsing_skips_blank_lines():
    assert _parse_env_lines(["", "  ", "\n", "FOO=1"]) == {"FOO": "1"}


def test_env_parsing_skips_comments():
    assert _parse_env_lines(["# comment", "FOO=1"]) == {"FOO": "1"}


def test_env_parsing_skips_lines_without_equals():
    assert _parse_env_lines(["NOEQUALSSIGN", "FOO=1"]) == {"FOO": "1"}


def test_env_parsing_value_with_equals():
    assert _parse_env_lines(["FOO=a=b=c"]) == {"FOO": "a=b=c"}


def test_env_parsing_empty_value():
    assert _parse_env_lines(["FOO="]) == {"FOO": ""}
