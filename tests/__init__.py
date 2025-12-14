"""pytest tests."""

from jvcprojector.device import END

IP = "127.0.0.1"
HOST = "localhost"
PORT = 12345
TIMEOUT = 3.0
MAC = "abcd1234"
MODEL = "B2A2"
PASSWORD = "pass1234"


def cc(hdr: bytes, cmd: str) -> bytes:
    """Create a command."""
    return hdr + cmd.encode() + END
