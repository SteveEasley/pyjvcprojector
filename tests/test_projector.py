"""Tests for projector module."""

from unittest.mock import AsyncMock

import pytest

from jvcprojector import command
from jvcprojector.error import JvcProjectorError
from jvcprojector.projector import JvcProjector

from . import HOST, IP, MODEL, PORT

# pylint: disable=unused-argument


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
        assert p.spec


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
    assert p.host == HOST
    assert p.port == PORT
    assert p.model == MODEL
    assert p.spec == "CS20191"
    await p.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("dev", [{command.ModelName: "ABCD"}], indirect=True)
async def test_connect_unknown_model(dev: AsyncMock):
    """Test connect with an unknown model succeeds."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()
    assert p.ip == IP
    assert p.model == "ABCD"
    assert p.spec == ""
    await p.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("dev", [{command.ModelName: "B2A9"}], indirect=True)
async def test_connect_partial_model_match(dev: AsyncMock):
    """Test connect with a partial model match succeeds."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()
    assert p.ip == IP
    assert p.model == "B2A9"
    assert p.spec == "CS20191 (B2A3)"
    await p.disconnect()


@pytest.mark.asyncio
async def test_info(dev: AsyncMock):
    """Test info method."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()
    info = p.info()
    assert info["ip"] == IP
    assert info["model"] == MODEL
    assert info["spec"] == "CS20191"


@pytest.mark.asyncio
async def test_get(dev: AsyncMock):
    """Test get method."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()

    # succeeds
    assert await p.get(command.Power) == command.Power.ON
    assert await p.get("Power") == command.Power.ON
    assert await p.get("PW") == command.Power.ON

    # fails
    with pytest.raises(JvcProjectorError):
        await p.get("BAD")
    with pytest.raises(JvcProjectorError):
        await p.get(command.EShift)


@pytest.mark.asyncio
async def test_set(dev: AsyncMock):
    """Test set method."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()

    # succeeds
    assert await p.set(command.Power, command.Power.ON) is None
    assert await p.set("Power", command.Power.ON) is None
    assert await p.set("PW", command.Power.ON) is None

    # fails
    with pytest.raises(JvcProjectorError):
        await p.set(command.Power, "bad")
    with pytest.raises(JvcProjectorError):
        await p.set("BAD", "")
    with pytest.raises(JvcProjectorError):
        await p.set(command.EShift, command.EShift.ON)


@pytest.mark.asyncio
async def test_supports(dev: AsyncMock):
    """Test support method."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()

    # succeeds
    assert p.supports(command.Power)
    assert p.supports(command.ColorProfile)

    # fails
    assert not p.supports(command.LaserPower)
    with pytest.raises(JvcProjectorError):
        p.supports("BAD")


@pytest.mark.asyncio
async def test_describe(dev: AsyncMock):
    """Test describe method."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()

    # succeeds
    info = p.describe(command.Power)
    assert info["name"] == "Power"
    assert info["code"] == "PW"
    assert info["reference"] is True
    assert info["operation"] is True
    assert info["category"] == "System"
    assert info["parameter"]["read"]["0"] == "standby"
    assert info["parameter"]["read"]["1"] == "on"
    assert info["parameter"]["write"]["0"] == "off"
    assert info["parameter"]["write"]["1"] == "on"

    # fails
    with pytest.raises(JvcProjectorError):
        p.describe(command.LaserPower)
    with pytest.raises(JvcProjectorError):
        p.describe("BAD")


@pytest.mark.asyncio
@pytest.mark.parametrize("dev", [{command.ModelName: "B2A3"}], indirect=True)
async def test_capabilities(dev: AsyncMock):
    """Test describe method."""
    p = JvcProjector(IP, port=PORT)
    await p.connect()

    caps = p.capabilities()
    assert "Power" in caps
    assert "ColorProfile" in caps
    assert "03" in caps["ColorProfile"]["parameter"]["read"]
    assert "01" not in caps["ColorProfile"]["parameter"]["read"]
    assert "LaserPower" not in caps
