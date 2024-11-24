"""Tests for command module."""

from jvcprojector.command import JvcCommandHelpers


def test_build_command():
    """Test build command succeeds."""
    a = JvcCommandHelpers.get_available_commands()
    assert len(a) > 1
