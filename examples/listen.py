import asyncio
import logging
from os.path import basename
import sys
from time import time

from jvcprojector import (
    Command,
    JvcProjector,
    JvcProjectorError,
    JvcProjectorTimeoutError,
    command,
)

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class State:
    """Represents the current state of the projector."""

    def __init__(self):
        """Initialize instance of class."""
        self.data: dict[str, str] = {}
        self._preserve = (command.Power.name, command.Signal.name, command.Input.name)

    def __getitem__(self, cmd: type[Command]) -> str | None:
        return self.data.get(cmd.name)

    def __setitem__(self, cmd: type[Command], value):
        self.data[cmd.name] = value

    def update(self, state: "State") -> dict[str, str]:
        """Update current state from new state."""
        changed: dict[str, str] = {}
        for key, val in state.data.items():
            if val is not None:
                self.data[key] = val
                changed[key] = val
        return changed

    def reset(self) -> None:
        """Reset current state."""
        for key in list(self.data.keys()):
            if key not in self._preserve:
                del self.data[key]


async def main():
    jp = JvcProjector(sys.argv[1])
    await jp.connect()

    state = State()
    next_full_sync = 0.0
    retries = 0

    async def update(_cmd: type[Command], _new_state: State) -> str | None:
        """Helper function to return a reference command value."""
        global next_full_sync
        if not jp.supports(_cmd):
            return None
        value = await jp.get(_cmd)
        if value != state[_cmd]:
            _new_state[_cmd] = value
            next_full_sync = 0.0
        return value

    while True:
        try:
            new_state = State()

            power = await update(command.Power, new_state)

            if power == command.Power.ON:
                await update(command.Input, new_state)
                signal = await update(command.Signal, new_state)

                if signal == command.Signal.SIGNAL:
                    hdr = await update(command.Hdr, new_state)
                    await update(command.Source, new_state)
                    await update(command.ColorDepth, new_state)
                    await update(command.ColorSpace, new_state)
                    await update(command.InstallationMode, new_state)

                    if next_full_sync <= time():
                        if hdr and hdr not in (command.Hdr.NONE, command.Hdr.SDR):
                            await update(command.HdrProcessing, new_state)

                        await update(command.PictureMode, new_state)
                        await update(command.ColorProfile, new_state)
                        await update(command.GraphicMode, new_state)
                        await update(command.EShift, new_state)
                        await update(command.Anamorphic, new_state)
                        await update(command.MotionEnhance, new_state)
                        await update(command.LaserPower, new_state)
                        await update(command.LowLatencyMode, new_state)
                        await update(command.LightTime, new_state)

                        next_full_sync = time() + 6
            else:
                if state[command.Signal] != command.Signal.NONE:
                    # Infer signal state
                    new_state[command.Signal] = command.Signal.NONE
                    state.reset()

            if changed := state.update(new_state):
                print(changed)

            retries = 0

            await asyncio.sleep(2)

        except JvcProjectorTimeoutError as e:
            # Timeouts are expected when the projector loses signal and ignores commands.
            retries += 1
            if retries > 1:
                file = basename(__file__)
                line = e.__traceback__.tb_lineno if e.__traceback__ else 0
                _LOGGER.warning(
                    "Retrying listener sync due to: %s (%s:%d)", e, file, line
                )
            await asyncio.sleep(1)

        except JvcProjectorError as e:
            retries += 1
            file = basename(__file__)
            line = e.__traceback__.tb_lineno if e.__traceback__ else 0
            _LOGGER.error("Failed listener sync due to:...%s (%s:%d)", e, file, line)
            await asyncio.sleep(15)


if __name__ == "__main__":
    asyncio.run(main())
