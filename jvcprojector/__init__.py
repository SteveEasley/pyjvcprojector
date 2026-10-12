"""A python library for controlling a JVC Projector over a network connection."""

from .command.base import Command
from .error import (
    JvcProjectorAuthError,
    JvcProjectorCommandError,
    JvcProjectorError,
    JvcProjectorTimeoutError,
)
from .projector import JvcProjector

__all__ = [
    "Command",
    "JvcProjector",
    "JvcProjectorAuthError",
    "JvcProjectorCommandError",
    "JvcProjectorError",
    "JvcProjectorTimeoutError",
]

__version__ = "2.1.0"
