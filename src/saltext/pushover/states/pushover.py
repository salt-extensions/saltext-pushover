"""
Send notifications via `Pushover <https://pushover.net>`_ during state runs.

.. important::
    See :ref:`Configuration <pushover-setup>` for a description of
    available configuration parameters.

Example
-------
.. code-block:: yaml

    pushover-message:
      pushover.post_message:
        - user: uQiRzpo4DXghDmr9QzzfQu27cmVRsG
        - token: azGDORePK8gMaC0QOYAMyEEuzJnyUi
        - title: Message from Salt
        - device: phone
        - priority: -1
        - expire: 3600
        - retry: 5
        - message: 'This state was executed successfully.'
"""

__virtualname__ = "pushover"


from salt.exceptions import CommandExecutionError


def __virtual__():
    if "pushover.post_message" in __salt__:
        return __virtualname__
    return (False, "pushover module could not be loaded")


def post_message(
    name,
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
    Send a message to a Pushover user or group.

    .. code-block:: yaml

        pushover-message:
          pushover.post_message:
            - user: uQiRzpo4DXghDmr9QzzfQu27cmVRsG
            - token: azGDORePK8gMaC0QOYAMyEEuzJnyUi
            - title: Message from Salt
            - device: phone
            - priority: -1
            - expire: 3600
            - retry: 5
            - message: 'This state was executed successfully.'

    name
        The name of the state. Irrelevant.

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
        Pushover API key.
        Required if not specified in the configuration.
    """
    ret = {"name": name, "changes": {}, "result": False, "comment": ""}

    if __opts__["test"]:
        ret["comment"] = f"The following message is to be sent to Pushover: {message}"
        ret["result"] = None
        return ret

    try:
        __salt__["pushover.post_message"](
            message,
            title=title,
            user=user,
            device=device,
            priority=priority,
            expire=expire,
            retry=retry,
            sound=sound,
            token=token,
        )
    except CommandExecutionError as err:
        ret["result"] = False
        ret["comment"] = f"Failed to send message '{name}'! Error: " + str(err)
    else:
        ret["result"] = True
        ret["comment"] = f"Sent message: {name}"

    return ret
