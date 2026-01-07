"""Command-line interface for JVC Projector control."""

from __future__ import annotations

import asyncio
import logging
from os.path import basename
import sys
from time import time
from typing import Any

from .command import command
from .command.base import CATEGORIES, Command
from .error import JvcProjectorError, JvcProjectorTimeoutError
from .projector import JvcProjector

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


async def cmd_list(jp: JvcProjector) -> None:
    """List all available commands."""
    commands: dict[str, list[tuple[str, str, str, str]]] = {}

    all_commands = jp.capabilities()

    for category in CATEGORIES + ["Other"]:
        commands[category] = []
        for name, cmd in all_commands.items():
            if cmd["category"] == category:
                reference = "  ✓" if cmd["reference"] else "  ✗"
                operation = "  ✓" if cmd["operation"] else "  ✗"
                commands[category].append(
                    (name, reference, operation, str(cmd["code"]))
                )
        commands[category].sort(key=lambda x: x[0])

    print(f"{'Command':<30} {'Read(ref)':<10} {'Write(op)':<10} {'Code':<4}")
    print("-" * 57)

    for category in CATEGORIES + ["Other"]:
        if not commands[category]:
            continue

        print(f"[{category}]")

        for name, reference, operation, code in commands[category]:
            print(f"{name:<30} {reference:<10} {operation:<10} {code:<4}")

        print()


async def cmd_describe(jp: JvcProjector, name: str) -> None:
    """Show help for a specific command."""
    cmd = jp.describe(name)

    code: str = str(cmd["code"])
    operation: bool = bool(cmd["operation"])
    parameter = cmd["parameter"]

    print(f"Command: {cmd['name']} ({code})")
    print(f"Writable: {'yes' if operation else 'no'}")

    if isinstance(parameter, dict):
        read: dict[str, str] = parameter["read"]
        write: dict[str, str] = parameter["write"]

        readwrite = operation and (write == read)

        print("Read" + ("/Write" if readwrite else "") + " Value:")
        for key, value in sorted(read.items()):
            print(f"  {value:<18} ({key})")

        if operation and not readwrite:
            print("Write Value:")
            for key, value in sorted(write.items()):
                print(f" {value:<18} ({key})")
    else:
        print(f"Value: {parameter}")


async def cmd_get(jp: JvcProjector, name: str) -> None:
    """Get command value from the projector."""
    try:
        print(await jp.get(name))
    except JvcProjectorError as e:
        print(f"Error: {e}")


async def cmd_set(jp: JvcProjector, name: str, value: str) -> None:
    """Set a command value on the projector."""
    if name not in Command.registry["name"]:
        die(f"Error: Unknown command {name}")

    try:
        await jp.set(name, value)
    except JvcProjectorError as e:
        print(f"Error: {e}")
    else:
        print("success")


async def cmd_listen(jp: JvcProjector) -> None:
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


def print_usage() -> None:
    """Print usage information."""
    print(
        "Usage: jvcprojector <-h|--host HOST> [-p|--password PASSWORD] <command> [args...]"
    )
    print()
    print("Commands:")
    print("  list                    List all available commands")
    print("  describe <command>      Describe a command")
    print("  get <command>           Get value of a command")
    print("  set <command> <value>   Set value of a command")
    print("  listen                  Listen for events")
    print()
    print("Options:")
    print("  -h, --host HOST         Projector hostname or IP address")
    print("  -p, --password PASS     Projector password (if required)")
    print("  -m, --model MODEL       Model override (e.g. B8B1)")
    print("  -v, --verbose           Enable verbose logging")


def die(msg: str) -> None:
    """Print error message and exit."""
    print(f"Error: {msg}")
    sys.exit(1)


def parse_args() -> dict[str, Any]:
    """Parse command-line arguments."""
    args = sys.argv[1:]

    if not args:
        print_usage()
        sys.exit(1)

    result: dict[str, Any] = {
        "host": "",
        "password": "",
        "model": "",
        "verbose": False,
        "action": "",
        "args": [],
    }

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ("-h", "--host"):
            if i + 1 >= len(args):
                die(f"Error: {arg} argument is required")
            result["host"] = args[i + 1]
            i += 2
        elif arg in ("-p", "--password"):
            if i + 1 >= len(args):
                die(f"Error: {arg} argument is required")
            result["password"] = args[i + 1]
            i += 2
        elif arg in ("-m", "--model"):
            result["model"] = args[i + 1]
            i += 2
        elif arg in ("-v", "--verbose"):
            result["verbose"] = True
            i += 1
        elif arg.startswith("-"):
            die(f"Error: Unknown option '{arg}'")
            print_usage()
            sys.exit(1)
        elif not result["action"]:
            result["action"] = arg
            i += 1
        else:
            result["args"].append(arg)
            i += 1

    return result


async def main() -> None:
    """CLI entry point."""
    parsed = parse_args()

    logging.basicConfig(level=logging.DEBUG if parsed["verbose"] else logging.WARNING)

    host = parsed["host"]
    password = parsed["password"]
    model = parsed["model"]
    action = parsed["action"]
    args = parsed["args"]

    jp = JvcProjector(host, password=password)

    if host:
        try:
            await jp.connect(**({"model": model} if model else {}))
        except JvcProjectorError as e:
            die(f"Error: {e}")

    print(f"Detected model: {jp.model} ({jp.spec})\n")

    if action == "list":
        await cmd_list(jp)

    elif action == "describe":
        if not args:
            die("Usage: jvcprojector describe <command>")
        await cmd_describe(jp, args[0])

    elif action == "get":
        if not args:
            die("Usage: jvcprojector -h <host> get <command>")
        await cmd_get(jp, args[0])

    elif action == "set":
        if len(args) < 2:
            die("Usage: jvcprojector -h <host> set <command> <value>")
        await cmd_set(jp, args[0], args[1])

    elif action == "listen":
        await cmd_listen(jp)

    else:
        print_usage()
        sys.exit(1)


def cli_entrypoint() -> None:
    """Synchronous entry point for CLI."""
    asyncio.run(main())
