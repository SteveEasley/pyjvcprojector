"""Functional tests."""

import asyncio
import logging
import os
import pytest
from jvcprojector.projector import JvcProjector
from jvcprojector import const

logging.basicConfig(level=logging.WARNING)
_LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION") != "true", reason="Set RUN_INTEGRATION to true"
)
async def test_connect():
    """Test connect succeeds."""
    ip = os.getenv("JVC_IP")
    password = os.getenv("JVC_PASSWORD")
    if not ip or not password:
        _LOGGER.error("Set JVC_IP and JVC_PASSWORD environment variables")
        pytest.fail("Set JVC_IP and JVC_PASSWORD environment variables")

    jp = JvcProjector(ip, password=password)
    await jp.connect()

    _LOGGER.info("Projector info:")
    _LOGGER.info(await jp.get_info())

    if not await jp.is_on():
        await jp.power_on()
        _LOGGER.info("Waiting for projector to warmup...")
        while not await jp.is_on():
            await asyncio.sleep(3)

    await jp.send_command(const.KEY_LASER_POWER, const.MEDIUM)
    _LOGGER.info("Current state:")
    state = await jp.get_state()
    for key, value in state.items():
        _LOGGER.info("%s: %s", key, value)

    await jp.disconnect()
