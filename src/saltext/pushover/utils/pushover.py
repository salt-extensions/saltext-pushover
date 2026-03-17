"""
Utility functions for interacting with the Pushover API.
"""

import logging

import salt.utils.http
import salt.utils.json
from salt.exceptions import CommandExecutionError

log = logging.getLogger(__name__)

API_URL = "https://api.pushover.net"


class PushoverAPIError(CommandExecutionError):
    """
    Generic exception to render Pushover API errors.
    """

    status: int
    res: dict
    raw: str | None

    def __init__(self, status: int, res: dict | None = None, raw: str | None = None):
        res = res or {}
        self.status = status
        self.res = res
        self.raw = raw

        msg = f"Pushover API Error (HTTP {status}): "
        if "errors" in res:
            msg += "; ".join(res["errors"])
        elif self.raw:
            msg += self.raw
        else:
            msg += "(no further description)"
        super().__init__(msg)


def query(
    endpoint,
    method="POST",
    *,
    data=None,
    query_params=None,
    token=None,
    api_version="1",
    header_dict=None,
    opts=None,
):
    """
    .. versionchanged:: 2.0.0
        * Parameters have been reordered.
        * Uses JSON request bodies by default.
        * Errors result in exceptions.
        * Returns the decoded response data only.

    Query the Pushover API.

    endpoint
        API endpoint to query (without ``.json`` suffix), e.g. ``messages``.

        .. versionchanged:: 2.0.0
            Previously, the first parameter was an internally defined identifier.
            This accepts all API paths.

    method
        HTTP method. Defaults to ``POST``.

    data
        Request body data.

        .. versionchanged:: 2.0.0
            Automatically dumped to JSON, unless the ``Content-Type`` header
            is set explicitly in ``header_dict``.

    query_params
        URI query parameter dictionary.

    token
        Pushover API token.
        Optional if already specified in ``data`` or ``query_params``,
        depending on the method. Overrides them.

    api_version
        API version. Used for building query URI. Defaults to ``1``.

    header_dict
        HTTP request headers to add.

    opts
        Pass through ``__opts__`` to respect Salt HTTP configuration.
    """
    query_params = query_params or {}

    decode = method != "DELETE"
    if token:
        if method == "GET":
            query_params["token"] = token
        else:
            data = data or {}
            data["token"] = token

    header_dict = header_dict or {}
    if method != "GET" and "Content-Type" not in header_dict:
        header_dict["Content-Type"] = "application/json"
        if data:
            data = salt.utils.json.dumps(data)

    result = salt.utils.http.query(
        f"{API_URL}/{api_version}/{endpoint}.json",
        method,
        params=query_params,
        data=data,
        header_dict=header_dict,
        decode=decode,
        decode_type="json",
        text=True,
        status=True,
        opts=opts,
    )
    if decode and "dict" not in result:
        # Salt does not decode the body if the status indicates an error
        try:
            result["dict"] = salt.utils.json.loads(result["body"])
        except ValueError:
            result["dict"] = {}

    if result["status"] >= 400:
        raise PushoverAPIError(result["status"], result.get("dict"), result.get("text"))
    if decode:
        return result["dict"]
    return result["text"]


def validate_sound(sound, token, *, context=None, opts=None):
    """
    Validate that a specified sound value exists.

    sound
        Sound to verify

    token
        Pushover API token

    context
        Pass through ``__context__`` to allow caching.

        .. versionadded:: 2.0.0

    opts
        Pass through ``__opts__`` to respect Salt HTTP configuration.

        .. versionadded:: 2.0.0
    """
    context = context or {}
    if "pushover_sounds" in context:
        sounds = context["pushover_sounds"]
    else:
        sounds = query("sounds", "GET", token=token, opts=opts)["sounds"]
        context["pushover_sounds"] = sounds
    return sound in sounds


def validate_user(user, token, device=None, *, context=None, opts=None):
    """
    Validate that a user/group ID (key) exists and has at least one active device.
    If ``device`` is not falsy, additionally validate that the device exists in the account.

    user
        User or group name to validate. Required.

    token
        Pushover API token. Required.

    device
        Optional device for ``user`` to validate.
        If unspecified, checks whether any device is available.

    context
        Pass through ``__context__`` to allow caching.

        .. versionadded:: 2.0.0

    opts
        Pass through ``__opts__`` to respect Salt HTTP configuration.

        .. versionadded:: 2.0.0
    """
    ckey = (user, token, device)
    context = context or {}
    if ckey in context:
        return True

    payload = {"user": user}
    if device:
        payload["device"] = device

    try:
        query(
            endpoint="users/validate",
            data=payload,
            token=token,
            opts=opts,
        )
    except PushoverAPIError as err:
        if "invalid" in err.res.get("user", ""):
            raise CommandExecutionError(f"Pushover: Invalid user '{user}'") from err
        if "invalid" in err.res.get("device", ""):
            raise CommandExecutionError(
                f"Pushover: Invalid device '{device}' for user '{user}'"
            ) from err
        raise

    # Only cache successful lookups to avoid false negatives
    context[ckey] = True
    return True
