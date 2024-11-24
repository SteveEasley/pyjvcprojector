"""pytest fixtures."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from jvcprojector import command, const
from jvcprojector.command import JvcCommand
from jvcprojector.device import HEAD_ACK, PJACK, PJOK

from . import IP, MAC, MODEL, PORT, cc, VERSION


@pytest.fixture(name="conn")
def fixture_mock_connection(request):
    """Return a mocked connection."""
    with patch("jvcprojector.device.JvcConnection", autospec=True) as mock:
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
        conn.ip = IP
        conn.port = PORT
        conn.is_connected.side_effect = lambda: connected
        conn.connect.side_effect = connect
        conn.disconnect.side_effect = disconnect
        conn.read.side_effect = [PJOK, PJACK]
        conn.readline.side_effect = [cc(HEAD_ACK, const.CMD_POWER)]
        conn.write.side_effect = lambda p: None

        yield conn


@pytest.fixture(name="dev")
def fixture_mock_device(request):
    """Return a mocked device."""
    with patch("jvcprojector.projector.JvcDevice", autospec=True) as mock:
        fixture = {
            command.TEST: None,
            const.CMD_LAN_SETUP_MAC_ADDRESS: MAC,
            const.CMD_MODEL: MODEL,
            const.CMD_POWER: const.ON,
            const.CMD_INPUT: const.HDMI1,
            const.CMD_SOURCE: const.SIGNAL,
            const.CMD_VERSION: VERSION,
        }

        if hasattr(request, "param"):
            fixture.update(request.param)

        async def send(cmds: list[JvcCommand]):
            for cmd in cmds:
                if cmd.code in fixture:
                    if fixture[cmd.code]:
                        cmd.response = fixture[cmd.code]
                    cmd.ack = True

        dev = mock.return_value
        dev.send.side_effect = send

        yield dev
