"""
Send notifications via `Pushover <https://pushover.net>`_.

.. important::
    See :ref:`Configuration <pushover-setup>` for a description of
    available configuration parameters.
"""

import logging

from salt.exceptions import SaltInvocationError

from saltext.pushover.utils import pushover

log = logging.getLogger(__name__)

__virtualname__ = "pushover"


def __virtual__():
    return __virtualname__


def _resolve_token(token):
    token = (
        token
        or __salt__["config.get"]("pushover.token")
        or __salt__["config.get"]("pushover:token")
    )
    if not token:
        raise SaltInvocationError("Pushover token is unavailable.")
    return token


def _resolve_user(user):
    user = (
        user or __salt__["config.get"]("pushover.user") or __salt__["config.get"]("pushover:user")
    )
    if not user:
        raise SaltInvocationError("Pushover user key is unavailable.")
    return user


def post_message(
    message,
    title=None,
    user=None,
    device=None,
    priority=0,
    expire=None,
    retry=None,
    sound=None,
    token=None,
):
    """
    .. versionchanged:: 2.0.0
        Parameters have been reordered.

        ``device`` and ``sound`` parameters are no longer validated
        to avoid unnecessary queries. Pushover defaults to all devices/the default sound in case the values are invalid.

    Send a message to a Pushover user or group.

    CLI Example:

    .. code-block:: bash

        salt '*' pushover.post_message 'Build is done'
        salt '*' pushover.post_message user='uQiRzpo4DXghDmr9QzzfQu27cmVRsG' title='Hi' message='Build is done'
        salt '*' pushover.post_message user='uQiRzpo4DXghDmr9QzzfQu27cmVRsG' title='Hi' message='Build is done' priority='2' expire='720' retry='5'

    message
        Message text to send. Required.

    title
        Message title. Defaults to ``Message from Salt``.

    user
        User or group of users to send the message to. Must be a user/group ID (key),
        not a name or an email address.
        Required if not specified in the configuration.

    device
        Name of the device to send the message to. Defaults to all devices of the user.

    priority
        Message priority (integers between ``-2`` and ``2``).
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
        `Notification sound <https://pushover.net/api#sounds>`_ to play. Defaults to user default.

    token
        Pushover API token.
        Required if not specified in the configuration.
    """
    token, user = _resolve_token(token), _resolve_user(user)
    return pushover.post_message(
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


def validate_user(user=None, device=None, token=None):
    """
    .. versionadded:: 2.0.0

    Validate the resolved user and device combination.

    CLI Example:

    .. code-block:: bash

        salt '*' pushover.validate_user
        salt '*' pushover.validate_user device=foobar
        salt '*' pushover.post_message user='uQiRzpo4DXghDmr9QzzfQu27cmVRsG' device=foobar

    user
        User to validate. Defaults to configured user.

    device
        Device of ``user`` to validate. If unspecified, ensures ``user`` has any registered device.

    token
        Pushover API token.
        Required if not specified in the configuration.
    """
    token, user = _resolve_token(token), _resolve_user(user)
    return pushover.validate_user(user, token, device, context=__context__, opts=__opts__)


def validate_sound(sound, token=None):
    """
    .. versionadded:: 2.0.0

    Validate a sound exists. Can only check official sounds.

    CLI Example:

    .. code-block:: bash

        salt '*' pushover.validate_sound bike

    sound
        Sound to validate.

    token
        Pushover API token.
        Required if not specified in the configuration.
    """
    token = _resolve_token(token)
    return pushover.validate_sound(sound, token, context=__context__, opts=__opts__)
