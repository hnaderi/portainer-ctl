import pytest

from portainer_ctl.helpers import to_base64


def test_to_base64_ascii():
    assert to_base64("hello") == "aGVsbG8="


def test_to_base64_multiline():
    assert to_base64("foo\nbar") == "Zm9vCmJhcg=="


def test_to_base64_empty():
    assert to_base64("") == ""
