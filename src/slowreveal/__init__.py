"""Slow reveal video processing toolkit with a simple GUI."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("slowrevealvideo")
except PackageNotFoundError:  # pragma: no cover - during local development
    __version__ = "0.0.0"

__all__ = ["__version__"]
