import json
from unittest.mock import patch

import pytest

import saltext.pushover.returners.pushover_returner as po


@pytest.fixture
def configure_loader_modules():
    return {
        po: {},
    }


@pytest.fixture(autouse=True)
def config():
    conf = {
        "title": "title",
        "user": "user",
        "device": "device",
        "priority": 1,
        "expire": 180,
        "retry": 33,
        "sound": "bike",
        "token": "token",
    }
    with patch(
        "saltext.pushover.returners.pushover_returner._get_options", autospec=True
    ) as getopts:
        getopts.return_value = conf
        yield getopts


@pytest.fixture
def http_query():
    with patch("salt.utils.http.query", autospec=True) as query:
        query.return_value = {"status": 200, "dict": {}, "text": "{}"}
        yield query


def test_returner(http_query):
    ret = {
        "id": "id",
        "fun": "fun",
        "fun_args": [],
        "jid": "jid",
        "return": {"foo": True},
    }
    po.returner(ret)
    http_query.assert_called_once()
    data = json.loads(http_query.call_args[1]["data"])
    exp_msg = (
        "id: id\r\nfunction: fun\r\nfunction args: []\r\njid: jid\r\nreturn: {'foo': True}\r\n"
    )
    assert data == {
        "user": "user",
        "title": "title",
        "priority": 1,
        "message": exp_msg,
        "device": "device",
        "expire": 180,
        "retry": 33,
        "sound": "bike",
        "token": "token",
    }


def test_returner_err_no_crash(http_query):
    """
    Ensure the returner does not leak exceptions from the utils module
    """
    http_query.return_value = {"status": 500, "body": ""}
    ret = {
        "id": "id",
        "fun": "fun",
        "fun_args": [],
        "jid": "jid",
        "return": {"foo": True},
    }
    po.returner(ret)
    http_query.assert_called_once()
