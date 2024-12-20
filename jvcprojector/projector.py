"""Module for interacting with a JVC Projector."""

from __future__ import annotations
from typing import Mapping
from . import command
from .command import JvcCommand, JvcCommandHelpers
from .connection import resolve
from .device import JvcDevice
from .error import JvcProjectorConnectError, JvcProjectorError
from . import const
import logging

DEFAULT_PORT = 20554
DEFAULT_TIMEOUT = 15.0

_LOGGER = logging.getLogger(__name__)


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
        """Initialize class."""
        self._host = host
        self._port = port
        self._timeout = timeout
        self._password = password

        self._device: JvcDevice | None = None
        self._ip: str = ""
        self._model: str = ""
        self._mac: str = ""
        self._version: str = ""
        self._dict: dict[str, str] = {}

    @property
    def ip(self) -> str:
        """Returns ip."""
        if not self._ip:
            raise JvcProjectorError("ip not initialized")
        return self._ip

    @property
    def host(self) -> str:
        """Returns host."""
        return self._host

    @property
    def port(self) -> int:
        """Returns port."""
        return self._port

    @property
    def model(self) -> str:
        """Returns model name."""
        if not self._mac:
            raise JvcProjectorError("model not initialized")
        return self.process_model_code(self._model)

    @property
    def mac(self) -> str:
        """Returns mac address."""
        if not self._mac:
            raise JvcProjectorError("mac address not initialized")
        return self._mac

    @property
    def version(self) -> str:
        """Get device software version."""
        if not self._version:
            raise JvcProjectorError("version address not initialized")
        return self.process_version(self._version)

    async def is_on(self) -> bool:
        """Return if device is fully on and ready."""
        return await self.get_power() == const.ON

    async def connect(self, get_info: bool = False) -> None:
        """Connect to device."""
        if self._device:
            return

        if not self._ip:
            self._ip = await resolve(self._host)

        self._device = JvcDevice(self._ip, self._port, self._timeout, self._password)

        if not await self.test():
            raise JvcProjectorConnectError("Failed to verify connection")

        if get_info:
            await self.get_info()

    async def disconnect(self) -> None:
        """Disconnect from device."""
        if self._device:
            await self._device.disconnect()
            self._device = None

    async def get_info(self) -> dict[str, str]:
        """Get device info.

        Returns:
            dict[str, str]: Dictionary containing model and MAC address

        Raises:
            JvcProjectorError: If device is not connected or MAC address is unavailable

        """
        if not self._device:
            raise JvcProjectorError("Must call connect before getting info")

        # Create base commands that work regardless of power state
        model = JvcCommand(const.CMD_MODEL, True)
        mac = JvcCommand(const.CMD_LAN_SETUP_MAC_ADDRESS, True)
        commands = [model, mac]
        _LOGGER.debug("Getting info with commands %s", commands)

        # Only add version command if projector is on
        is_on = await self.is_on()
        if is_on:
            _LOGGER.debug("Projector is on, adding version command")
            version = JvcCommand(const.CMD_VERSION, True)
            commands.append(version)

        # Send commands
        await self._send(commands)
        _LOGGER.debug("Got responses %s", [cmd.response for cmd in commands])

        # Validate
        if mac.response is None:
            raise JvcProjectorError("MAC address not available")

        # responses
        self._model = model.response or "(unknown)"
        self._mac = mac.response  # None checked above
        self._version = version.response if is_on and version.response else "(unknown)"

        return {const.KEY_MODEL: self._model, const.KEY_MAC: self._mac}

    async def get_state(self) -> Mapping[str, str | None]:
        """Get device state."""
        if not self._device:
            raise JvcProjectorError("Must call connect before getting state")

        # Add static values
        self._dict[const.KEY_MODEL] = self.process_model_code(self._model)
        self._dict[const.KEY_VERSION] = self.process_version(self._version)
        self._dict[const.KEY_MAC] = self.process_mac(self._mac)

        async def send_and_update(commands: dict[str, str]) -> None:
            """Send commands and update the dictionary."""
            # send commands with is_ref set to true
            cmd_vals = [JvcCommand(cmd, True) for cmd in commands.values()]
            res = await self._send(cmd_vals)
            # discard the command values and zip the keys with the responses
            for (key, _), value in zip(commands.items(), res):
                # Only store non-None values
                if value is not None:
                    self._dict[key] = value

        # Always get power state
        await send_and_update({const.KEY_POWER: const.CMD_POWER})

        # If power is on, get additional states
        if self._dict.get(const.KEY_POWER) == const.ON:
            await send_and_update(
                {
                    const.KEY_INPUT: const.CMD_INPUT,
                    const.KEY_SOURCE: const.CMD_SOURCE,
                    const.KEY_PICTURE_MODE: const.CMD_PICTURE_MODE,
                    const.KEY_LOW_LATENCY: const.CMD_PICTURE_MODE_LOW_LATENCY,
                    const.KEY_LASER_POWER: const.CMD_PICTURE_MODE_LASER_POWER,
                    const.KEY_LASER_TIME: const.CMD_FUNCTION_LASER_TIME,
                    const.KEY_ANAMORPHIC: const.CMD_INSTALLATION_ANAMORPHIC,
                    const.KEY_INSTALLATION_MODE: const.CMD_INSTALLATION_MODE,
                }
            )

            # Check if there's a signal before getting signal-dependent states
            if self._dict.get(const.KEY_SOURCE) == const.SIGNAL:
                await send_and_update(
                    {
                        const.KEY_HDR: const.CMD_FUNCTION_HDR,
                        const.KEY_HDMI_INPUT_LEVEL: const.CMD_INPUT_SIGNAL_HDMI_INPUT_LEVEL,
                        const.KEY_HDMI_COLOR_SPACE: const.CMD_INPUT_SIGNAL_HDMI_COLOR_SPACE,
                        const.KEY_COLOR_PROFILE: const.CMD_PICTURE_MODE_COLOR_PROFILE,
                        const.KEY_GRAPHICS_MODE: const.CMD_PICTURE_MODE_GRAPHICS_MODE,
                        const.KEY_COLOR_SPACE: const.CMD_FUNCTION_COLOR_SPACE,
                    }
                )

            # NX9 and NZ model specific commands
            if (
                "NZ" in self._dict[const.KEY_MODEL]
                or "NX9" in self._dict[const.KEY_MODEL]
            ):
                await send_and_update(
                    {
                        const.KEY_ESHIFT: const.CMD_PICTURE_MODE_8K_ESHIFT,
                        const.KEY_CLEAR_MOTION_DRIVE: const.CMD_PICTURE_MODE_CLEAR_MOTION_DRIVE,
                        const.KEY_MOTION_ENHANCE: const.CMD_PICTURE_MODE_MOTION_ENHANCE,
                        const.KEY_LASER_VALUE: const.CMD_PICTURE_MODE_LASER_VALUE,
                        const.KEY_LASER_DIMMING: const.CMD_LASER_DIMMING,
                    }
                )

            # HDR-specific commands
            if (
                self._dict.get("hdr")
                not in [const.HDR_CONTENT_NONE, const.HDR_CONTENT_SDR]
            ) and self._dict.get(const.KEY_SOURCE) == const.SIGNAL:
                await send_and_update(
                    {
                        const.KEY_HDR_PROCESSING: const.CMD_PICTURE_MODE_HDR_PROCESSING,
                        const.KEY_HDR_CONTENT_TYPE: const.CMD_PICTURE_MODE_HDR_CONTENT_TYPE,
                    }
                )

        return self._dict

    def process_mac(self, mac: str) -> str:
        """Process mac address."""
        # skip every 2 characters and join with :
        return ":".join(mac[i : i + 2] for i in range(0, len(mac), 2))

    def process_model_code(self, model: str) -> str:
        """Process model code."""
        return const.MODEL_MAP.get(model[-4:], f"{model}: Unknown")

    def process_version(self, version: str) -> str:
        """Process version string."""

        if version == "(unknown)":
            return version

        version = version.removesuffix("PJ")
        version = version.zfill(4)

        # Extract major, minor, and patch versions
        major = str(
            int(version[0:2])
        )  # Remove leading zero and convert to int then back to str
        minor = str(int(version[2]))
        patch = str(int(version[3]))

        return f"{major}.{minor}.{patch}"

    async def get_version(self) -> str | None:
        """Get device software version."""
        return await self.ref(const.CMD_VERSION)

    async def get_power(self) -> str | None:
        """Get power state."""
        return await self.ref(const.CMD_POWER)

    async def get_input(self) -> str | None:
        """Get current input."""
        return await self.ref(const.CMD_INPUT)

    async def get_signal(self) -> str | None:
        """Get if has signal."""
        return await self.ref(const.CMD_SOURCE)

    async def test(self) -> bool:
        """Run test command."""
        cmd = JvcCommand(f"{command.TEST}")
        await self._send([cmd])
        return cmd.ack

    async def power_on(self) -> None:
        """Run power on command."""
        await self.op(f"{const.CMD_POWER}1")

    async def power_off(self) -> None:
        """Run power off command."""
        await self.op(f"{const.CMD_POWER}0")

    async def remote(self, code: str) -> None:
        """Run remote code command."""
        await self.op(f"{const.CMD_REMOTE}{code}")

    async def op(self, code: str) -> None:
        """Send operation code."""
        await self._send([JvcCommand(code, False)])

    async def ref(self, code: str) -> str | None:
        """Send reference code."""
        return (await self._send([JvcCommand(code, True)]))[0]

    async def _send(self, cmds: list[JvcCommand]) -> list[str | None]:
        """Send command to device."""
        if self._device is None:
            raise JvcProjectorError("Must call connect before sending commands")

        await self._device.send(cmds)

        return [cmd.response for cmd in cmds]

    @staticmethod
    def _invert_dict(d: dict[str, str]) -> dict[str, str]:
        return {v: k for k, v in d.items()}

    async def send_command(self, cmd: str, val: str) -> None:
        """Send a command to the projector using well-known names like "power". Intended to be human readable commands."""
        # normalize the command and value
        cmd = cmd.lower()
        val = val.lower()

        # get all valid commands and the PJ codes
        valid_command_map = JvcCommandHelpers.get_available_commands()

        # ensure the command is valid
        if cmd not in valid_command_map:
            raise ValueError(f"Unknown command: {cmd}")

        # get the PJ code and values
        cmd_values = valid_command_map[cmd]["values"]
        raw_cmd = valid_command_map[cmd]["command"]

        # ensure the value is valid
        try:
            if val not in cmd_values:
                raise ValueError(f"Invalid value for {cmd}: {val}")
        except KeyError as exc:
            raise ValueError(f"Unknown command: {cmd}") from exc

        # get the PJ values like high = 1
        command_info = JvcCommand.command_map[raw_cmd]

        # transform human values to PJ values
        if command_info["values"] == "callable":
            # For callable formatters, we'll just pass the value as is
            value = val
        elif "inverse" in command_info:
            if val not in command_info["inverse"]:
                raise ValueError(f"Invalid value for {cmd}: {val}")
            value = command_info["inverse"][val]
        else:
            raise ValueError(f"Unsupported command type for {cmd}")

        await self.op(f"{raw_cmd}{value}")
