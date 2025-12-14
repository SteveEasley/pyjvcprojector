"""Module for representing a JVC Projector command."""

# pylint: disable=W0223

from __future__ import annotations

import logging
import re
from typing import Any

from ..error import JvcProjectorError

_LOGGER = logging.getLogger(__name__)


_CATEGORY_MATCHER = {
    "PW|IP|SC|RC|IFLT|MD|LSMA|IFSV": "System",
    "IF|IS": "Signal",
    "PM": "Picture",
    "IN": "Installation",
    "FU": "Function",
}

CATEGORIES = list(_CATEGORY_MATCHER.values())


class Command:
    """Class for representing a JVC Projector command."""

    name: str
    code: str
    category: str = "Other"
    reference: bool = False
    operation: bool = False
    limp: bool = False
    operation_timeout: float | None = None
    parameter: Parameter | dict[Spec | tuple[Spec, ...], Parameter]
    _parameter: Parameter | None = None

    registry: dict[str, dict[str, type[Command]]] = {
        "name": {},
        "code": {},
    }

    def __init_subclass__(cls, **kwargs):
        """Initialize subclass."""
        super().__init_subclass__(**kwargs)

        cls.name = cls.__name__
        cls.registry["name"][cls.name] = cls
        cls.registry["code"][cls.code] = cls

        for match, name in _CATEGORY_MATCHER.items():
            pattern = re.compile(f"^({match})")
            if re.search(pattern, cls.code):
                cls.category = name
                break

    @classmethod
    def lookup(cls, name: str) -> type[Command] | None:
        """Get a command class by name or code."""
        assert cls is Command

        if name in Command.registry["name"]:
            return Command.registry["name"][name]

        if name in Command.registry["code"]:
            return Command.registry["code"][name]

        return None

    @classmethod
    def supports(cls, spec: Spec | None) -> bool:
        """Return if the current model supports the command."""
        if cls._parameter is None:
            cls._resolve(spec)
        assert cls._parameter
        return cls._parameter.supported()

    @classmethod
    def describe(cls) -> dict[str, Any]:
        """Describe command."""
        assert cls._parameter
        return {
            "name": cls.name,
            "code": cls.code,
            "reference": cls.reference,
            "operation": cls.operation,
            "category": cls.category,
            "parameter": cls._parameter.describe(),
        }

    @classmethod
    def _resolve(cls, spec: Spec | None = None) -> None:
        """Resolve the supported parameter for command."""

        # Commands not supported by the current model default to an empty sentinel parameter.
        parameter = Parameter()

        if isinstance(cls.parameter, Parameter):
            # e.g. parameter = MapParameter()
            if spec or cls.limp:
                parameter = cls.parameter

        elif isinstance(cls.parameter, dict) and spec:
            for key, param in cls.parameter.items():
                if isinstance(key, Spec):
                    # e.g. parameter = {CS20241: MapParameter()}
                    if key == spec:
                        parameter = param
                        break
                elif isinstance(key, tuple):
                    # e.g. parameter = {(CS20241, CS20221): MapParameter()}
                    if spec in key:
                        parameter = param
                        break

        parameter.resolve(spec)

        cls._parameter = parameter

    @classmethod
    def unload(cls) -> None:
        """Clear all resolved parameters for each registered command."""
        assert cls is Command
        for cmd in cls.registry["name"].values():
            # pylint: disable=protected-access
            if cmd._parameter:
                cmd._parameter.unload()
                cmd._parameter = None

    def __init__(self, spec: Spec | None = None):
        """Initialize instance of class."""
        self.ack: bool = False
        self.is_ref: bool = True
        self.is_op: bool = False

        self._spec: Spec | None = spec
        self._op_value: str | None = None
        self._ref_value: str | None = None

        if not self.reference and not self.operation:
            raise RuntimeError(
                f"Command {self.name} ({self.code}) is neither reference nor operation"
            )

        if self._parameter is None:
            self._resolve(spec)

    @property
    def ref_value(self) -> str | None:
        """Get response value."""
        return self._ref_value

    @ref_value.setter
    def ref_value(self, value: str) -> None:
        """Set response value."""
        assert self._parameter

        if self._parameter.size and len(value) != self._parameter.size:
            msg = "Command %s (%s) returned unexpected response size %s; expected %s"
            _LOGGER.warning(msg, self.name, self.code, len(value), self._parameter.size)

        self._ref_value = self._parameter.ref(self, value)

    @property
    def op_value(self) -> str:
        """Get operation command parameter value."""
        return str(self._op_value)

    @op_value.setter
    def op_value(self, value: str) -> None:
        """Set operation command parameter value."""
        assert self._parameter

        self._op_value = self._parameter.op(self, value)

        self.is_op = True
        self.is_ref = False


