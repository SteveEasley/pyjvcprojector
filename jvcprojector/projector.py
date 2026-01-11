"""Module for interacting with a JVC Projector."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from . import command
from .command.base import LIMP_MODE, Command
from .command.command import SPECIFICATIONS
from .connection import resolve
from .device import Device
from .error import JvcProjectorError

if TYPE_CHECKING:
    from .command.command import Spec


_LOGGER = logging.getLogger(__name__)


DEFAULT_PORT: Final = 20554
DEFAULT_TIMEOUT: Final = 2.0


class JvcProjector:
    """Class for interacting with a JVC Projector."""

    def __init__(
        self,
        host: str,
        *,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
        password: str | None = None,
    ) -> None:
        """Initialize instance of class."""
        self._host = host
        self._port = port
        self._timeout = timeout
        self._password = password

        self._device: Device | None = None
        self._ip: str | None = None
        self._spec: Spec = LIMP_MODE
        self._model: str | None = None

    @property
    def host(self) -> str:
        """Returns host name."""
        return self._host

    @property
    def port(self) -> int:
        """Returns ip port."""
        return self._port

    @property
    def ip(self) -> str:
        """Returns ip address."""
        if self._ip is None:
            raise JvcProjectorError("IP not initialized")
        return self._ip

    @property
    def model(self) -> str:
        """Returns model name."""
        if self._model is None:
            raise JvcProjectorError("Model not initialized")
        return self._model

    @property
    def spec(self) -> str:
        """Returns specification."""
        if not self._device:
            raise JvcProjectorError("Not connected")

        spec = self._spec.name

        if not self._spec.limp_mode and self._spec.model.name != self._model:
            spec += f"-{self._spec.model.name}"

        return spec

    async def connect(self, *, model: str | None = None) -> None:
        """Initialize communication with the projector."""
        if self._device:
            return

        if not self._ip:
            self._ip = await resolve(self._host)

        self._device = Device(self._ip, self._port, self._timeout, self._password)

        self._model = model if model else await self.get(command.ModelName)

        for spec in SPECIFICATIONS:
            if spec.matches_model(self._model):
                self._spec = spec
                break

        if self._spec.limp_mode:
            for spec in SPECIFICATIONS:
                if spec.matches_prefix(self._model):
                    msg = "Unknown model %s detected; defaulting %s (%s)"
                    _LOGGER.warning(msg, self._model, spec.model.name, spec.name)
                    self._spec = spec
                    break

        if self._spec.limp_mode:
            _LOGGER.warning(
                "Unknown model %s detected; entering limp mode", self._model
            )

    async def disconnect(self) -> None:
        """Disconnect from the projector."""
        if self._device:
            await self._device.disconnect()
            self._device = None

        self._ip = None
        self._model = None
        self._spec = LIMP_MODE

        Command.unload()

    async def get(self, name: str | type[Command]) -> str:
        """Get a projector parameter value (reference command)."""
        return str(await self._send(name))

    async def set(self, name: str | type[Command], value: Any = None) -> None:
        """Set a projector parameter value (operation command)."""
        await self._send(name, value)

    async def remote(self, value: Any = None) -> None:
        """Send a projector remote command."""
        await self.set(command.Remote, value)

    async def _send(self, name: str | type[Command], value: Any = None) -> str | None:
        """Send a command to the projector."""
        if not self._device:
            raise JvcProjectorError("Not connected")

        cls = Command.lookup(name) if isinstance(name, str) else name

        if cls is None:
            raise JvcProjectorError(f"Command {name} not implemented")

        cmd = cls(self._spec)

        if not cmd.supports(self._spec):
            raise JvcProjectorError(
                f"Command {cmd.name} ({cmd.code}) not supported by this model"
            )

        if value is None:
            if not cmd.reference:
                raise JvcProjectorError(
                    f"Invalid attempt to read from non-reference command {cmd.name} ({cmd.code})"
                )
        else:
            if not cmd.operation:
                raise JvcProjectorError(
                    f"Invalid attempt to write to non-operation command {cmd.name} ({cmd.code})"
                )
            cmd.op_value = str(value)

        await self._device.send(cmd)

        return cmd.ref_value

    def supports(self, name: str | type[Command]) -> bool:
        """Check if a command is supported by the projector."""
        if not self._device:
            raise JvcProjectorError("Not connected")

        cls = Command.lookup(name) if isinstance(name, str) else name

        if cls is None:
            raise JvcProjectorError(f"Command {name} not implemented")

        return cls.supports(self._spec)

    def describe(self, name: str | type[Command]) -> dict[str, Any]:
        """Return a command description."""
        if not self._device:
            raise JvcProjectorError("Not connected")

        cls = Command.lookup(name) if isinstance(name, str) else name

        if cls is None:
            raise JvcProjectorError(f"Command {name} not implemented")

        if cls.supports(self._spec):
            return cls.describe()

        raise JvcProjectorError(
            f"Command {cls.name} ({cls.code}) not supported by this model"
        )

    def capabilities(self) -> dict[str, Any]:
        """Return the supported command list."""
        if not self._device:
            raise JvcProjectorError("Not connected")

        commands: dict[str, Any] = {}

        for cls in Command.registry["name"].values():
            if cls.supports(self._spec):
                commands[cls.name] = cls.describe()

        return commands
