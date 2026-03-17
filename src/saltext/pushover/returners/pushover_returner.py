"""
Return Salt data via `Pushover <https://pushover.net>`_.

.. important::
    See :ref:`Configuration <pushover-setup>` for a description of
    available configuration parameters.

Usage
-----
To use the Pushover returner, pass ``--return pushover`` to the Salt command:

.. code-block:: bash

    salt '*' test.ping --return pushover

Alternative configuration profiles can be requested via the ``--return_config`` parameter:

.. code-block:: bash

    salt '*' test.ping --return pushover --return_config alternative

To override individual configuration items during the call, pass
``--return_kwargs '{"key:": "value"}'`` to the Salt command.

.. code-block:: bash

    salt '*' test.ping --return pushover --return_kwargs '{"title": "Salt is awesome!"}'
"""

import logging
import pprint

import salt.returners
from salt.exceptions import CommandExecutionError
from salt.exceptions import SaltInvocationError

from saltext.pushover.utils import pushover

log = logging.getLogger(__name__)

__virtualname__ = "pushover"


def __virtual__():
    return __virtualname__


def _get_options(ret=None):
    defaults = {"priority": "0"}

    attrs = {
        "pushover_profile": "profile",
        "user": "user",
        "device": "device",
        "token": "token",
        "priority": "priority",
        "title": "title",
        "expire": "expire",
        "retry": "retry",
        "sound": "sound",
    }

    profile_attr = "pushover_profile"

    profile_attrs = {
        "user": "user",
        "device": "device",
        "token": "token",
        "priority": "priority",
        "title": "title",
        "expire": "expire",
        "retry": "retry",
        "sound": "sound",
    }

    _options = salt.returners.get_returner_options(
        __virtualname__,
        ret,
        attrs,
        profile_attr=profile_attr,
        profile_attrs=profile_attrs,
        __salt__=__salt__,
        __opts__=__opts__,
        defaults=defaults,
    )
    return _options


def returner(ret):
    """
    Send a Pushover notification with the return data.
    """

    _options = _get_options(ret)

    user = _options.get("user")
    device = _options.get("device")
    token = _options.get("token")
    title = _options.get("title")
    priority = _options.get("priority")
    expire = _options.get("expire")
    retry = _options.get("retry")
    sound = _options.get("sound")

    if not token:
        raise SaltInvocationError("Pushover token is unavailable.")

    if not user:
        raise SaltInvocationError("Pushover user key is unavailable.")

    # pylint: disable=consider-using-f-string
    message = "id: {}\r\nfunction: {}\r\nfunction args: {}\r\njid: {}\r\nreturn: {}\r\n".format(
        ret.get("id"),
        ret.get("fun"),
        ret.get("fun_args"),
        ret.get("jid"),
        pprint.pformat(ret.get("return")),
    )

    try:
        res = pushover.post_message(
            message,
            user,
            token,
            title=title,
            device=device,
            priority=priority,
            expire=expire,
            retry=retry,
            sound=sound,
            opts=__opts__,
        )
        log.debug("Pushover result: %s", res)
    except CommandExecutionError as err:
        log.info("Error: %s", err)
