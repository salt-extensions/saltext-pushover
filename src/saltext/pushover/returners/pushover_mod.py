"""
Salt returner module
"""
import logging

log = logging.getLogger(__name__)

__virtualname__ = "pushover"


def __virtual__():
    # To force a module not to load return something like:
    #   return (False, "The pushover returner module is not implemented yet")
    return __virtualname__