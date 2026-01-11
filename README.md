# pyjvcprojector

A Python client library for controlling JVC Projectors over a network connection.

## Features

- **Async/await support** - Built with asyncio for non-blocking operations
- **Network-based control** - Connects to JVC projectors over TCP
- **Command system** - Get/set projector parameters and send remote control commands
- **Model detection** - Automatically detects projector model and adjusts capabilities
- **Password support** - Optional password authentication
- **Command discovery** - Check supported commands and capabilities
- **CLI tool** - Command-line interface included

## ⚠️ Version 2.0 Breaking Changes

Version 2.0 introduces significant API changes that are **not backwards compatible** with 1.x versions. The library has been completely redesigned for better maintainability and extensibility.

### What Changed

**Old API (1.x):**
```python
jp = JvcProjector("192.168.1.100")
await jp.connect()

# Helper methods
await jp.power_on()
state = await jp.get_power()

# Direct protocol commands
await jp.ref("PMPM")      # Read command
await jp.op("PMPM01")     # Write command

# Constants from separate module
from jvcprojector import const
await jp.remote(const.REMOTE_INFO)
```

**New API (2.0):**
```python
jp = JvcProjector("192.168.1.100")
await jp.connect()

# Unified get/set interface with command classes
from jvcprojector import command

state = await jp.get(command.Power)
await jp.set(command.Power, command.Power.ON)

# Commands are self-documenting with constants
await jp.remote(command.Remote.INFO)
await jp.set(command.PictureMode, command.PictureMode.FILM)

# Discover capabilities
if jp.supports(command.LensMemory):
    await jp.set(command.LensMemory, "1")
```

### Migration Guide

| 1.x | 2.0 |
|-----|-----|
| `await jp.power_on()` | `await jp.set(command.Power, command.Power.ON)` |
| `await jp.power_off()` | `await jp.set(command.Power, command.Power.OFF)` |
| `await jp.get_power()` | `await jp.get(command.Power)` |
| `await jp.get_input()` | `await jp.get(command.Input)` |
| `await jp.get_signal()` | `await jp.get(command.SignalStatus)` |
| `await jp.get_state()` | `jp.info()` (not async) |
| `await jp.ref("PMPM")` | `await jp.get(command.PictureMode)` |
| `await jp.op("PMPM01")` | `await jp.set(command.PictureMode, command.PictureMode.FILM)` |
| `const.REMOTE_INFO` | `command.Remote.INFO` |
| `const.ON` | `command.Power.ON` |

### Why the Change?

- **Type Safety**: Command classes provide better IDE autocomplete and type checking
- **Self-Documenting**: Commands include their own value constants and descriptions
- **Extensibility**: Easy to add new commands and model-specific features
- **Discoverability**: Use `capabilities()`, `supports()`, and `describe()` to explore available commands
- **Consistency**: Single `get`/`set` interface replaces multiple helper methods

## Installation

```bash
pip install pyjvcprojector
```

## Requirements

- Python 3.10 or higher

## Quickstart

```python
import asyncio
from jvcprojector import JvcProjector, command

async def main():
    # Create projector instance
    jp = JvcProjector("{ip}")
    await jp.connect()

    # Get projector info
    print(f"Model: {jp.model}")

    # Get current power state
    power_state = await jp.get(command.Power)
    print(f"Power state: {power_state}")

    # Turn projector on
    if power_state == command.Power.STANDBY:
        await jp.set(command.Power, command.Power.ON)

    # Using the remote method to send remote control commands
    await jp.remote(command.Remote.UP)

    # Or use the more powerful get/set reference/operation method
    current_input = await jp.get(command.Input)
    print(f"Current input: {current_input}")

    # Disconnect
    await jp.disconnect()

asyncio.run(main())
```

## Usage

### Creating a Connection

```python
from jvcprojector import JvcProjector

# Basic connection
jp = JvcProjector("{ip}")

# With custom port and timeout
jp = JvcProjector("{ip}", port=20554, timeout=5.0)

# With password authentication
jp = JvcProjector("{ip}", password="{password}")

# Connect to projector
await jp.connect()
```

### Getting and Setting Parameters

```python
from jvcprojector import command

# Get a parameter value (reference command)
power_state = await jp.get(command.Power)
input_mode = await jp.get(command.Input)
picture_mode = await jp.get(command.PictureMode)

# Set a parameter value (operation command)
await jp.set(command.Power, command.Power.ON)
await jp.set(command.Input, command.Input.HDMI_1)
await jp.set(command.PictureMode, command.PictureMode.CINEMA)
```

### Sending Remote Commands

```python
from jvcprojector import command

# Send remote control button presses
await jp.remote(command.Remote.MENU)
await jp.remote(command.Remote.UP)
await jp.remote(command.Remote.OK)
await jp.remote(command.Remote.BACK)
```

### Discovering Capabilities

