"""A python library for controlling a JVC Projector over a network connection."""

# ruff: noqa: F401

from .error import (
    JvcProjectorAuthError,
    JvcProjectorCommandError,
    JvcProjectorConnectError,
    JvcProjectorError,
)
from .projector import JvcProjector

__version__ = "1.1.2"
