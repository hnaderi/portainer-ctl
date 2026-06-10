from unittest.mock import MagicMock

import pytest

from portainer_ctl import errors
from portainer_ctl.api import GlobalStacksAPI, StacksAPI


def _mock_client(get_return=None, put_return=None, post_return=None):
    client = MagicMock()
    client.get.return_value = get_return
    client.put.return_value = put_return
    client.post.return_value = post_return
    return client


# ---------------------------------------------------------------------------
# GlobalStacksAPI.get_stack_id_by_name
# ---------------------------------------------------------------------------

def test_get_stack_id_by_name_returns_id():
    client = _mock_client(get_return=[{"Id": 42, "Name": "mystack"}])
    api = GlobalStacksAPI(client)
    assert api.get_stack_id_by_name("mystack") == 42


def test_get_stack_id_by_name_not_found_raises():
    client = _mock_client(get_return=[])
    api = GlobalStacksAPI(client)
    with pytest.raises(errors.InvalidCommand):
        api.get_stack_id_by_name("missing")


def test_get_stack_id_by_name_filters_by_name():
    # API may return stacks that don't exactly match the name filter
    client = _mock_client(get_return=[
        {"Id": 1, "Name": "mystack"},
        {"Id": 2, "Name": "mystack-old"},
    ])
    api = GlobalStacksAPI(client)
    assert api.get_stack_id_by_name("mystack") == 1


# ---------------------------------------------------------------------------
# StacksAPI.create — update / create / ambiguous branches
# ---------------------------------------------------------------------------

def _stacks_api(client, endpoint_id="1"):
    return StacksAPI(client, endpoint_id)


def test_create_updates_when_one_existing_stack():
    client = _mock_client(
        get_return=[{"Id": 7, "Name": "app"}],
        put_return={"Id": 7},
    )
    api = _stacks_api(client)
    api.create("app", "compose-content", [])
    client.put.assert_called_once()
    assert "/stacks/7" in client.put.call_args[0][0]


def test_create_raises_on_multiple_stacks_with_same_name():
    client = _mock_client(get_return=[
        {"Id": 1, "Name": "app"},
        {"Id": 2, "Name": "app"},
    ])
    api = _stacks_api(client)
    with pytest.raises(errors.InvalidCommand, match="Multiple stacks"):
        api.create("app", "compose-content", [])


def test_create_new_stack_in_swarm():
    docker_info = {"Swarm": {"Cluster": {"ID": "swarm-abc"}}}
    client = _mock_client(
        get_return=[],           # no existing stacks
        post_return={"Id": 99},
    )
    # get() is called twice: once for stacks list, once for docker info via EndpointAPI
    client.get.side_effect = [
        [],                      # GlobalStacksAPI.list (get_stacks_by_name)
        {"ApiVersion": "1.41"},  # EndpointAPI.__init__ version call
        docker_info,             # EndpointAPI.get_docker_info
    ]
    api = _stacks_api(client)
    api.create("newapp", "compose-content", [])
    client.post.assert_called_once()
    assert "swarm/string" in client.post.call_args[0][0]


def test_create_raises_when_not_in_swarm():
    client = _mock_client()
    client.get.side_effect = [
        [],                              # no existing stacks
        {"ApiVersion": "1.41"},          # EndpointAPI version
        {"Swarm": None},                 # docker info — not in swarm
    ]
    api = _stacks_api(client)
    with pytest.raises(errors.InvalidCommand, match="Swarm"):
        api.create("newapp", "compose-content", [])
