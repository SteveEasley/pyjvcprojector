"""A python library for controlling a JVC Projector over a network connection."""

# ruff: noqa: F401

from .command.base import Command
from .error import (
    JvcProjectorAuthError,
    JvcProjectorCommandError,
    JvcProjectorError,
    JvcProjectorTimeoutError,
)
from .projector import JvcProjector

__all__ = [
    "JvcProjector",
    "JvcProjectorError",
    "JvcProjectorTimeoutError",
    "JvcProjectorAuthError",
    "JvcProjectorCommandError",
    "Command",
]

__version__ = "2.0.6"
