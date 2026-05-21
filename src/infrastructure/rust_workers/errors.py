class RustWorkerError(RuntimeError):
    """Base error for Rust worker integration failures."""


class RustWorkerTimeoutError(RustWorkerError):
    """Timeout from Rust workers."""


class RustWorkerValidationError(RustWorkerError):
    """Contract validation failure from Rust workers."""