```python
# Check if a command is supported
import command

if jp.supports(command.InstallationMode):
    await jp.set(command.LensMemory, "memory-1")

# Get description of a command
description = jp.describe(command.Power)
print(description)

# Get all supported commands
capabilities = jp.capabilities()
for cmd_name, cmd_info in capabilities.items():
    print(f"{cmd_name}: {cmd_info}")

# Get projector information
info = jp.info()
print(info)  # {'ip': '192.168.1.100', 'model': 'NZ8', 'spec': '...'}
```

## API Reference

### JvcProjector

**Constructor:**
```python
JvcProjector(host, port=20554, timeout=2.0, password=None)
```

**Methods:**
- `await connect(model=None)` - Initialize connection to the projector
- `await disconnect()` - Close connection to the projector
- `await get(command)` - Get a projector parameter value (reference command)
- `await set(command, value)` - Set a projector parameter value (operation command)
- `await remote(value)` - Send a remote control command
- `capabilities()` - Get all supported commands for current projector model
- `supports(command)` - Check if a command is supported by the projector model
- `describe(command)` - Get description of a command
- `info()` - Get projector information (IP, model, spec)

**Properties:**
- `host` - Hostname or IP address
- `port` - TCP port (default: 20554)
- `ip` - Resolved IP address (available after connect)
- `model` - Projector model name (available after connect)
- `spec` - Projector specification (available after connect)

## Command-Line Interface

The library includes a CLI tool:

```bash
% jvcprojector --help

Usage: jvcprojector <-h|--host HOST> [-p|--password PASSWORD] <command> [args...]

Commands:
  list                    List all available commands
  describe <command>      Describe a command
  get <command>           Get value of a command
  set <command> <value>   Set value of a command
  listen                  Listen for events  

Options:
  -h, --host HOST         Projector hostname or IP address
  -p, --password PASS     Projector password (if required)
  -m, --model MODEL       Model override (e.g. B8B1)
  -v, --verbose           Enable verbose logging
```

## Development

```bash
# Clone the repository
git clone https://github.com/SteveEasley/pyjvcprojector.git
cd pyjvcprojector

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy jvcprojector

# Run linting
ruff check .
```

### Adding New Commands

The library uses a command system defined in `jvcprojector/command/command.py`. This file contains:

1. **Specifications and Models** - Defines which projector models support which command sets
2. **Command Classes** - Individual command implementations (55+ commands including Power, Input, PictureMode, etc.)

#### Command Structure

Each command class inherits from `Command` and defines:

```python
class Power(Command):
    """Power command."""

    code = "PW"                    # JVC protocol command code
    reference = True               # Supports reading (get)
    operation = True               # Supports writing (set)
    limp_mode = True               # Available in limp mode (unknown models)

    # Constants for command values
    OFF = "off"
    ON = "on"
    STANDBY = "standby"
    COOLING = "cooling"
    WARMING = "warming"

    # Parameter mapping between JVC codes and human-readable values
    parameter = MapParameter(
        size=1,
        read={"0": STANDBY, "1": ON, "2": COOLING, "3": WARMING},
        write={"0": OFF, "1": ON},
    )
```

#### Model-Specific Commands

Some commands are only available on certain models. Use conditional parameters:

```python
class SomeCommand(Command):
    code = "XX"
    reference = True
    operation = True

    # Different parameters for different specifications
    parameter = {
        CS20241: MapParameter(size=1, readwrite={"0": "value1", "1": "value2"}),
        (CS20221, CS20191): MapParameter(size=1, readwrite={"0": "value1"}),
    }
```

#### Parameter Types

- **`MapParameter`** - Maps JVC protocol values to human-readable strings
  - `size` - Expected response size in characters
  - `read` - Mapping for reference (get) operations
  - `write` - Mapping for operation (set) operations
  - `readwrite` - Shorthand when read/write mappings are identical

- **`ModelParameter`** - Parses model names
- **`MacAddressParameter`** - Formats MAC addresses
- **`VersionParameter`** - Handles version strings
- **`LaserPowerParameter`** - Converts laser power (hex to percentage)
- **`LightTimeParameter`** - Converts light source time (hex to hours)

#### Specifications

The `SPECIFICATIONS` tuple at the top of `command.py` defines model families and their command support:

```python
SPECIFICATIONS = (
    CS20241 := Spec(
        "CS20241",
        B8A2 := Model("B8A2"),  # RS3200, NZ800, etc.
        B8A1 := Model("B8A1"),  # RS4200, NZ900, etc.
    ),
    # ... more specs
)
```

Models are matched in order:
1. Exact model name match
2. Prefix match (first 3 characters)
3. Falls back to "limp mode" with minimal command support

#### Adding a New Command

1. Define the command class in `command.py`
2. Set the JVC protocol `code`
3. Mark as `reference` and/or `operation`
4. Define the `parameter` (use `MapParameter` for most cases)
5. Add human-readable constants for common values
6. Optionally specify model-specific support using spec keys
7. Run `python tools/update_imports.py` to update imports

The command automatically registers itself and becomes available via `command.YourCommandName`.

## License

This project is licensed under the terms specified in the `LICENSE` file included in this repository.