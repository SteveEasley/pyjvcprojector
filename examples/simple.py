# type: ignore
"""simple example"""

import asyncio
import logging

from jvcprojector.projector import JvcProjector
from jvcprojector import const

logging.basicConfig(level=logging.WARNING)


async def main():
    jp = JvcProjector("192.168.0.30")
    await jp.connect()

    print("Projector info:")
    print(await jp.get_info())

    if not await jp.is_on():
        await jp.power_on()
        print("Waiting for projector to warmup...")
        while not await jp.is_on():
            await asyncio.sleep(3)

    print("Current state:")
    print(await jp.get_state())

    #
    # Example of sending remote codes
    #
    print("Showing info")
    await jp.remote(const.REMOTE_INFO)
    await asyncio.sleep(5)

    print("Hiding info")
    await jp.remote(const.REMOTE_BACK)

    #
    # Example of reference command (reads value from function)
    #
    print("Picture mode info:")
    print(await jp.ref("PMPM"))

    await jp.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
