import json
from unittest.mock import patch

import pytest
from salt.exceptions import CommandExecutionError

import saltext.pushover.modules.pushover_notify as po


def _config_get(conf, *_args, **_kwargs):
    return conf


@pytest.fixture
def configure_loader_modules(context):
    return {
        po: {
            "__salt__": {"config.get": _config_get},
            "__context__": context,
        },
    }


@pytest.fixture
def context():
    return {"keep dict ref": True}


@pytest.fixture
def http_query():
    with patch("salt.utils.http.query", autospec=True) as query:
        query.return_value = {"status": 200, "dict": {}, "text": "{}"}
        yield query


def test_post_message_bare(http_query):
    po.post_message("Hi")
    http_query.assert_called_once()
    args, kwargs = http_query.call_args
    assert args[0] == "https://api.pushover.net/1/messages.json"
    assert args[1] == "POST"
    data = json.loads(kwargs["data"])
    assert data == {
        "user": "pushover.user",
        "priority": 0,
        "message": "Hi",
        "title": "Message from Salt",
        "token": "pushover.token",
    }


def test_post_message_all(http_query):
    po.post_message(
        "Hi",
        title="title",
        user="user",
        device="device",
        priority=1,
        expire=180,
        retry=33,
        sound="bike",
        token="token",
    )
    http_query.assert_called_once()
    data = json.loads(http_query.call_args[1]["data"])
    assert data == {
        "user": "user",
        "title": "title",
        "priority": 1,
        "message": "Hi",
        "device": "device",
        "expire": 180,
        "retry": 33,
        "sound": "bike",
        "token": "token",
    }


def test_validate_user_user_ok(http_query):
    po.validate_user()
    args, kwargs = http_query.call_args
    assert args[0] == "https://api.pushover.net/1/users/validate.json"
    assert args[1] == "POST"
    data = json.loads(kwargs["data"])
    data = json.loads(http_query.call_args[1]["data"])
    assert data == {"user": "pushover.user", "token": "pushover.token"}


def test_validate_user_user_fail(http_query):
    prev_ret = http_query.return_value
    http_query.return_value = {
        "status": 400,
        "error": "HTTP 400: Bad Request",
        "body": '{"user":"invalid","errors":["user key is invalid"],"status":0,"request":"6aa7ec75-11a0-426a-88a4-a71437519c46"}',
        "dict": {
            "user": "invalid",
            "errors": ["user key is invalid"],
            "status": 0,
            "request": "6aa7ec75-11a0-426a-88a4-a71437519c46",
        },
    }
    with pytest.raises(CommandExecutionError, match=".*Invalid user"):
        po.validate_user()
    data = json.loads(http_query.call_args[1]["data"])
    assert data == {"user": "pushover.user", "token": "pushover.token"}
    http_query.return_value = prev_ret
    # Check that we don't cache negative results to keep false negatives low
    po.validate_user()


def test_validate_user_device_ok(http_query):
    po.validate_user(user="foo", token="token", device="device")
    data = json.loads(http_query.call_args[1]["data"])
    assert data == {"user": "foo", "token": "token", "device": "device"}


def test_validate_user_device_fail(http_query):
    http_query.return_value = {
        "status": 400,
        "error": "HTTP 400: Bad Request",
        "body": '{"device":"invalid for this user","group":0,"licenses":["iOS"],"errors":["device name is not valid for user"],"status":0,"request":"19c385f6-8a7d-462f-a531-33d3f3d4bbbe"}',
        "dict": {
            "device": "invalid for this user",
            "group": 0,
            "licenses": ["iOS"],
            "errors": ["device name is not valid for user"],
            "status": 0,
            "request": "19c385f6-8a7d-462f-a531-33d3f3d4bbbe",
        },
    }
    with pytest.raises(CommandExecutionError, match=".*Invalid device.*"):
        po.validate_user()
    data = json.loads(http_query.call_args[1]["data"])
    assert data == {"user": "pushover.user", "token": "pushover.token"}


def test_validate_sound_ok(http_query, context):
    http_query.return_value = {
        "status": 200,
        "dict": {"sounds": {"bike": "description", "foo": "other"}},
    }
    po.validate_sound("bike")
    http_query.assert_called_once()
    args, kwargs = http_query.call_args
    assert args[0] == "https://api.pushover.net/1/sounds.json"
    assert args[1] == "GET"
    assert kwargs["params"] == {"token": "pushover.token"}
    po.validate_sound("bike")
    http_query.assert_called_once()
    po.validate_sound("other")
    http_query.assert_called_once()
    context["pushover_sounds"]["new"] = "fake"
    po.validate_sound("new")
    http_query.assert_called_once()


def test_validate_sound_err(http_query, context):
    http_query.return_value = {
        "status": 200,
        "dict": {"sounds": {"bike": "description", "foo": "other"}},
    }
    po.validate_sound("bike")
    http_query.assert_called_once()
    args, kwargs = http_query.call_args
    assert args[0] == "https://api.pushover.net/1/sounds.json"
    assert args[1] == "GET"
    assert kwargs["params"] == {"token": "pushover.token"}
    po.validate_sound("bike")
    http_query.assert_called_once()
    po.validate_sound("other")
    http_query.assert_called_once()
    context["pushover_sounds"]["new"] = "fake"
    po.validate_sound("new")
    http_query.assert_called_once()
