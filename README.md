# pyjvcprojector

A python library for controlling a JVC Projector over a network connection.

https://pypi.org/project/pyjvcprojector/

Forked from https://github.com/SteveEasley/pyjvcprojector

## Features

A full reference to the available commands is available from JVC here
http://pro.jvc.com/pro/attributes/PRESENT/Manual/External%20Command%20Spec%20for%20D-ILA%20projector_V3.0.pdf.

### Commands
* `JvcCommandHelpers.get_available_commands()` return an object containing all available commands.
* `JvcCommandHelpers.get_command_help("picture_mode")` return human readable help for a given command.

### Convenience functions:
* `JvcProjector::power_on()` turns on power.
* `JvcProjector::power_off()` turns off power.
* `JvcProjector::get_power()` gets power state (_standby, on, cooling, warming, error_)
* `JvcProjector::is_on()` returns True if the power is on and ready
* `JvcProjector::get_input()` get current input (_hdmi1, hdmi2_).
* `JvcProjector::get_signal()` get signal state (_signal, nosignal_).
* `JvcProjector::get_state()` returns {_power, input, signal_}.
* `JvcProjector::get_info()` returns {_model, mac address_}.

### Send supported commands
* `JvcProjector::send_command(cmd, val)` where cmd is a top level key from `JvcCommandHelpers.get_available_commands()` such as `laser_power` and val is a valid option found in the `values` key. For example, `clear_motion_drive, low`.
 
### Send remote control codes
A wrapper for calling `JvcProjector::op(f"RC{code}")`
* `JvcProjector::remote(code)` sends remote control command.

### Send raw command codes
* `JvcProjector::ref(code)` sends reference commands to read data. `code` is formatted `f"{cmd}"`.
* `JvcProjector::op(code)` sends operation commands to write data. `code` is formatted `f"{cmd}{val}"`.

## Installation

```
pip install pyjvcprojector
```

## Usage

```python
import asyncio

from jvcprojector.projector import JvcProjector
from jvcprojector import const


async def main():
    jp = JvcProjector("127.0.0.1")
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
    # Example sending remote code
    #
    print("Showing info window")
    await jp.remote(const.REMOTE_INFO)
    await asyncio.sleep(5)

    print("Hiding info window")
    await jp.remote(const.REMOTE_BACK)

    #
    # Example sending reference command (reads value from function)
    #
    print("Picture mode info:")
    print(await jp.ref("PMPM"))

    #
    # Example sending operation command
    #
    await jp.send_command(const.CMD_PICTURE_MODE_LASER_POWER, const.VAL_LASER_POWER[1])

    await jp.disconnect()
```

Password authentication is also supported for both older and newer models.

```python
JvcProjector("127.0.0.1", password="1234567890")
```