import asyncio
import logging
import sys

from jvcprojector import JvcProjector, command

logging.basicConfig(level=logging.WARNING)


async def main():
    jp = JvcProjector(sys.argv[1])
    await jp.connect()

    print("Projector model info:")
    print({
        "model": jp.model,
        "spec": jp.spec,
    })

    if await jp.get(command.Power) == command.Power.STANDBY:
        print("Turning projector on...")
        await jp.set(command.Power, command.Power.ON)
        await asyncio.sleep(1)

    if await jp.get(command.Power) == command.Power.WARMING:
        print("Waiting for projector to warmup...")
        while await jp.get(command.Power) != command.Power.ON:
            await asyncio.sleep(3)
    elif await jp.get(command.Power) == command.Power.COOLING:
        print("Run command after projector has cooled down")
        sys.exit(0)

    # Example of sending remote codes
    print("Showing info on screen")
    await jp.remote(command.Remote.INFO)
    await asyncio.sleep(5)
    print("Hiding info on screen")
    await jp.remote(command.Remote.BACK)

    # Example of reference command
    print("Current projector input:")
    print(await jp.get(command.Input))

    await jp.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
