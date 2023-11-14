import pytest
import salt.modules.test as testmod
import saltext.pushover.modules.pushover_mod as pushover_module


@pytest.fixture
def configure_loader_modules():
    module_globals = {
        "__salt__": {"test.echo": testmod.echo},
    }
    return {
        pushover_module: module_globals,
    }


def test_replace_this_this_with_something_meaningful():
    echo_str = "Echoed!"
    assert pushover_module.example_function(echo_str) == echo_str
