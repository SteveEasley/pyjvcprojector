"""pytest fixtures."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from jvcprojector import command
from jvcprojector.command.base import Command
from jvcprojector.device import HEAD_ACK, PJACK, PJOK

from . import IP, MAC, MODEL, PORT, cc


@pytest.fixture(name="conn")
def fixture_mock_connection(request):
    """Return a mocked connection."""
    with patch("jvcprojector.device.Connection", autospec=True) as mock:
        connected = False

        fixture = {"raise_on_connect": 0}

        if hasattr(request, "param"):
            fixture.update(request.param)

        def connect():
            nonlocal connected
            if fixture["raise_on_connect"] > 0:
                fixture["raise_on_connect"] -= 1
                raise ConnectionRefusedError
            connected = True

        def disconnect():
            nonlocal connected
            connected = False

        conn = mock.return_value
        conn.host = IP
        conn.port = PORT
        conn.is_connected.side_effect = lambda: connected
        conn.connect.side_effect = connect
        conn.disconnect.side_effect = disconnect
        conn.read.side_effect = [PJOK, PJACK]
        conn.readline.side_effect = [cc(HEAD_ACK, command.Power.code)]
        conn.write.side_effect = lambda p: None

        yield conn


@pytest.fixture(name="dev")
def fixture_mock_device(request):
    """Return a mocked device."""
    with patch("jvcprojector.projector.Device", autospec=True) as mock:
        fixture: dict[type[Command], str] = {
            command.MacAddress: MAC,
            command.ModelName: MODEL,
            command.Power: "1",
            command.Input: "6",
            command.Signal: "1",
        }

        if hasattr(request, "param"):
            fixture.update(request.param)

        async def send(cmd: Command):
            if type(cmd) in fixture:
                if cmd.is_ref:
                    cmd.ref_value = fixture[type(cmd)]
                cmd.ack = True

        dev = mock.return_value
        dev.send.side_effect = send

        yield dev


@pytest.fixture(autouse=True)
def reset_commands():
    """Ensure Command subclasses' cached state is reset before each test."""
    Command.unload()
    yield
