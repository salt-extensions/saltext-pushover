from unittest.mock import Mock
from unittest.mock import patch

import pytest

import saltext.pushover.modules.pushover_notify as pushover_exemod
import saltext.pushover.states.pushover as po


@pytest.fixture
def configure_loader_modules():
    return {
        po: {},
    }


@pytest.fixture
def post_message():
    send = Mock(spec=pushover_exemod.post_message)
    with patch.dict(po.__salt__, {"pushover.post_message": send}):
        yield send


@pytest.fixture(params=(False, True))
def test_mode(request):
    with patch.dict(po.__opts__, {"test": request.param}):
        yield request.param


def test_pushover_state(test_mode, post_message):
    message = "Chaos is a ladder"
    ret = po.post_message("event", "user", message=message)
    assert isinstance(ret, dict)
    assert ret["name"] == "event"
    assert not ret["changes"]
    if test_mode:
        assert message in ret["comment"]
        assert ret["result"] is None
        assert "is to be sent" in ret["comment"]
        post_message.assert_not_called()
    else:
        assert "event" in ret["comment"]
        assert ret["result"] is True
        assert ret["comment"].startswith("Sent message")
        post_message.assert_called_once_with(
            user="user",
            message=message,
            title=None,
            device=None,
            priority=None,
            expire=None,
            retry=None,
            token=None,
        )
