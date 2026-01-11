"""Tests for device module."""

from hashlib import sha256
from unittest.mock import AsyncMock, call

import pytest

from jvcprojector import command
from jvcprojector.command.command import CS20191
from jvcprojector.device import (
    AUTH_SALT,
    HEAD_ACK,
    HEAD_OP,
    HEAD_REF,
    HEAD_RES,
    PJACK,
    PJNAK,
    PJNG,
    PJOK,
    PJREQ,
    Device,
)
from jvcprojector.error import JvcProjectorError

from . import IP, PORT, TIMEOUT, cc


@pytest.mark.asyncio
async def test_send_ref(conn: AsyncMock):
    """Test send reference command succeeds."""
    conn.readline.side_effect = [
        cc(HEAD_ACK, command.Power.code),
        cc(HEAD_RES, command.Power.code + "1"),
    ]
    dev = Device(IP, PORT, TIMEOUT, None)
    cmd = command.Power(CS20191)
    await dev.send(cmd)
    await dev.disconnect()
    assert cmd.ack
    assert cmd.ref_value == command.Power.ON
    conn.connect.assert_called_once()
    conn.write.assert_has_calls([call(PJREQ), call(cc(HEAD_REF, command.Power.code))])


@pytest.mark.asyncio
async def test_send_op(conn: AsyncMock):
    """Test send operation command succeeds."""
    dev = Device(IP, PORT, TIMEOUT, None)
    cmd = command.Power(CS20191)
    cmd.op_value = command.Power.ON
    await dev.send(cmd)
    await dev.disconnect()
    assert cmd.ack
    assert cmd.ref_value is None
    conn.connect.assert_called_once()
    conn.write.assert_has_calls(
        [call(PJREQ), call(cc(HEAD_OP, f"{command.Power.code}1"))]
    )


@pytest.mark.asyncio
async def test_send_with_password(conn: AsyncMock):
    """Test send with 10 character password succeeds."""
    dev = Device(IP, PORT, TIMEOUT, "passwd7890")
    cmd = command.Power(CS20191)
    cmd.op_value = command.Power.ON
    await dev.send(cmd)
    await dev.disconnect()
    conn.write.assert_has_calls(
        [
            call(PJREQ + b"_passwd7890\x00\x00\x00\x00\x00\x00"),
            call(cc(HEAD_OP, f"{command.Power.code}1")),
        ]
    )


@pytest.mark.asyncio
async def test_send_with_password_sha256(conn: AsyncMock):
    """Test send with a projector requiring sha256 hashing."""
    conn.read.side_effect = [PJOK, PJNAK, PJACK]
    dev = Device(IP, PORT, TIMEOUT, "passwd78901")
    cmd = command.Power(CS20191)
    cmd.op_value = command.Power.ON
    await dev.send(cmd)
    await dev.disconnect()
    auth = sha256(f"passwd78901{AUTH_SALT}".encode()).hexdigest().encode()
    conn.write.assert_has_calls(
        [call(PJREQ + b"_" + auth), call(cc(HEAD_OP, f"{command.Power.code}1"))]
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("conn", [{"raise_on_connect": 1}], indirect=True)
async def test_connection_refused_retry(conn: AsyncMock):
    """Test connection refused results in retry."""
    dev = Device(IP, PORT, TIMEOUT, None)
    cmd = command.Power(CS20191)
    cmd.op_value = command.Power.ON
    await dev.send(cmd)
    await dev.disconnect()
    assert cmd.ack
    assert conn.connect.call_count == 2
    conn.write.assert_has_calls(
        [call(PJREQ), call(cc(HEAD_OP, f"{command.Power.code}1"))]
    )


@pytest.mark.asyncio
async def test_connection_busy_retry(conn: AsyncMock):
    """Test handshake busy results in retry."""
    conn.read.side_effect = [PJNG, PJOK, PJACK]
    dev = Device(IP, PORT, TIMEOUT, None)
    cmd = command.Power(CS20191)
    cmd.op_value = command.Power.ON
    await dev.send(cmd)
    await dev.disconnect()
    assert conn.connect.call_count == 2
    conn.write.assert_has_calls(
        [call(PJREQ), call(cc(HEAD_OP, f"{command.Power.code}1"))]
    )


@pytest.mark.asyncio
async def test_connection_bad_handshake_error(conn: AsyncMock):
    """Test bad handshake results in error."""
    conn.read.side_effect = [b"BAD"]
    dev = Device(IP, PORT, TIMEOUT, None)
    cmd = command.Power(CS20191)
    cmd.op_value = command.Power.ON
    with pytest.raises(JvcProjectorError):
        await dev.send(cmd)
    conn.connect.assert_called_once()
    assert not cmd.ack


@pytest.mark.asyncio
async def test_send_op_bad_ack_error(conn: AsyncMock):
    """Test send operation with bad ack results in error."""
    conn.readline.side_effect = [cc(HEAD_ACK, "ZZ")]
    dev = Device(IP, PORT, TIMEOUT, None)
    cmd = command.Power(CS20191)
    cmd.op_value = command.Power.ON
    with pytest.raises(JvcProjectorError):
        await dev.send(cmd)
    conn.connect.assert_called_once()
    assert not cmd.ack


@pytest.mark.asyncio
async def test_send_ref_bad_ack_error(conn: AsyncMock):
    """Test send reference with bad ack results in error."""
    conn.readline.side_effect = [cc(HEAD_ACK, command.Power.code), cc(HEAD_RES, "ZZ1")]
    dev = Device(IP, PORT, TIMEOUT, None)
    cmd = command.Power(CS20191)
    with pytest.raises(JvcProjectorError):
        await dev.send(cmd)
    conn.connect.assert_called_once()
    assert not cmd.ack
