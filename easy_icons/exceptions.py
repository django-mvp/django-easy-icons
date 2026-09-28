"""Exceptions raised by easy_icons."""


class IconNotFoundError(Exception):
    """Raised when an icon name cannot be resolved or underlying asset is missing."""

    pass


class InvalidSvgError(Exception):
    """Raised when SVG content is malformed or missing required elements."""

    pass
