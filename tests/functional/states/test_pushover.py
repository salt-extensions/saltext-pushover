import pytest

pytestmark = [
    pytest.mark.requires_salt_states("pushover.exampled"),
]


@pytest.fixture
def pushover(states):
    return states.pushover


def test_replace_this_this_with_something_meaningful(pushover):
    echo_str = "Echoed!"
    ret = pushover.exampled(echo_str)
    assert ret.result
    assert not ret.changes
    assert echo_str in ret.comment
