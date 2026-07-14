"""Custom exceptions for django-easy-icons.

This module defines the custom exception classes used throughout the django-easy-icons
package to provide clear error messages for common failure scenarios.

Exceptions:
    IconNotFoundError: Raised when an icon name cannot be resolved
    InvalidSvgError: Raised when SVG content is malformed or invalid

These exceptions inherit from the standard Python Exception class and can be caught
either specifically or as general exceptions.

Example:
    try:
        icon("missing-icon")
    except IconNotFoundError:
        # Handle missing icon case
        pass
    except InvalidSvgError:
        # Handle malformed SVG case
        pass
"""


class IconNotFoundError(Exception):
    """Raised when an icon name cannot be resolved or underlying asset is missing."""

    pass


class InvalidSvgError(Exception):
    """Raised when SVG content is malformed or missing required elements."""

    pass
