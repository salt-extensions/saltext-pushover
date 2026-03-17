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


def _post_message(
    user,
    device,
    message,
    title,
    priority,
    expire,
    retry,
    sound,
    token=None,
):
    """
    Send a message to a Pushover user or group.

    :param user:        The user or group to send to, must be key of user or group not email address.
    :param message:     The message to send to the Pushover user or group.
    :param title:       Specify who the message is from.
    :param priority     The priority of the message, defaults to 0.
    :param notify:      Whether to notify the room, default: False.
    :param token:       The Pushover token, if not specified in the configuration.
    :return:            Boolean if message was sent successfully.
    """

    pushover.validate_user(user, token, device=device, context=__context__, opts=__opts__)

    parameters = {}
    parameters["user"] = user
    if device is not None:
        parameters["device"] = device
    parameters["title"] = title
    parameters["priority"] = priority
    if expire is not None:
        parameters["expire"] = expire
    if retry is not None:
        parameters["retry"] = retry
    parameters["message"] = message

    if sound and pushover.validate_sound(sound, token):
        parameters["sound"] = sound

    return pushover.query(
        "messages",
        token=token,
        data=parameters,
        opts=__opts__,
    )


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

    if priority and priority == 2:
        if not expire and not retry:
            raise SaltInvocationError(
                "Priority 2 requires pushover.expire and pushover.retry options."
            )

    # pylint: disable=consider-using-f-string
    message = "id: {}\r\nfunction: {}\r\nfunction args: {}\r\njid: {}\r\nreturn: {}\r\n".format(
        ret.get("id"),
        ret.get("fun"),
        ret.get("fun_args"),
        ret.get("jid"),
        pprint.pformat(ret.get("return")),
    )

    try:
        res = _post_message(
            user=user,
            device=device,
            message=message,
            title=title,
            priority=priority,
            expire=expire,
            retry=retry,
            sound=sound,
            token=token,
        )
        log.debug("Pushover result: %s", res)
    except CommandExecutionError as err:
        log.info("Error: %s", err)
