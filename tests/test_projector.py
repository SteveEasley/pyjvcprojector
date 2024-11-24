"""Tests for projector module."""

from unittest.mock import AsyncMock

import pytest
from unittest.mock import patch

from jvcprojector import const
from jvcprojector.error import JvcProjectorError
from jvcprojector.projector import JvcProjector

from . import HOST, IP, MAC, MODEL, PORT


@pytest.mark.asyncio
async def test_init(dev: AsyncMock):
    """Test init succeeds."""
    p = JvcProjector(IP, port=PORT)
    assert p.host == IP
    assert p.port == PORT
    with pytest.raises(JvcProjectorError):
        assert p.ip
    with pytest.raises(JvcProjectorError):
        assert p.model
    with pytest.raises(JvcProjectorError):
        assert p.mac


@pytest.mark.asyncio
async def test_connect(dev: AsyncMock):
    """Test connect succeeds."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()
    assert p.ip == IP
    await p.disconnect()
    assert dev.disconnect.call_count == 1


@pytest.mark.asyncio
async def test_connect_host(dev: AsyncMock):
    """Test connect succeeds."""
    p = JvcProjector(HOST, port=PORT)
    await p.connect()
    assert p.ip == IP
    await p.disconnect()
    assert dev.disconnect.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("dev", [{const.CMD_MODEL: None}], indirect=True)
async def test_unknown_model(dev: AsyncMock):
    """Test projector with unknown model succeeds."""
    p = JvcProjector(IP)
    await p.connect()
    await p.get_info()
    assert p.mac == MAC
    assert p.model == "(unknown): Unknown"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dev", [{const.CMD_LAN_SETUP_MAC_ADDRESS: None}], indirect=True
)
async def test_unknown_mac(dev: AsyncMock):
    """Test projector with unknown mac uses model succeeds."""
    p = JvcProjector(IP)
    await p.connect()
    with pytest.raises(JvcProjectorError):
        assert p.mac == ""


@pytest.mark.asyncio
async def test_get_info(dev: AsyncMock):
    """Test get_info succeeds."""
    p = JvcProjector(IP)
    await p.connect()
    assert await p.get_info() == {"model": MODEL, "mac": MAC}
    # make sure model code is right
    assert p.model in const.MODEL_MAP.values()


@pytest.mark.asyncio
async def test_get_state(dev: AsyncMock):
    """Test get_state succeeds."""
    p = JvcProjector(IP)
    await p.connect()
    expected_dict = {
        "power": const.ON,
    }
    assert set(expected_dict.items()).issubset((await p.get_state()).items())


def test_version():
    """Test version processing."""
    version = "0300PJ"
    p = JvcProjector(IP)
    assert p.process_version(version) == "3.0.0"


def test_model():
    """Test model processing."""
    model = "B5A1"
    p = JvcProjector(IP)
    assert p.process_model_code(model) == "NZ9"


@pytest.mark.asyncio
async def test_send_command_success(dev: AsyncMock):
    """Test send_command succeeds."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()

    # Mock the _build_command_map method
    p._build_command_map = lambda: {
        const.CMD_PICTURE_MODE_LASER_POWER: {
            "values": {"0": "low", "1": "high", "2": "medium"},
            "inverse": {"low": "0", "high": "1", "medium": "2"},
        }
    }

    # Patch the op method to avoid actual sending
    with patch.object(p, "op") as mock_op:
        await p.send_command(
            const.KEY_LASER_POWER, const.HIGH
        )

        # Assert that op was called once with the correct command
        mock_op.assert_called_once_with(f"{const.CMD_PICTURE_MODE_LASER_POWER}1")

    # We don't need to assert anything about dev.send here, as we're not directly testing it


@pytest.mark.asyncio
async def test_send_command_invalid_value(dev: AsyncMock):
    """Test send_command fails with invalid value."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()

    # Mock the _build_command_map method
    p._build_command_map = lambda: {
        const.CMD_PICTURE_MODE_LASER_POWER: {
            "values": {"0": "low", "1": "high", "2": "medium"},
            "inverse": {"low": "0", "high": "1", "medium": "2"},
        }
    }

    with pytest.raises(
        ValueError,
        match=f"Invalid value for {const.KEY_LASER_POWER}: invalid_value",
    ):
        await p.send_command(const.KEY_LASER_POWER, "invalid_value")


@pytest.mark.asyncio
async def test_send_command_unknown_command(dev: AsyncMock):
    """Test send_command fails with unknown command."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()

    # Mock the _build_command_map method
    p._build_command_map = lambda: {}

    with pytest.raises(ValueError, match="Unknown command: unknown_command"):
        await p.send_command("UNKNOWN_COMMAND", "value")
