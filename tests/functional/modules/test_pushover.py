import pytest

pytestmark = [
    pytest.mark.requires_salt_modules("pushover.example_function"),
]


@pytest.fixture
def pushover(modules):
    return modules.pushover


def test_replace_this_this_with_something_meaningful(pushover):
    echo_str = "Echoed!"
    res = pushover.example_function(echo_str)
    assert res == echo_str
