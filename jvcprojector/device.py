"""Module for representing a JVC Projector device."""

from __future__ import annotations

import asyncio
from hashlib import sha256
import logging
import struct
from time import time
from typing import TYPE_CHECKING, Final

from .connection import Connection
from .error import (
    JvcProjectorAuthError,
    JvcProjectorError,
    JvcProjectorReadWriteTimeoutError,
    JvcProjectorTimeoutError,
)

if TYPE_CHECKING:
    from .command.base import Command


PJOK: Final = b"PJ_OK"
PJNG: Final = b"PJ_NG"
PJREQ: Final = b"PJREQ"
PJACK: Final = b"PJACK"
PJNAK: Final = b"PJNAK"

UNIT_ID: Final = b"\x89\x01"
HEAD_OP: Final = b"!" + UNIT_ID
HEAD_REF: Final = b"?" + UNIT_ID
HEAD_RES: Final = b"@" + UNIT_ID
HEAD_ACK: Final = b"\x06" + UNIT_ID
HEAD_LEN: Final = 1 + len(UNIT_ID)
END: Final = b"\n"

AUTH_SALT: Final = "JVCKWPJ"

KEEPALIVE_TTL: Final = 0.5

_LOGGER = logging.getLogger(__name__)


class Device:
    """Class for representing a JVC Projector device."""

    def __init__(
        self, ip: str, port: int, timeout: float, password: str | None
    ) -> None:
        """Initialize instance of class."""
        self._conn = Connection(ip, port, timeout)

        self._auth = b""
        if password:
            self._auth = struct.pack(f"{max(10, len(password))}s", password.encode())

        self._lock = asyncio.Lock()
        self._keepalive: asyncio.Task | None = None
        self._last_connect: float = 0.0
        self._next_send: float = 0.0

    async def send(self, cmd: Command) -> None:
        """Send command to the device."""
        async with self._lock:
            if self._keepalive:
                self._keepalive.cancel()
                self._keepalive = None

            # Throttle commands to avoid known issues
            ts = time()
            if self._next_send and ts < self._next_send:
                await asyncio.sleep(self._next_send - ts)

            try:
                await self._send(cmd)
            finally:
                self._keepalive = asyncio.create_task(self.disconnect(KEEPALIVE_TTL))

            # Throttle next command. Give ops more time to take effect.
            self._next_send = time() + 0.1 if cmd.is_ref else 1.0

    async def _connect(self) -> None:
        """Connect to device."""
        assert not self._conn.is_connected()

        # Throttle new connections to avoid known issues
        elapsed = time() - self._last_connect
        if elapsed < 0.75:
            await asyncio.sleep(0.75 - elapsed)

        retries = 0
        while retries < 12:
            try:
                _LOGGER.debug("Connecting to %s", self._conn.ip)
                await self._conn.connect()
            except (ConnectionRefusedError, asyncio.TimeoutError):
                retries += 1
                if retries == 5:
                    _LOGGER.warning("Retrying refused connection")
                else:
                    _LOGGER.debug("Retrying refused connection")
                await asyncio.sleep(0.25 * (retries + 1))
                continue
            except ConnectionError as e:
                raise JvcProjectorError from e

            try:
                data = await self._conn.read(len(PJOK))
            except asyncio.TimeoutError as err:
                raise JvcProjectorTimeoutError("Handshake init timeout") from err

            _LOGGER.debug("Handshake received %s", data)

            if data == PJNG:
                _LOGGER.warning("Handshake retrying on busy")
                retries += 1
                await asyncio.sleep(0.2 * retries)
                continue

            if data != PJOK:
                raise JvcProjectorError("Handshake init invalid")

            break
        else:
            raise JvcProjectorTimeoutError(
                f"Failed to connect to {self._conn.ip}; retries exceeded"
            )

        _LOGGER.debug("Handshake sending '%s'", PJREQ.decode())
        await self._conn.write(PJREQ + (b"_" + self._auth if self._auth else b""))

        try:
            data = await self._conn.read(len(PJACK))
            _LOGGER.debug("Handshake received %s", data)

            if data == PJNAK:
                _LOGGER.debug("Standard auth failed, trying SHA256 auth")
                auth = (
                    sha256(f"{self._auth.decode()}{AUTH_SALT}".encode())
                    .hexdigest()
                    .encode()
                )
                await self._conn.write(PJREQ + b"_" + auth)
                data = await self._conn.read(len(PJACK))
                if data == PJACK:
                    self._auth = auth

            if data == PJNAK:
                raise JvcProjectorAuthError

            if data != PJACK:
                raise JvcProjectorError("Handshake ack invalid")

        except asyncio.TimeoutError as err:
            raise JvcProjectorTimeoutError("Handshake ack timeout") from err

        self._last_connect = time()

    async def _send(self, cmd: Command) -> None:
        """Send command to the device."""
        if not self._conn.is_connected():
            await self._connect()

        data = HEAD_REF if cmd.is_ref else HEAD_OP

        code = cmd.code.encode()
        data += code

        if cmd.is_op and cmd.op_value:
            data += cmd.op_value.encode()

        data += END

        _LOGGER.debug(
            "Sending %s '%s (%s)'", "ref" if cmd.is_ref else "op", cmd.code, data
        )

        await self._conn.write(data)

        try:
            data = await self._conn.readline(
                cmd.operation_timeout if cmd.is_op else None
            )
        except asyncio.TimeoutError as e:
            raise JvcProjectorReadWriteTimeoutError(
                f"Read timeout for command {cmd.name} ({cmd.code})"
            ) from e

        if not data.startswith(HEAD_ACK + code[0:2]):
            raise JvcProjectorError(
                f"Invalid ack '{data!r}' for command {cmd.name} ({cmd.code})"
            )

        _LOGGER.debug("Received ack %s", data)

        if cmd.is_ref:
            try:
                data = await self._conn.readline()
            except asyncio.TimeoutError as e:
                raise JvcProjectorReadWriteTimeoutError(
                    f"Read timeout for command {cmd.name} ({cmd.code})"
                ) from e

            _LOGGER.debug("Received ref %s (%s)", data[HEAD_LEN + 2 : -1], data)

            if not data.startswith(HEAD_RES + code[0:2]):
                raise JvcProjectorError(
                    f"Invalid header '{data!r}' for command {cmd.name} ({cmd.code})"
                )

            try:
                cmd.ref_value = data[HEAD_LEN + 2 : -1].decode()
            except UnicodeDecodeError as e:
                cmd.ref_value = data.hex()
                raise JvcProjectorError(
                    f"Invalid response '{data!r} for command {cmd.name} ({cmd.code})'"
                ) from e

        cmd.ack = True

    async def disconnect(self, delay: float = 0.0) -> None:
        """Disconnect from the device."""
        if delay:
            await asyncio.sleep(delay)

        if self._keepalive:
            self._keepalive.cancel()
            self._keepalive = None

        await self._conn.disconnect()

        _LOGGER.debug("Disconnected")
