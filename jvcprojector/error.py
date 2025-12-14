"""Error classes."""


class JvcProjectorError(Exception):
    """Projector error."""


class JvcProjectorTimeoutError(JvcProjectorError):
    """Projector timeout error."""


class JvcProjectorReadWriteTimeoutError(JvcProjectorTimeoutError):
    """Projector read timeout error."""


class JvcProjectorAuthError(JvcProjectorError):
    """Projector auth error."""
