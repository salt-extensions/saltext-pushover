import pytest
import salt.modules.test as testmod
import saltext.pushover.modules.pushover_mod as pushover_module
import saltext.pushover.states.pushover_mod as pushover_state


@pytest.fixture
def configure_loader_modules():
    return {
        pushover_module: {
            "__salt__": {
                "test.echo": testmod.echo,
            },
        },
        pushover_state: {
            "__salt__": {
                "pushover.example_function": pushover_module.example_function,
            },
        },
    }


def test_replace_this_this_with_something_meaningful():
    echo_str = "Echoed!"
    expected = {
        "name": echo_str,
        "changes": {},
        "result": True,
        "comment": f"The 'pushover.example_function' returned: '{echo_str}'",
    }
    assert pushover_state.exampled(echo_str) == expected
