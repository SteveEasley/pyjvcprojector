import asyncio
import logging
import pytest
import os
from jvcprojector.projector import JvcProjector
from jvcprojector import const

logging.basicConfig(level=logging.WARNING)


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION") != "true", reason="Set RUN_INTEGRATION to true"
)
async def test_connect():
    ip = os.getenv("JVC_IP")
    password = os.getenv("JVC_PASSWORD")
    if not ip or not password:
        print("Set JVC_IP and JVC_PASSWORD environment variables")
        pytest.fail("Set JVC_IP and JVC_PASSWORD environment variables")

    jp = JvcProjector(ip, password=password)
    await jp.connect()

    print("Projector info:")
    print(await jp.get_info())

    if not await jp.is_on():
        await jp.power_on()
        print("Waiting for projector to warmup...")
        while not await jp.is_on():
            await asyncio.sleep(3)

    await jp.send_command(const.KEY_LASER_POWER, const.MEDIUM)
    print("Current state:")
    state = await jp.get_state()
    for key, value in state.items():
        print(f"{key}: {value}")

    await jp.disconnect()