class Parameter:
    """Base class for a command parameter."""

    size: int = 0

    def ref(self, cmd: Command, value: str) -> str:
        """Convert a native projector value to a human readable value."""
        raise NotImplementedError

    def op(self, cmd: Command, value: str) -> str:
        """Convert a human readable value to a native projector value."""
        raise NotImplementedError

    def supported(self) -> bool:
        """Return if the supported model supports this parameter."""
        return type(self) is not Parameter  # pylint: disable=unidiomatic-typecheck

    # pylint: disable=unused-argument
    def resolve(self, spec: Spec | None) -> None:
        """Resolve the matching parameter for the given model."""
        return None

    def describe(self) -> str | dict[str, dict[str, str]]:
        """Return a descriptive representation of the parameter."""
        return ""

    def unload(self) -> None:
        """Clear resolved parameter."""
        return None


class ModelParameter(Parameter):
    """Parameter for Model command."""

    def ref(self, cmd: Command, value: str) -> str:
        return re.sub(r"ILAFPJ\W+", "", value)

    def describe(self) -> str:
        return "Model name (e.g. B2A2)"


class MacAddressParameter(Parameter):
    """Parameter for MacAddress command."""

    def ref(self, cmd: Command, value: str) -> str:
        return re.sub(r"-+", "-", value.replace(" ", "-"))

    def describe(self) -> str:
        return "Mac address (e.g. E0DADC0A1562)"


class VersionParameter(Parameter):
    """Parameter for SoftwareVersion command."""

    def ref(self, cmd: Command, value: str) -> str:
        return value

    def describe(self) -> str:
        return "Software version"


class LaserPowerParameter(Parameter):
    """Parameter for the LaserPower command."""

    def ref(self, cmd: Command, value: str) -> str:
        return str(round((int(value, 16) - 109) / 110, 2))

    def op(self, cmd: Command, value: str) -> str:
        val = float(value)
        if val < 0.0 or val > 1.0:
            raise JvcProjectorError(
                f"Command {cmd.name} ({cmd.code}) returned an out of range value '{value}'"
            )
        return f"{round(110 * val + 109):04X}"

    def describe(self) -> str:
        return "Laser power level % (0.0 - 1.0)"


class LightTimeParameter(Parameter):
    """Parameter for LightSourceTime command."""

    def ref(self, cmd: Command, value: str) -> str:
        return str(int(value, 16))

    def describe(self) -> str:
        return "Light source time in hours"


class MapParameter(Parameter):
    """Parameter for map commands."""

    def __init__(
        self,
        size: int = 0,
        read: dict[str, str | tuple[str | Model, ...]] | None = None,
        write: dict[str, str | tuple[str | Model, ...]] | None = None,
        readwrite: dict[str, str | tuple[str | Model, ...]] | None = None,
    ):
        self._read: dict[str, str | tuple[str | Model, ...]] = {}
        self._write: dict[str, str | tuple[str | Model, ...]] = {}
        self._resolved_read: dict[str, str] = {}
        self._resolved_write: dict[str, str] = {}

        self.size = size

        if readwrite and (read or write):
            raise RuntimeError("Cannot specify both readwrite and read/write")

        if read:
            self._read = read
        elif readwrite:
            self._read = readwrite

        if write:
            self._write = write
        elif readwrite:
            self._write = readwrite

    def resolve(self, spec: Spec | None):
        for k, v in self._read.items():
            if isinstance(v, str):
                self._resolved_read[k] = v
            elif isinstance(v, tuple) and spec and spec.model in v[1:]:
                self._resolved_read[k] = str(v[0])

        for k, v in self._write.items():
            if isinstance(v, str):
                self._resolved_write[k] = v
            elif isinstance(v, tuple) and spec and spec.model in v[1:]:
                self._resolved_write[k] = str(v[0])

    def ref(self, cmd: Command, value: str) -> str:
        if value not in self._resolved_read:
            raise JvcProjectorError(
                f"Command {cmd.name} ({cmd.code}) received unmapped value '{value}' from projector"
            )

        return self._resolved_read[value]

    def op(self, cmd: Command, value: str) -> str:
        for k, v in self._resolved_write.items():
            if v == value:
                return k

        raise JvcProjectorError(
            f"Command {cmd.name} ({cmd.code}) received unmapped value '{value}' from user"
        )

    def supported(self) -> bool:
        # A command is supported if it has at least one mapped value for the current model."""
        return bool(self._resolved_read or self._resolved_write)

    def describe(self) -> dict[str, dict[str, str]]:
        return {"read": self._resolved_read, "write": self._resolved_write}

    def unload(self) -> None:
        self._resolved_read = {}
        self._resolved_write = {}


class Model:
    """Represents a JVC projector model."""

    def __init__(self, *args: str) -> None:
        self.name: str = args[0] if len(args) > 0 else ""
        self.names: list[str] = list(args)


class Spec:
    """Represents a JVC command specification."""

    def __init__(self, name: str, *args: Model) -> None:
        self.name = name
        self.models: list[Model] = list(args)
        self.model: Model = Model()

    def matches_model(self, name: str) -> bool:
        """Look up the model by name."""
        for model in self.models:
            if name in model.names:
                self.model = model
                return True
        return False

    def matches_prefix(self, name: str) -> bool:
        """Look up the model by prefix."""
        for model in self.models:
            for _name in model.names:
                if _name[0:3] == name[0:3]:
                    self.model = model
                    return True
        return False
