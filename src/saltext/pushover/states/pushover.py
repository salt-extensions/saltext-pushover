"""
Send notifications via `Pushover <https://www.pushover.net>`_ during state runs.

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


def __virtual__():
    if "pushover.post_message" in __salt__:
        return __virtualname__
    return (False, "pushover module could not be loaded")


def post_message(
    name,
    user=None,
    device=None,
    message=None,
    title=None,
    priority=0,
    expire=None,
    retry=None,
    sound=None,  # pylint: disable=unused-argument
    api_version=1,  # pylint: disable=unused-argument
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

    name
        The name of the state. Irrelevant.

    user
        The user or group of users to send the message to. Must be a user/group ID (key),
        not a name or an email address.
        Required if not specified in the configuration.

    message
        The message to send to the Pushover user or group. Required.

    title
        The message title to use.

    device
        The name of the device to send the message to.

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

    token
        The authentication token to use for the Pushover API.
        Required if not specified in the configuration.
    """
    ret = {"name": name, "changes": {}, "result": False, "comment": ""}

    if __opts__["test"]:
        ret["comment"] = f"The following message is to be sent to Pushover: {message}"
        ret["result"] = None
        return ret

    if not user:
        user = __salt__["config.get"]("pushover.user") or __salt__["config.get"]("pushover:user")
        if not user:
            ret["comment"] = f"Pushover user is missing: {user}"
            return ret

    if not message:
        ret["comment"] = f"Pushover message is missing: {message}"
        return ret

    result = __salt__["pushover.post_message"](
        user=user,
        message=message,
        title=title,
        device=device,
        priority=priority,
        expire=expire,
        retry=retry,
        token=token,
    )

    if result:
        ret["result"] = True
        ret["comment"] = f"Sent message: {name}"
    else:
        ret["comment"] = f"Failed to send message: {name}"

    return ret
