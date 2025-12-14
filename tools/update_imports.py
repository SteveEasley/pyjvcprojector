from __future__ import annotations

from pathlib import Path
import re
import subprocess

import jvcprojector
from jvcprojector.command.base import Command
import jvcprojector.command.command as command_module


def get_class_names() -> list[str]:
    """Return a sorted list of all Command subclass names defined in the command module."""
    names: set[str] = set()

    for cls in Command.registry["name"].values():
        if cls.__module__ == command_module.__name__:
            names.add(cls.__name__)

    return sorted(names)


def main() -> None:
    """Rewrite the import line in the jvcprojector/__init__.py with the sorted Command names."""
    path = Path(command_module.__file__).resolve().with_name("__init__.py")
    text = path.read_text(encoding="utf-8")

    replace = "from .command import " + ", ".join(get_class_names())
    pattern = r"^from \.command import[^)]+\)"
    text = re.sub(pattern, replace, text, flags=re.MULTILINE)

    path.write_text(text, encoding="utf-8")

    subprocess.run(["ruff", "check", "--fix", str(path)], check=False)

    print("Done")

if __name__ == "__main__":
    main()