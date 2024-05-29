"""
Send notifications via `Pushover <https://www.pushover.net>`_.

.. important::
    See :ref:`Configuration <pushover-setup>` for a description of
    available configuration parameters.
"""

import logging
import urllib.parse

from salt.exceptions import SaltInvocationError

import saltext.pushover.utils.pushover

log = logging.getLogger(__name__)
__virtualname__ = "pushover"


def __virtual__():
    return __virtualname__


def post_message(
    user=None,
    device=None,
    message=None,
    title=None,
    priority=0,
    expire=None,
    retry=None,
    sound=None,
    api_version=1,  # pylint: disable=unused-argument
    token=None,
):
    """
    Send a message to a Pushover user or group.

    CLI Example:

    .. code-block:: bash

        salt '*' pushover.post_message user='uQiRzpo4DXghDmr9QzzfQu27cmVRsG' title='Message from Salt' message='Build is done'

        salt '*' pushover.post_message user='uQiRzpo4DXghDmr9QzzfQu27cmVRsG' title='Message from Salt' message='Build is done' priority='2' expire='720' retry='5'

    user
        The user or group of users to send the message to. Must be a user/group ID (key),
        not a name or an email address.
        Required if not specified in the configuration.

    device
        The name of the device to send the message to.

    message
        The message to send to the Pushover user or group. Required.

    title
        The message title to use. Defaults to ``Message from SaltStack``.

    priority
        The priority of the message (integers between ``-2`` and ``2``).
        Defaults to ``0``.

        .. note::

            Emergency priority (``2``) requires ``expire`` and ``retry`` parameters
            to be set.

    expire
        Stop notifying the user after the specified amount of seconds.
        The message is still shown after expiry.

    retry
        Repeat the notification after this amount of seconds. Minimum: ``30``.

    sound
        The `notification sound <https://pushover.net/api#sounds>`_ to play.

    token
        The authentication token to use for the Pushover API.
        Required if not specified in the configuration.
    """

    if not token:
        token = __salt__["config.get"]("pushover.token") or __salt__["config.get"]("pushover:token")
        if not token:
            raise SaltInvocationError("Pushover token is unavailable.")

    if not user:
        user = __salt__["config.get"]("pushover.user") or __salt__["config.get"]("pushover:user")
        if not user:
            raise SaltInvocationError("Pushover user key is unavailable.")

    if not message:
        raise SaltInvocationError('Required parameter "message" is missing.')

    if priority not in range(-2, 3):
        raise SaltInvocationError(
            f"Invalid priority {priority}. Needs to be an integer between -2 and 2 (inclusive)"
        )

    if priority == 2 and not (expire and retry):
        raise SaltInvocationError(
            "Emergency messages require `expire` and `retry` parameters to be set"
        )

    if retry and retry < 30:
        raise SaltInvocationError("`retry` needs to be at least 30 (seconds)")

    user_validate = saltext.pushover.utils.pushover.validate_user(user, device, token)
    if not user_validate["result"]:
        return user_validate

    if not title:
        title = "Message from SaltStack"

    parameters = dict()
    parameters["user"] = user
    if device is not None:
        parameters["device"] = device
    parameters["token"] = token
    parameters["title"] = title
    parameters["priority"] = priority
    if expire is not None:
        parameters["expire"] = expire
    if retry is not None:
        parameters["retry"] = retry
    parameters["message"] = message

    if sound and saltext.pushover.utils.pushover.validate_sound(sound, token)["res"]:
        parameters["sound"] = sound

    result = saltext.pushover.utils.pushover.query(
        function="message",
        method="POST",
        header_dict={"Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode(parameters),
        opts=__opts__,
    )

    if result["res"]:
        return True
    else:
        return result
