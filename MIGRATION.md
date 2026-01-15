## Version 2.0 Breaking Changes

Version 2.0 introduces significant API changes that are **not backwards compatible** with 1.x versions.
The library has been completely redesigned for better maintainability and extensibility.


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
