"""Tests for command module."""

from jvcprojector.command import JvcCommand, JvcCommandHelpers


def test_build_command():
    a = JvcCommandHelpers.get_available_commands()
    assert len(a) > 1
